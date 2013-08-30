from mykde import BaseAction, signals


class Action(BaseAction):

    name = "Classic Blue"
    author = 'Victor Varvariuc'
    description = """\
Custom widget (QtCurve) and color themes. I tried to make the QtCurve theme to contain is little
lines as possible - to make it visually light.<br>
<br>
<img src="screenshot.png"/>
"""
    packages = ['qtcurve', 'fonts-droid']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        signals.kwin_stopped.connect(self.proceed2)

    def proceed(self):
        self.print_message('Action will performed after Kwin is stopped.')

    def proceed2(self, **kwargs):
        self.copy_file('./classic_blue.qtcurve', '~/.kde/share/apps/QtCurve/')
        self.copy_file('./classic_blue.colors', '~/.kde/share/apps/color-schemes/')
        self.update_kconfig('./stylerc', '~/.config/qtcurve/stylerc')
        self.update_kconfig('./kwinrc', '~/.kde/share/config/kwinrc')
        self.update_kconfig('./kwinqtcurverc', '~/.kde/share/config/kwinqtcurverc')
        self.update_kconfig('./kdeglobals', '~/.kde/share/config/kdeglobals')
