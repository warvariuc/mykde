import dbus
from PyKDE4 import kdecore

import mykde


# http://api.kde.org/frameworks-api/frameworks5-apidocs/plasma-framework/html/classPlasma_1_1Applet.html
PLASMA_DESKTOP_APPLETSRC_PATH = '~/.kde/share/config/plasma-desktop-appletsrc'


class Action(mykde.BaseAction):

    name = "Wallpaper"
    description = """
Flower Monasterio, Cusco, Peru.<br>
This work by <a href="http://si.smugmug.com">Simon Tong</a> is licensed under a 
<a href="http://creativecommons.org/licenses/by-nc-sa/3.0/us/">Creative Commons License</a><br>
<br>
<img src="screenshot.jpg"/>
"""
    affects = [mykde.Plasma]

    def proceed(self):
        # there is no API no change the wallpaper, so we do it manually
        # https://bugs.kde.org/show_bug.cgi?id=217950
        wallpaper_path = self.copy_file(
            './flower monasterio cusco peru.jpg', '~/.kde/share/wallpapers/')

        activity_manager = dbus.SessionBus().get_object(
            'org.kde.ActivityManager', '/ActivityManager/Activities')
        current_activity_id = dbus.Interface(
            activity_manager, 'org.kde.ActivityManager.Activities').CurrentActivity()

        self.print_text('Patching %s' % PLASMA_DESKTOP_APPLETSRC_PATH)
        konf_path = self.make_abs_path(PLASMA_DESKTOP_APPLETSRC_PATH)
        # http://api.kde.org/pykde-4.7-api/kdecore/KConfig.html
        konf = kdecore.KConfig(konf_path, kdecore.KConfig.SimpleConfig)
        containments = konf.group('Containments')
        for group_name in containments.groupList():
            group = containments.group(group_name)
            # http://api.kde.org/pykde-4.7-api/kdecore/KConfigGroup.html
            if (group.readEntry('activity') == 'Desktop' and
                    group.readEntry('activityId') == current_activity_id):
                group.group('Wallpaper').group('image').writeEntry('wallpaper', wallpaper_path)
