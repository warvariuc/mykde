__author__ = "Victor Varvariuc <victor.varvariuc@gmail.com>"

import os, sys, datetime
from distutils import dir_util
from PyQt4 import QtGui
from PyKDE4.kdecore import KConfig, KConfigGroup, KUrl
from PyKDE4.kdeui import KGlobalSettings
from PyKDE4.kio import KRun
import apt, json, subprocess, traceback

#import pprint
#pprint.pprint(sys.modules)
import scripts.main
main = sys.modules['scripts.main']


def checkPackages(*requiredPackages):
    requiredPackages = set(requiredPackages)

    main.mainWindow.statusBar().showMessage('Checking if required packages are installed...')
    packages = apt.Cache()
    packages.open()
    for package in packages:
        if package.is_installed and package.name in requiredPackages:
            requiredPackages.remove(package.name)
    main.mainWindow.statusBar().clearMessage()

    if not requiredPackages:
        return True # all required packages are installed

    res = QtGui.QMessageBox.question(main.mainWindow, 'Required packages',
            'These additional packages must be installed:\n' + '\n'.join(requiredPackages),
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
    if res != QtGui.QMessageBox.Yes:
        return

    main.mainWindow.statusBar().showMessage('Installing additional packages...')
    cmd = 'kdesudo "apt-get --assume-yes install ' + ' '.join(requiredPackages) + '"'
    try:
        output = subprocess.check_output(cmd, shell = True)
    except subprocess.CalledProcessError as e:
        QtGui.QMessageBox.warning(main.mainWindow, 'Error',
                'An error occured during apt-get install:\n\n' + e.output)
        return
    finally:
        main.mainWindow.statusBar().clearMessage()

    QtGui.QMessageBox.information(main.mainWindow, 'Packages installed',
            'The packages were sucessfully installed:\n\n' + output)
    return True



def applyConfig(srcCfgPath, dstCfgPath, bkpCfgPath=''):
# http://api.kde.org/4.0-api/kdelibs-apidocs/kdeui/html/classKGlobalSettings.html
# http://api.kde.org/4.x-api/kdelibs-apidocs/kdecore/html/classKConfig.html
# http://api.kde.org/4.x-api/kdelibs-apidocs/kdecore/html/classKConfigGroup.html
# https://projects.kde.org/projects/kde/kdebase/kde-runtime/repository/show/kreadconfig
    def walkGroup(groupName, srcGroup, dstGroup, bkpGroup):
        #print('Walking group: [' + groupName + ']')
        groups = list(srcGroup.groupList())
        srcGroup = srcGroup.group(groupName)
        dstGroup = dstGroup.group(groupName)
        bkpGroup = bkpGroup.group(groupName)

        for entryName in list(srcGroup.entryMap()):
            newEntryValue = unicode(srcGroup.readEntry(entryName))
            oldEntryValue = unicode(dstGroup.readEntry(entryName))
            dstGroup.writeEntry(entryName, newEntryValue)
            if newEntryValue != oldEntryValue and oldEntryValue:
                bkpGroup.writeEntry(entryName, oldEntryValue)

        for groupName in groups:
            walkGroup(groupName, srcGroup, dstGroup, bkpGroup)

    srcCfg = KConfig(srcCfgPath, KConfig.NoGlobals)
    dstCfg = KConfig(dstCfgPath, KConfig.NoGlobals)
    bkpCfg = KConfig(bkpCfgPath, KConfig.NoGlobals) # we keep here original settings of dest
    
    walkGroup('', srcCfg, dstCfg, bkpCfg)

    dstCfg.sync() # save the current state of the configuration object

    if bkpCfgPath:
        bkpCfg.sync()



def notifyKDEReloadConfig():
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



def install(themeDir):
    try:
        settingsFilePath = os.path.join(themeDir, 'settings')
        with open(settingsFilePath) as file:
            settings = json.load(file)
        requiredPackages = settings['requiredPackages'].split()
        if not checkPackages(*requiredPackages):
            QtGui.QMessageBox.warning(main.mainWindow, 'Required packages',
                    'Not all required packages are installed.')
            return
    except:
        QtGui.QMessageBox.warning(main.mainWindow, 'Error',
                'An error occured during install:\n' + traceback.format_exc())
        return

    todayStr = '{0:%Y-%m-%d_%H-%M-%S}'.format(datetime.datetime.now())
    homeDir = os.path.expanduser('~')
    srcDir = os.path.join(themeDir, 'files') # source folder of files to copy
    cfgDir = os.path.join(themeDir, 'config') # source folder of configs to apply
    bkpDir = os.path.join(homeDir, '.mykde', 'backup', todayStr) # backup folder for possible recovery of original configs

    if not os.path.isdir(bkpDir):
        os.makedirs(bkpDir)

    print('Copying files from\n   ', srcDir, '\n  to\n   ', homeDir)
    filesCopied = dir_util.copy_tree(srcDir, homeDir, dry_run=0)
    print('Copied', len(filesCopied), 'file(s)')

    # save list of copied files
    with open(os.path.join(bkpDir, 'files'), 'w') as file:
        for filePath in filesCopied:
            file.write(filePath + '\n')

    print('Applying new configuration')
    for dirpath, dirnames, filenames in os.walk(cfgDir):
        for cfgFileName in filenames:
            srcCfgPath = os.path.join(dirpath, cfgFileName)
            relPath = os.path.relpath(srcCfgPath, cfgDir)
            dstCfgPath = os.path.join(homeDir, relPath)
            bkpCfgPath = os.path.join(bkpDir, relPath)
            bkpCfgDir = os.path.dirname(bkpCfgPath)
            if not os.path.isdir(bkpCfgDir):
                os.makedirs(bkpCfgDir)
#            print('Updating configuration file:\n   ', dstCfgPath)
#            print('  from\n   ', srcCfgPath, '\n  backup to\n   ', bkpCfgPath)
            applyConfig(srcCfgPath, dstCfgPath, bkpCfgPath)


    notifyKDEReloadConfig()

    QtGui.QMessageBox.information(main.mainWindow, 'Done',
                'All needed files were copied and new settings applied.\n'\
                'Some changes will only affect newly started applications.\n'\
                'If you see any glitches, log out and log back in \n'
                'to fully apply new settings.')





# http://api.kde.org/4.x-api/kdelibs-apidocs/kdecore/html/classKStandardDirs.html
#from PyKDE4.kdecore import KStandardDirs
#kStandardDirs = KStandardDirs()
