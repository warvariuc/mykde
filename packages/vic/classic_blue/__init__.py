from scripts import Action


class Action(Action):

    name = "Classic Blue"
    description = "Custom widget (QtCurve) and color themes."
    packages = ['qtcurve', 'fonts-droid']

    def proceed(self):
        self.copy_file('./classic_blue.colors',
                       '~/.kde/share/apps/QtCurve/classic_blue.qtcurve')
        self.copy_file('./classic_blue.qtcurve',
                       '~/.kde/share/apps/color-schemes/classic_blue.colors')
        self.update_kconfig('./stylerc',
                            '~/.config/qtcurve/stylerc')
        self.update_kconfig('./kwinrc',
                            '~/.kde/share/config/kwinrc')
        self.update_kconfig('./kdeglobals',
                            '~/.kde/share/config/kdeglobals')
