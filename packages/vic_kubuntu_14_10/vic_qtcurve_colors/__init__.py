"""
It is not enough to copy color scheme and set it as used in kdeglobals.
KDE keeps using *current* colors, which are stored in kdeglobals too, but are set when you apply
selected color theme in system settings.
"""
import mykde


class Action(mykde.BaseAction):

    name = "QtCurve Vic theme and colors for widgets and windows"
    author = 'Victor Varvariuc'
    description = """
Custom widget (QtCurve) and color themes. I tried to make the QtCurve theme to contain is little
lines as possible - to make it visually light.<br>
<br>
<img src="screenshot.png"/>
"""
    packages = ['qtcurve', 'fonts-droid']

    affects = [mykde.Kwin]

    def proceed(self):
        self.print_text('Installing %r' % self.name)
        self.copy_file('./vic.qtcurve', '~/.kde/share/apps/QtCurve/')
        self.copy_file('./Vic.colors', '~/.kde/share/apps/color-schemes/')
        self.update_kconfig('./stylerc', '~/.config/qtcurve/stylerc')
        self.copy_file('./windowBorderSizes', '~/.config/qtcurve/')
        self.update_kconfig('./kwinrc', '~/.kde/share/config/kwinrc')
        self.update_kconfig('./kwinqtcurverc', '~/.kde/share/config/kwinqtcurverc')
        self.update_kconfig('./kdeglobals', '~/.kde/share/config/kdeglobals')
