__author__ = 'Victor Varvariuc<victor.varvariuc@gmail.com>'

import os
import sys
import time
import re
import shlex

import dbus
import apt
from distutils import dir_util, file_util
from PyQt4 import QtGui, QtCore
from PyKDE4.kdecore import KConfig
from PyKDE4.kdeui import KGlobalSettings
import pexpect

from .xml_tree_merge import XmlTreeMerger


class ActionMeta(type):
    """Action metaclass to make Action subclasses sortable.
    """
    def __new__(mcs, name, bases, attrs):
        action = type.__new__(mcs, name, bases, attrs)

        action.action_dir = os.path.dirname(sys.modules[action.__module__].__file__)

        def make_abs_path(match):
            img_abs_path = action.make_abs_path(match.group(1))
            if not os.path.exists(img_abs_path):
                print('Description image file does not exist: %s' % img_abs_path)
            return '<img src="%s"/>' % img_abs_path

        # convert relative paths of img tags to absolute
        action.description = re.sub(r'<\s*img\s+src\s*=\s*"([^"]+)"\s*/>', make_abs_path,
                                    action.description)

        return action


class BaseAction(metaclass=ActionMeta):
    """Base class for user actions.
    """
    name = ''
    author = ''
    # http://doc.qt.digia.com/qt/richtext-html-subset.html
    description = "HTML description of the action"
    # {repo_name: (repo_url, public_key_url)} repositories for installing packages
    repositories = {}
    # list of package names to install
    packages = []
    affects = []
    action_dir = ''  # directory of the action class to compute absolute paths in description

    def __init__(self, main_window):
        from .main import MainWindow
        assert isinstance(main_window, MainWindow)
        self.main_window = main_window

    def __str__(self):
        return '%s.%s' % (self.__class__.__module__, self.__class__.__name__)

    def print_text(self, message, end='\n'):
        self.main_window.print_text(message, end=end)

    def print_html(self, message, end='<br>'):
        self.main_window.print_html(message, end=end)

    def install_repositories(self, repositories):
        assert isinstance(repositories, dict)

        commands = []
        # check if file exists
        for repo_name, (repo_url, public_key_url) in repositories.items():
            assert isinstance(repo_name, str)
            assert isinstance(public_key_url, str)
            assert isinstance(repo_url, str)
            if repo_name.startswith('ppa:'):
                commands.append('add-apt-repository --yes %s' % repo_name)
                continue
            assert re.match(  # man sources.list
                r'[a-zA-Z0-9_\-\.]+\.list', repo_name), 'Invalid repo name: %r' % repo_name
            repo_path = os.path.join('/etc/apt/sources.list.d/', repo_name)
            if os.path.isfile(repo_path):
                with open(repo_path) as repo_file:
                    if repo_url in repo_file.read().splitlines():
                        # URL is already there, do not add this repo
                        continue
                # install public key
            commands.append('wget --quiet --output-document=- %s | sudo apt-key add -'
                            % public_key_url)
            # add repo to the list of repos
            commands.append('echo "%s" >> %s' % (repo_url, repo_path))

        if not commands:
            self.print_html('<b style="color:green">All required repositories are already '
                            'installed</b>')
            return True

        self.print_html('<b style="color:#B08000">Installing additional repositories:</b>')

        command = '\n'.join(commands)
        #        self.open_konsole(command)
        retcode = self.kdesudo(command, 'Install additional repositories')
        if retcode:
            self.print_html('<b style="color:red">An error happened during installation of '
                            'repositories.</b>')
            QtGui.QMessageBox.critical(self.main_window, 'Error',
                                       'An error occured during apt-get install')
            return False

        self.print_html('<b style="color:green">The repositories were sucessfully '
                        'installed.</b>')
        return True

    def install_packages(self, package_names):
        """apt-get install packages, which are not yet installed

        Args:
            package_names (list): names of the packages to install
        """
        assert isinstance(package_names, (list, tuple))
        if not package_names:
            self.print_html('<b style="color:green">No packages required to install.</b>')
            return True

        packages = {package_name: None for package_name in package_names}

        apt_cache = apt.Cache()
        apt_cache.open()
        for package_name in list(packages.keys()):
            try:
                apt_package = apt_cache[package_name]
            except KeyError:  # package not found
                apt_package = None
            if apt_package is None or apt_package.is_installed:
                packages.pop(package_name)
            else:
                packages[package_name] = apt_package.candidate.summary

        if not packages:
            self.print_html('<b style="color:green">All required packages are already '
                            'installed</b>')
            return True

        self.print_html('<b style="color:#B08000">Updating package index:</b>')
        retcode = self.kdesudo('apt-get update', 'Updating package index')
        if retcode:
            self.print_html('<b style="color:red">An error happened while updating package '
                            'index .</b>')
            return False

        self.print_html('<b style="color:green">The package index was sucessfully '
                        'updated.</b>')

        message = 'These additional packages must be installed:<ul>'
        for package_name, package_summary in sorted(packages.items()):
            message += '<li><b>%s</b>: %s</li>' % (package_name, package_summary)
        message += '</ul>'
        res = QtGui.QMessageBox.question(
            self.main_window, 'Required packages', message,
            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Ok)
        if res != QtGui.QMessageBox.Ok:
            return False

        self.print_html('<b style="color:#B08000">Installing additional packages:</b>')
        retcode = self.kdesudo('apt-get --assume-yes install %s' % ' '.join(packages),
                               'Install required packages')
        if retcode:
            self.print_html('<b style="color:red">An error happened during packages '
                            'installation.</b>')
            QtGui.QMessageBox.critical(self.main_window, 'Error',
                                       'An error occured during apt-get install')
            return False

        self.print_html('<b style="color:green">The packages were successfully installed.</b>')
        return True

    def kdesudo(self, command, comment):
        retcode, msg = self.call(['kdesudo', '--comment', comment, '-c', command])
        return retcode

    def run_konsole(self, text):
        """Open a Konsole and type text in it.
        """
        bus = dbus.SessionBus()
        konsole = bus.get_object('org.kde.konsole', '/Konsole')
        session_id = dbus.Interface(konsole, 'org.kde.konsole.Window').newSession()
        session = bus.get_object('org.kde.konsole', '/Sessions/%s' % session_id)
        session.sendText(text)

    @classmethod
    def make_abs_path(cls, file_path):
        file_path = os.path.expanduser(file_path)
        if os.path.isabs(file_path):
            return os.path.normpath(file_path)
        file_path = os.path.join(cls.action_dir, file_path)
        file_path = os.path.abspath(file_path)
        return file_path

    def update_kconfig(self, source_config_path, dest_config_path):
        """Update a configuration file which is in format of kconfig.

        Args:
            source_config_path (str): relative path to the source configuration file
            dest_config_path (str): path to the file to apply patch to
        """
        assert isinstance(source_config_path, str)
        assert isinstance(dest_config_path, str)
        assert not os.path.isabs(source_config_path), 'The source should be relative'
        source_config_path = self.make_abs_path(source_config_path)
        assert os.path.isfile(source_config_path)
        dest_config_path = self.make_abs_path(dest_config_path)
        self.print_html('Updating configuration in <code>%s</code> from <code>%s</code>.'
                        % (dest_config_path, source_config_path))

        # http://api.kde.org/4.x-api/kdelibs-apidocs/kdeui/html/classKGlobalSettings.html
        # http://api.kde.org/4.x-api/kdelibs-apidocs/kdecore/html/classKConfig.html
        # http://api.kde.org/4.x-api/kdelibs-apidocs/kdecore/html/classKConfigGroup.html
        # https://projects.kde.org/projects/kde/kdebase/kde-runtime/repository/show/kreadconfig
        def update_group(src_group, dst_group, bkp_group):
            for entry_name, new_entry_value in src_group.entryMap().items():
                if hasattr(dst_group, 'writeEntry'):
                    old_entry_value = dst_group.readEntry(entry_name)
                    dst_group.writeEntry(entry_name, new_entry_value)
                    if new_entry_value != old_entry_value and old_entry_value:
                        bkp_group.writeEntry(entry_name, old_entry_value)
            for group_name in src_group.groupList():
                update_group(src_group.group(group_name), dst_group.group(group_name),
                             bkp_group.group(group_name))

        src_cfg = KConfig(source_config_path, KConfig.SimpleConfig)
        dst_cfg = KConfig(dest_config_path, KConfig.SimpleConfig)
        bkp_cfg = KConfig('', KConfig.SimpleConfig)  # we keep here original settings of dest

        update_group(src_cfg, dst_cfg, bkp_cfg)
        # update top level entries
        update_group(src_cfg.group(''), dst_cfg.group(''), bkp_cfg)

        dst_cfg.sync()  # save the current state of the configuration object

    #        if bkpCfgPath:
    #            bkp_cfg.sync()

    def update_xmlconfig(self, source_config_path, dest_config_path, default_config_path=''):
        """Update an XML configuration file

        Args:
            source_config_path (str): relative path to the source configuration file
            dest_config_path (str): path to the file to apply patch to
        """
        assert isinstance(source_config_path, str)
        assert isinstance(dest_config_path, str)
        assert not os.path.isabs(source_config_path), 'The source should be relative'
        source_config_path = self.make_abs_path(source_config_path)
        assert os.path.isfile(source_config_path)
        dest_config_path = self.make_abs_path(dest_config_path)
        self.print_html('Updating configuration in <code>%s</code> from <code>%s</code>.'
                        % (dest_config_path, source_config_path))

        if not os.path.exists(dest_config_path):
            assert default_config_path, 'Default configuration path must be specified'
            assert os.path.basename(dest_config_path) == os.path.basename(default_config_path)
            self.copy_file(default_config_path, os.path.dirname(dest_config_path))

        merger = XmlTreeMerger(dest_config_path, source_config_path)
        new_xml = merger.merge()
        dest_dir_path = os.path.dirname(dest_config_path)
        if not os.path.exists(dest_dir_path):
            self.create_directory(dest_dir_path)
        with open(dest_config_path, 'w', encoding='utf-8') as file:
            file.write(new_xml)

    def create_directory(self, dir_path):
        dir_util.mkpath(dir_path)

    def copy_file(self, src_path, dst_dir_path):
        """Copy a single file/directory to another directory.

        Args:
            src_path (str): path of the file/directory to copy
            dst_dir_path (str): path of the destination directory
        Returns:
            str: path of the copied file
        """
        src_path = self.make_abs_path(src_path)
        dst_dir_path = self.make_abs_path(dst_dir_path)
        self.print_html('Copying file <code>%s</code> to <code>%s</code>.'
                        % (src_path, dst_dir_path))
        if not os.path.exists(src_path):
            raise ValueError('Source path does not exist: %s' % src_path)
        file_name = os.path.split(src_path)[1]
        dst_path = os.path.join(dst_dir_path, file_name)
        if os.path.isdir(src_path):
            dir_util.copy_tree(src_path, dst_path)
        else:
            self.create_directory(dst_dir_path)
            file_util.copy_file(src_path, dst_path)

        return dst_path

    def create_symlink(self, src_path, dst_path):
        """Create a symlink.

        Args:
            src_path (str): path of the file/directory to which the created symlink will point
            dst_path (str): path of the symbolic link to create
        """
        src_path = self.make_abs_path(src_path)
        dst_path = self.make_abs_path(dst_path)
        self.print_html('Creating symbolic link <code>%s</code> to <code>%s</code>.'
                        % (dst_path, src_path))
        if not os.path.exists(src_path):
            raise ValueError('Source path does not exist: %s' % src_path)
        if os.path.exists(dst_path):
            self.delete_file(dst_path)
        os.symlink(src_path, dst_path)

    def delete_file(self, file_path):
        """Delete a file.
        """
        if not os.path.exists(file_path):
            return
        self.print_html('Deleting file <code>%s</code>.' % file_path)
        if os.path.isdir(file_path):
            dir_util.remove_tree(file_path)
        else:
            os.remove(file_path)

    def call(self, command, message=''):
        """Run a [terminal] command.

        Args:
            command (str, callable): a command to run via subprocess or a callable to call passing
                it main_window as an argument
            message (str): additional text to print before executing the command
        """
        if not command:
            return

        if message:
            self.print_text(message)

        if callable(command):
            return command(self.main_window)

        if isinstance(command, str):
            command = shlex.split(command)
        else:
            assert isinstance(command, (tuple, list))
        self.print_html('<code style="background-color:#CCC">%s</code>'
                        % " ".join(map(shlex.quote, command)))

        process = pexpect.spawn(command[0], command[1:])

        output = []
        while process.isalive():
            try:
                process.expect([process.crlf, pexpect.EOF], timeout=0.1)
            except pexpect.TIMEOUT:
                QtGui.QApplication.processEvents()
                continue
            line = process.before.decode('utf-8')
            if not line:
                break
            output.append(line)
            self.print_text(line)

        retcode = process.exitstatus
        return retcode, output

    def proceed(self):
        """To be reimplemented in subclasses.
        """


