import subprocess
from PyKDE4.kdecore import KConfig, KConfigGroup, KUrl
from PyKDE4.kdeui import KGlobalSettings


class ActionMeta(type):

    def __lt__(self, other):
        return id(self) < id(other)

    def __eq__(self, other):
        return id(self) == id(other)


class Action(metaclass=ActionMeta):

    name = None
    description = "HTML description of the action"

    def install_package(self):
        """
        apt-get install a package
        """

    def update_kconfig(self):
        """
        Update a configuration file which is in format of kconfig
        """

    def copy_file(self, src, dst):
        """
        Copy a file
        """

    def notify_kde_reload_config(self):
        # https://projects.kde.org/projects/kde/kdebase/kde-workspace/repository/revisions/master/entry/kcontrol/style/kcmstyle.cpp
        kGlobalSettings = KGlobalSettings.self()
        print('Asking KDE apps to recreate their styles according to new settings.')
        kGlobalSettings.emitChange(KGlobalSettings.StyleChanged)
        kGlobalSettings.emitChange(KGlobalSettings.SettingsChanged)
        kGlobalSettings.emitChange(KGlobalSettings.ToolbarStyleChanged)
        kGlobalSettings.emitChange(KGlobalSettings.PaletteChanged)
        kGlobalSettings.emitChange(KGlobalSettings.FontChanged)
        kGlobalSettings.emitChange(KGlobalSettings.IconChanged)
        kGlobalSettings.emitChange(KGlobalSettings.CursorChanged)
    
        print('Asking Kwin to reload its config')
        subprocess.call(['dbus-send', '--dest=org.kde.kwin', '/KWin', 'org.kde.KWin.reloadConfig'])
    #    print 'Restarting kwin'
    #    subprocess.call("kwin --replace")
    
        print('Asking plasma to reload its config')
        subprocess.call(['dbus-send', '--dest=org.kde.plasma-desktop', '/MainApplication', 'org.kde.KApplication.reparseConfiguration'])
    #    print 'Restarting plasma'
    #    subprocess.call(['kquitapp', 'plasma-desktop'])
    #    subprocess.call(['plasma-desktop'])


class ActionSet():
    "Action set properties: description"
    name = ''
    description = ''
    actions = []  # list of action names contained in this action set 


class ActionPackage():
    "Action package properties: desription, author, etc."
    author = ''
    version = 0
    description = ''
