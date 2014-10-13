__author__ = 'Victor Varvariuc<victor.varvariuc@gmail.com>'

import subprocess
import os
import sys
import time
import re
import traceback
import functools
import shlex

import dbus
import apt
from distutils import dir_util, file_util
from PyQt4 import QtGui, QtCore
from PyKDE4.kdecore import KConfig
from PyKDE4.kdeui import KGlobalSettings
import pexpect

from . import signals
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

    # the following methods are needed to be able to sort Action subclasses
    def __lt__(self, other):
        return id(self) < id(other)

    def __eq__(self, other):
        return id(self) == id(other)


def defer_to_end(method):

    @functools.wraps(method)
    def wrapper(self, immediately=False):

        if immediately:
            return method(self)

        def call_method(**kwargs):
            try:
                method(self)
            finally:
                signals.action_set_proceeded.disconnect(dispatch_uid=method)

        signals.action_set_proceeded.connect(call_method, dispatch_uid=method, weak=False)

    return wrapper


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
    action_dir = ''  # directory of the action class to compute absolute paths in description

    def __init__(self, main_window):
        assert isinstance(main_window, QtGui.QMainWindow)
        self.main_window = main_window

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
            self.print_text('No packages required to install.')
            return True

        self.print_html('<b style="color:#B08000">Updating package index:</b>')
        retcode = self.kdesudo('apt-get update', 'Updating package index')
        if retcode:
            self.print_html('<b style="color:red">An error happened while updating package '
                            'index .</b>')
            return False

        self.print_html('<b style="color:green">The package index was sucessfully '
                        'updated.</b>')

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

    def open_konsole(self, text):
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

    def call(self, args):
        """Run a program.
        """
        if isinstance(args, str):
            args = shlex.split(args)
        else:
            assert isinstance(args, (tuple, list))
        self.print_html('<code style="background-color:#CCC">%s</code>' % args)

        process = pexpect.spawn(args[0], args[1:])

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

    @defer_to_end
    def request_kde_reload_config(self):
        # https://projects.kde.org/projects/kde/kde-workspace/repository/revisions/master/entry/kcontrol/style/kcmstyle.cpp
        kGlobalSettings = KGlobalSettings.self()
        self.print_html('<b style="color:green">Notifying all KDE applications about the '
                        'global settings change.</b>')
        kGlobalSettings.emitChange(KGlobalSettings.StyleChanged)
        kGlobalSettings.emitChange(KGlobalSettings.SettingsChanged)
        kGlobalSettings.emitChange(KGlobalSettings.ToolbarStyleChanged)
        kGlobalSettings.emitChange(KGlobalSettings.PaletteChanged)
        kGlobalSettings.emitChange(KGlobalSettings.FontChanged)
        kGlobalSettings.emitChange(KGlobalSettings.IconChanged)
        kGlobalSettings.emitChange(KGlobalSettings.CursorChanged)

    @defer_to_end
    def request_plasma_reload_config(self):
        self.print_text('Asking plasma to reload its config')
        plasma = dbus.SessionBus().get_object('org.kde.plasma-desktop', '/MainApplication')
        dbus.Interface(plasma, 'org.kde.KApplication').reparseConfiguration()

    def _call(self, command, message, signal=None):
        self.print_text(message)
        try:
            with open(os.devnull, 'wb') as dev_null:
                subprocess.call(command, shell=True, stdout=dev_null, stderr=dev_null)
            if signal:
                signal.send(None)
        except Exception:
            self.print_text(traceback.format_exc())

    @defer_to_end
    def restart_plasma(self):
        self._call('kquitapp plasma-desktop', 'Stopping Plasma', signals.plasma_stopped)
        time.sleep(2)  # give time to stop completely
        self._call('kstart plasma-desktop', 'Starting Plasma', signals.plasma_started)

    @defer_to_end
    def restart_kwin(self):
        self._call('kquitapp kwin', 'Stopping Kwin', signals.kwin_stopped)
        time.sleep(2)  # give time to stop completely
        self._call('kwin &', 'Starting Kwin', signals.kwin_started)

    @defer_to_end
    def request_kwin_reload_config(self):
        self.print_text('Asking Kwin to reload its config')
        kwin = dbus.SessionBus().get_object('org.kde.kwin', '/MainApplication')
        dbus.Interface(kwin, 'org.kde.KApplication').reparseConfiguration()

    @defer_to_end
    def request_global_accel_reload_config(self):
        self.print_text('Asking global shortcuts manager to reload its config')
        dbus.Interface(dbus.SessionBus().get_object('org.kde.kglobalaccel', '/MainApplication'),
                       'org.kde.KApplication').reparseConfiguration()

    @defer_to_end
    def restart_kglobalaccel(self):
        self._call('kquitapp kglobalaccel', 'Stopping global shortcuts manager')
        time.sleep(2)  # give time to stop completely
        self._call('kglobalaccel &', 'Starting global shortcuts manager')

    # @defer_to_end
    # def khotkeys_reload_config(self):
    #     self.print_text('Asking khotkeys to reload its config')
    #     kwin = dbus.SessionBus().get_object('org.kde.kded', '/modules/khotkeys')
    #     dbus.Interface(kwin, 'org.kde.khotkeys').reread_configuration()

    def proceed(self):
        """To be reimplemented in subclasses.
        """
        pass
        # self.print_html('<b>Doing nothing</b>')


class ActionSet():
    """Action set properties: description, actions contained in the set, etc.
    """
    name = ''
    description = ''  # html description
    actions = []  # list of action names contained in this action set


class ActionPackage():
    """Action package properties: desription, author, etc.
    """
    author = ''
    version = 0
    description = ''  # html description