class ActionPackage:
    """Action package properties: desription, author, etc.
    """
    author = ''
    version = 0
    description = ''  # html description


class App:
    """Base class for KDE apps.
    """
    name = ''  # descriptive name of the app
    stop = ''  # command to stop the app
    start = ''  # command to start the app


class Plasma(App):

    name = 'Plasma'
    stop = 'kquitapp plasma-desktop'
    start = 'kstart plasma-desktop'

    @staticmethod
    def reload_config(action):
        action.print_text('Asking plasma to reload its config')
        plasma = dbus.SessionBus().get_object('org.kde.plasma-desktop', '/MainApplication')
        dbus.Interface(plasma, 'org.kde.KApplication').reparseConfiguration()


class Kwin(App):

    name = 'Kwin'
    stop = 'kquitapp kwin'
    start = 'kstart kwin'

    @staticmethod
    def reload_config(action):
        action.print_text('Asking Kwin to reload its config')
        kwin = dbus.SessionBus().get_object('org.kde.kwin', '/MainApplication')
        dbus.Interface(kwin, 'org.kde.KApplication').reparseConfiguration()


class KGlobalAccel(App):

    name = 'Global shortcuts manager'
    stop = 'kquitapp kglobalaccel'
    start = 'kstart kglobalaccel'

    @staticmethod
    def reload_config(action):
        action.print_text('Asking global shortcuts manager to reload its config')
        dbus.Interface(dbus.SessionBus().get_object('org.kde.kglobalaccel', '/MainApplication'),
                       'org.kde.KApplication').reparseConfiguration()


