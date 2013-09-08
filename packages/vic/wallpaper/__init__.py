import dbus
from PyKDE4.kdecore import KConfig

from mykde import BaseAction, signals


class Action(BaseAction):

    name = "Wallpaper"
    description = """\
Flower Monasterio, Cusco, Peru.<br>
This work by <a href="http://si.smugmug.com">Simon Tong</a> is licensed under a 
<a href="http://creativecommons.org/licenses/by-nc-sa/3.0/us/">Creative Commons License</a><br>
<br>
<img src="screenshot.jpg"/>
"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        signals.kwin_stopped.connect(self.proceed2)

    def proceed(self):
        self.print_message('Action will performed after Plasma is stopped.')

    def proceed2(self, **kwargs):
        # https://bugs.kde.org/show_bug.cgi?id=217950
        self.print_message('Changing wallpaper.')
        wallpaper_path = self.copy_file(
            './flower monasterio cusco peru.jpg', '~/.kde/share/wallpapers/')

        activity_manager = dbus.SessionBus().get_object(
            'org.kde.ActivityManager', '/ActivityManager/Activities')
        current_activity_id = dbus.Interface(
            activity_manager, 'org.kde.ActivityManager.Activities').CurrentActivity()

        konf_path = self.make_abs_path('~/.kde/share/config/plasma-desktop-appletsrc')
        # http://api.kde.org/pykde-4.7-api/kdecore/KConfig.html
        konf = KConfig(konf_path, KConfig.SimpleConfig)
        containments = konf.group('Containments')
        for group_name in containments.groupList():
            group = containments.group(group_name)
            # http://api.kde.org/pykde-4.7-api/kdecore/KConfigGroup.html
            if group.readEntry('activityId') == current_activity_id:
                wallpaper_image_group = group.group('Wallpaper').group('image')
                wallpaper_image_group.writeEntry('wallpaper', wallpaper_path)

