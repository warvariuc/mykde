from scripts import Action


class Action(Action):

    name = "Classic Blue"
    author = 'Victor Varvariuc'
    description = """\
Custom widget (QtCurve) and color themes. I tried to make the QtCurve theme to contain is little
lines as possible - to make it visually light.
"""
    packages = ['qtcurve', 'fonts-droid']

    def proceed(self):
        self.copy_file('./classic_blue.qtcurve', '~/.kde/share/apps/QtCurve/')
        self.copy_file('./classic_blue.colors', '~/.kde/share/apps/color-schemes/')
        self.copy_file('./Hycons', '~/.kde/share/icons/')
        self.update_kconfig('./stylerc', '~/.config/qtcurve/stylerc')
        self.update_kconfig('./kwinrc', '~/.kde/share/config/kwinrc')
        self.update_kconfig('./kwinqtcurverc', '~/.kde/share/config/kwinqtcurverc')
        self.update_kconfig('./kdeglobals', '~/.kde/share/config/kdeglobals')
