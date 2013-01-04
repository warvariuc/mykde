import subprocess
import json
import traceback
import os
import sys
import time

import dbus
import apt
from distutils import dir_util, file_util
from PyQt4 import QtGui, QtCore
from PyKDE4.kdecore import KConfig, KConfigGroup, KUrl
from PyKDE4.kdeui import KGlobalSettings
from PyKDE4.kio import KRun


# disable PyQt input hook in order for ipdb to work
QtCore.pyqtRemoveInputHook()


class ActionMeta(type):
    """Action metaclass to make Action sublclasses sortable.
    """
    def __lt__(self, other):
        return id(self) < id(other)

    def __eq__(self, other):
        return id(self) == id(other)


class Action(metaclass=ActionMeta):

    name = None
    description = "HTML description of the action"
    repositories = {}  # {repo_name: (repo_url, public_key_url)} repositories for installing packages
    packages = []  # list of package names to install

    def __init__(self, main_window):
        assert isinstance(main_window, QtGui.QMainWindow)
        self.main_window = main_window

    def install_repositories(self, repositories):
        assert isinstance(repositories, dict)
        if not repositories:
            self.print_message('No repositories required to install.')
            return

        commands = []
        # check if file exists
        for repo_name, (repo_url, public_key_url) in repositories.items():
            assert isinstance(repo_name, str)
            assert isinstance(repo_url, str)
            assert isinstance(public_key_url, str)
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
            self.print_message('All required repositories are already installed')
            return True

        commands.append('apt-get update')
        command = "sudo sh -c '%s'" % '\n'.join(commands)
#        self.open_konsole(command)
        comment = 'Install additional repositories'
        window_id = self.main_window.effectiveWinId()

        retcode, msg = self.call(
            ['kdesudo', '--comment', comment, '--attach', str(window_id), '-c', command]
        )
        if retcode:
            QtGui.QMessageBox.critical(self.main_window, 'Error',
                                       'An error occured during apt-get install')
            return False

        return True

    def open_konsole(self, text):
        """Open a Konsole and type text in it.
        """
        bus = dbus.SessionBus()
        konsole = bus.get_object('org.kde.konsole', '/Konsole')
        session_id = dbus.Interface(konsole, 'org.kde.konsole.Window').newSession()
        session = bus.get_object('org.kde.konsole', '/Sessions/%s' % session_id)
        session.sendText(text)

    def print_message(self, message, end='\n'):
        self.main_window.print_message(message, end=end)

    def install_packages(self, package_names):
        """apt-get install packages, which are not yet installed
        @param package_names: list of package names to install
        """
        assert isinstance(package_names, (list, tuple))
        if not package_names:
            self.print_message('No packages required to install.')
            return
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
            self.print_message('All required packages are already installed')
            return True

        message = 'These additional packages must be installed:<ul>'
        for package_name, package_summary in packages.items():
            message += '<li><b>%s</b>: %s</li>' % (package_name, package_summary)
        message += '</ul>'
        res = QtGui.QMessageBox.question(self.main_window, 'Required packages', message,
                                         QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                                         QtGui.QMessageBox.Ok)
        if res != QtGui.QMessageBox.Ok:
            return

        self.print_message('<>Installing additional packages:<hr>', end='')
        comment = 'Install required packages'
        window_id = self.main_window.effectiveWinId()
        cmd = 'apt-get --assume-yes install %s' % ' '.join(packages)
        self.print_message(cmd)

        retcode, msg = self.call(
            ['kdesudo', '--comment', comment, '--attach', str(window_id), '-c', cmd]
        )
        if retcode:
            QtGui.QMessageBox.critical(self.main_window, 'Error',
                                       'An error occured during apt-get install')
            return False

        self.print_message('<><hr>The packages were sucessfully installed.')
        QtGui.QMessageBox.information(self.main_window, 'Packages were installed',
                'The packages were sucessfully installed.')
        return True

    def _get_abs_path(self, file_path):
        file_path = os.path.expanduser(file_path)
        if os.path.isabs(file_path):
            return os.path.normpath(file_path)
        module_dir = os.path.dirname(sys.modules[self.__class__.__module__].__file__)
        file_path = os.path.join(module_dir, file_path)
        file_path = os.path.abspath(file_path)
        return file_path

    def update_kconfig(self, source_config_path, dest_config_path):
        """Update a configuration file which is in format of kconfig
        @param source_config_path: relative path to the source configuration file
        @param dest_config_path: path to the file to apply patch to
        """
        assert isinstance(source_config_path, str)
        assert isinstance(dest_config_path, str)
        assert not os.path.isabs(source_config_path), 'The source should be relative'
        source_config_path = self._get_abs_path(source_config_path)
        assert os.path.isfile(source_config_path)
        dest_config_path = self._get_abs_path(dest_config_path)
        self.print_message('Updating configuration in `%s` from `%s`'
                           % (dest_config_path, source_config_path))

        # http://api.kde.org/4.0-api/kdelibs-apidocs/kdeui/html/classKGlobalSettings.html
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

        src_cfg = KConfig(source_config_path, KConfig.NoGlobals)
        dst_cfg = KConfig(dest_config_path, KConfig.NoGlobals)
        bkp_cfg = KConfig('', KConfig.NoGlobals)  # we keep here original settings of dest

        update_group(src_cfg, dst_cfg, bkp_cfg)
        # update top level entries
        update_group(src_cfg.group(''), dst_cfg.group(''), bkp_cfg)

        dst_cfg.sync()  # save the current state of the configuration object

