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
            newEntryValue = srcGroup.readEntry(entryName)
            oldEntryValue = dstGroup.readEntry(entryName)
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
