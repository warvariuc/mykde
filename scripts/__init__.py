import subprocess
import json
import traceback

import apt
from PyQt4 import QtGui
from PyKDE4.kdecore import KConfig, KConfigGroup, KUrl
from PyKDE4.kdeui import KGlobalSettings
from PyKDE4.kio import KRun



def debug_trace():
    '''Set a tracepoint in the Python debugger that works with Qt'''
    from PyQt4.QtCore import pyqtRemoveInputHook
    from pdb import set_trace
    pyqtRemoveInputHook()
    set_trace()


class ActionMeta(type):
    "Action metaclass to make Action sublclasses sortable."

    def __lt__(self, other):
        return id(self) < id(other)

    def __eq__(self, other):
        return id(self) == id(other)


class Action(metaclass = ActionMeta):

    name = None
    description = "HTML description of the action"
    trusted_public_keys = []  # public to keys to install for repositories
    repositories = {}  # {repo_name: repo_url} repositories for installing packages
    packages = []  # list of package names to install

    def __init__(self, main_window):
        assert isinstance(main_window, QtGui.QMainWindow)
        self.main_window = main_window
        
    def print_message(self, message):
        text_edit = self.main_window.text_edit
        tc = text_edit.textCursor()
        tc.movePosition(QtGui.QTextCursor.End)
        text_edit.setTextCursor(tc)
        text_edit.insertHtml(message)
        text_edit.ensureCursorVisible() # scroll to the new message

    def install_trusted_public_keys(self, key_urls):
        assert isinstance(key_urls, (list, tuple))
        for url in key_urls:
            self.call('wget -q -O - %s | sudo apt-key add -' % url)

    def add_repositories(self, repositories):
        assert isinstance(repositories, dict)
        self.call("""sudo sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'""")

    def update_package_index(self):
        self.call('sudo apt-get update')

    def install_packages(self, package_names):
        """
        apt-get install packages, which are not yet installed
        @param package_names: list of package names to install
        """
        # TODO: show a window with the list of required packages and their description
        assert isinstance(package_names, (list, tuple))
        packages = {package_name: None for package_name in package_names}

        self.print_message('Checking if required packages are already installed...')
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
            return True  # all required packages are installed

        message = 'These additional packages must be installed:<ul>'
        for package_name, package_summary in packages.items():
            message += '<li><b>%s</b>: %s</li>' % (package_name, package_summary)
        message += '</ul>'
        res = QtGui.QMessageBox.question(
            self.main_window, 'Required packages', message,
            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Ok
        )
        if res != QtGui.QMessageBox.Ok:
            return

        self.print_message('Installing additional packages...')
        window_id = self.main_window.effectiveWinId()
        comment = 'Install required packages'
        cmd = 'apt-get --assume-yes install %s' % ' '.join(packages)
        res, msg = self.call(['kdesudo', '--comment', comment, '--attach', str(window_id), '-c', cmd])
        if not res:
            QtGui.QMessageBox.critical(
                self.main_window, 'Error',
                'An error occured during apt-get install:\n\n%s' % msg
            )
            return

        QtGui.QMessageBox.information(self.main_window, 'Packages were installed',
                'The packages were sucessfully installed:\n\n%s' % msg)
        return True

    def update_kconfig(self):
        """
        Update a configuration file which is in format of kconfig
        """

    def copy_file(self, src, dst):
        """
        Copy a file
        """

    def call(self, args):
        "Run an external program."
        subprocess.call(args)
        try:
            return True, subprocess.check_output(args)
        except subprocess.CalledProcessError as exc:
            return False, exc.output

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

    def proceed(self):
        pass


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
