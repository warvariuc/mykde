from scripts import Action


class Action(Action):

    name = "Wallpaper"
    description = """\
Flower Monasterio, Cusco, Peru.<br>
This work by <a href="http://si.smugmug.com">Simon Tong</a> is licensed under a 
<a href="http://creativecommons.org/licenses/by-nc-sa/3.0/us/">Creative Commons License</a><br>
<br>
<img src="screenshot.jpg"/>
"""

    def proceed(self):
        self.copy_file('./flower monasterio cusco peru.jpg',
                       '~/.kde/share/wallpapers/')
#        self.update_kconfig('./plasmarc',
#                            '~/.kde/share/config/plasmarc')



#import sys
#import os
#import subprocess
#
#import dbus
#from PyQt4 import QtGui
#from PyKDE4.kdecore import KConfig
#
#
#activity_manager = dbus.SessionBus().get_object('org.kde.kactivitymanagerd', '/ActivityManager')
#current_activity_id = dbus.Interface(activity_manager, 'org.kde.ActivityManager').CurrentActivity()
#print('Current activity ID:', current_activity_id)
#
#kwin = dbus.SessionBus().get_object('org.kde.kwin', '/KWin')
#print('Current desktop:', dbus.Interface(kwin, 'org.kde.KWin').currentDesktop())
#
#print('Primary screen:', QtGui.QApplication(sys.argv).desktop().primaryScreen())
#
#konf_path = os.path.expanduser('~/.kde/share/config/plasma-desktop-appletsrc')
## http://api.kde.org/pykde-4.7-api/kdecore/KConfig.html
#konf = KConfig(konf_path, KConfig.SimpleConfig)
#containments = konf.group('Containments')
#for group_name in containments.groupList():
#    group = containments.group(group_name)
#    # http://api.kde.org/pykde-4.7-api/kdecore/KConfigGroup.html
#    if group.readEntry('activityId') == current_activity_id:
#        print('Containment ID of the current activity:', group_name)
#        wallpaper_image_group = group.group('Wallpaper').group('image')
#        wallpaper_image_group.writeEntry('wallpaper', '/home/vic/.kde/share/wallpapers/morning 3 machu picchu peru-X3.jpg')
#
#
## dbus call does not cause wallpaper change, i guess applet config is not re-read
## plasma = dbus.SessionBus().get_object('org.kde.plasma-desktop', '/MainApplication')
## dbus.Interface(plasma, 'org.kde.KApplication').reparseConfiguration()
#
#print('Restarting plasma...')
#with open(os.devnull, "w") as fnull:
#    subprocess.call('kquitapp plasma-desktop && sleep 2s', shell=True, stdout=fnull, stderr=fnull)
#    konf.sync()  # save the configuration
#    subprocess.call('plasma-desktop &', shell=True, stdout=fnull, stderr=fnull)