#        if bkpCfgPath:
#            bkp_cfg.sync()

    def copy_file(self, src_path, dst_path, link=None):
        """Copy a file.
        If `src_path` is a file, `dst_path` must not be a directory, but a full file path.
        If `src_path` is a directory, `dst_path` must be a directory path inside which  `src_path`
        directory will be copied.
        """
        src_path = self._get_abs_path(src_path)
        dst_path = self._get_abs_path(dst_path)
        if not os.path.exists(src_path):
            raise ValueError('Source path does not exist: %s' % src_path)
        if os.path.isfile(src_path) or link:
            dir_util.mkpath(os.path.dirname(dst_path))
            file_util.copy_file(src_path, dst_path, link=link)
        elif os.path.isdir(src_path):
            dir_util.mkpath(dst_path)
            dir_util.copy_tree(src_path, dst_path)
        else:
            raise ValueError('Source path is not file/directory: %s' % src_path)

    def delete_file(self, file_path):
        """Delete a file.
        """
        if not os.path.exists(file_path):
            return
        if os.path.isdir(file_path):
            dir_util.remove_tree(file_path)
        else:
            os.remove(file_path)

    def call(self, cmd):
        """Run a program.
        """
        assert isinstance(cmd, (str, tuple, list))
        self.print_message(cmd if isinstance(cmd, str) else ' '.join(cmd))
        shell = isinstance(cmd, str)

        process = subprocess.Popen(cmd, bufsize=1, close_fds=True, shell=shell,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        output = []
        while True:
            time.sleep(0.1)
            line = process.stdout.readline().decode('utf-8')
            if not line:
                break
            output.append(line)
            self.print_message(line, end='')

        output = '\n'.join(output)
        retcode = process.poll()
        return retcode, output

    def request_kde_reload_config(self):
        # https://projects.kde.org/projects/kde/kde-workspace/repository/revisions/master/entry/kcontrol/style/kcmstyle.cpp
        kGlobalSettings = KGlobalSettings.self()
        self.print_message('Notifying all KDE applications about the global settings change.')
        kGlobalSettings.emitChange(KGlobalSettings.StyleChanged)
        kGlobalSettings.emitChange(KGlobalSettings.SettingsChanged)
        kGlobalSettings.emitChange(KGlobalSettings.ToolbarStyleChanged)
        kGlobalSettings.emitChange(KGlobalSettings.PaletteChanged)
        kGlobalSettings.emitChange(KGlobalSettings.FontChanged)
        kGlobalSettings.emitChange(KGlobalSettings.IconChanged)
        kGlobalSettings.emitChange(KGlobalSettings.CursorChanged)

        self.request_kwin_reload_config()
        self.request_plasma_reload_config()

    def request_plasma_reload_config(self):
        self.print_message('Asking plasma to reload its config')
        plasma = dbus.SessionBus().get_object('org.kde.plasma-desktop', '/MainApplication')
        dbus.Interface(plasma, 'org.kde.KApplication').reparseConfiguration()

    def request_kwin_reload_config(self):
        self.print_message('Asking Kwin to reload its config')
        kwin = dbus.SessionBus().get_object('org.kde.kwin', '/MainApplication')
        dbus.Interface(kwin, 'org.kde.KApplication').reparseConfiguration()

    def proceed(self):
        """To be reimplemented in subclasses.
        """
        pass


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