class KdeSettings(App):

    name = 'KDE settings'

    @staticmethod
    def start(main_window):
        # https://projects.kde.org/projects/kde/kde-workspace/repository/revisions/master/entry/kcontrol/style/kcmstyle.cpp
        kGlobalSettings = KGlobalSettings.self()
        main_window.print_html(
            '<b style="color:green">Notifying all KDE applications about the '
            'global settings change.</b>')
        kGlobalSettings.emitChange(KGlobalSettings.StyleChanged)
        kGlobalSettings.emitChange(KGlobalSettings.SettingsChanged)
        kGlobalSettings.emitChange(KGlobalSettings.ToolbarStyleChanged)
        kGlobalSettings.emitChange(KGlobalSettings.PaletteChanged)
        kGlobalSettings.emitChange(KGlobalSettings.FontChanged)
        kGlobalSettings.emitChange(KGlobalSettings.IconChanged)
        kGlobalSettings.emitChange(KGlobalSettings.CursorChanged)


class KHotKeys(App):

    @staticmethod
    def reload_config(action):
        action.print_text('Asking khotkeys to reload its config')
        kwin = dbus.SessionBus().get_object('org.kde.kded', '/modules/khotkeys')
        dbus.Interface(kwin, 'org.kde.khotkeys').reread_configuration()


