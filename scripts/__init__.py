import subprocess
import json
import traceback

import apt
from PyQt4 import QtGui
from PyKDE4.kdecore import KConfig, KConfigGroup, KUrl
from PyKDE4.kdeui import KGlobalSettings
from PyKDE4.kio import KRun


class ActionMeta(type):
    "Action metaclass to make Action sublclasses sortable."

    def __lt__(self, other):
        return id(self) < id(other)

    def __eq__(self, other):
        return id(self) == id(other)


class Action(metaclass=ActionMeta):

    name = None
    description = "HTML description of the action"

    def install_packages(self, package_names):
        """
        apt-get install packages, which are not yet installed
        @param package_names: list of package names to install
        """
        assert isinstance(package_names, (list, tuple))
        package_names = set(package_names)

#        main.mainWindow.statusBar().showMessage('Checking if required packages are installed...')
        packages = apt.Cache()
        packages.open()
        for package in packages:
            if package.is_installed and package.name in package_names:
                package_names.remove(package.name)
        main.mainWindow.statusBar().clearMessage()

        if not package_names:
            return True  # all required packages are installed

        res = QtGui.QMessageBox.question(main.mainWindow, 'Required packages',
                'These additional packages must be installed:\n  ' + '\n  '.join(package_names),
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
        if res != QtGui.QMessageBox.Yes:
            return

#        main.mainWindow.statusBar().showMessage('Installing additional packages...')
        cmd = 'kdesudo "apt-get --assume-yes install %s"' % ' '.join(package_names)
        try:
            output = subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            QtGui.QMessageBox.warning(main.mainWindow, 'Error',
                    'An error occured during apt-get install:\n\n%s' % e.output)
            return
        finally:
            main.mainWindow.statusBar().clearMessage()

        QtGui.QMessageBox.information(main.mainWindow, 'Packages were installed',
                'The packages were sucessfully installed:\n\n%s' % output)
        return True

    def update_kconfig(self):
        """
        Update a configuration file which is in format of kconfig
        """

    def copy_file(self, src, dst):
        """
        Copy a file
        """

    def call(self, *args):
        "Run an external program."
        subprocess.call(list(args))

    def request_kde_reload_config(self):
        # https://projects.kde.org/projects/kde/kde-workspace/repository/revisions/master/entry/kcontrol/style/kcmstyle.cpp
        kGlobalSettings = KGlobalSettings.self()
        print('Notifying KDE apps about settings change.')
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
        print('Asking plasma to reload its config')
        self.call('dbus-send', '--dest=org.kde.plasma-desktop', '/MainApplication',
                  'org.kde.KApplication.reparseConfiguration')
#        print('Restarting plasma')
#        self.call('kquitapp', 'plasma-desktop')
#        self.call('plasma-desktop')

    def request_kwin_reload_config(self):
        print('Asking Kwin to reload its config')
        self.call('dbus-send', '--dest=org.kde.kwin', '/KWin', 'org.kde.KWin.reloadConfig')
#        print('Restarting kwin')
#        self.call("kwin", "--replace")


class ActionSet():
    "Action set properties: description, actions contained in the set, etc."
    name = ''
    description = ''  # html description
    actions = []  # list of action names contained in this action set 


class ActionPackage():
    "Action package properties: desription, author, etc."
    author = ''
    version = 0
    description = ''  # html description