def run_action_set(main_window, action_classes):

        actions = []
        packages = []  # packages to install
        repositories = {}  # repositories to add

        for action_class in action_classes:
            actions.append(action_class(main_window))
            packages.extend(action_class.packages)
            repositories.update(action_class.repositories)

        # add new repositories
        res = actions[0].install_repositories(repositories)
        if not res:
            main_window.print_html(
                '<b style="color:red">Not all repositories installed. Not proceeding further.</b>')
            return

        # install missing packages
        res = actions[0].install_packages(packages)
        if not res:
            main_window.print_html(
                '<b style="color:red">Not all packages installed. Not proceeding further.</b>')
            return

        affected_apps = set()
        for action in actions:
            affected_apps.update(action.affects)

        for app in affected_apps:
            actions[0].call(app.stop, 'Stopping %s' % app.name)
        time.sleep(2)  # give time for the apps to shut down

        # perform the actions
        for action in actions:
            main_window.print_html('Performing action <b>"%s"</b>' % action.name)
            try:
                action.proceed()
            except Exception as exc:
                main_window.print_html('<span style="color:red"><b>Error:</b> %s</span>' % exc)
            else:
                main_window.print_html(
                    'Finished action <b style="color:green">"%s"</b>' % action.name)

        for app in affected_apps:
            actions[0].call(app.start, 'Starting %s' % app.name)

        main_window.print_html(
            '<b style="background-color:green;color:white">Finished package installation.<br>'
            'Some effects could be seen only when you restart your KDE session.</b>')
