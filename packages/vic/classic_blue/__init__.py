from scripts import Action


class Action(Action):

    name = "Classic Blue"
    description = "Custom widget (QtCurve) and color themes."
    packages = ['qtcurve', 'fonts-droid']

    def proceed(self):
        self.copy_file('./classic_blue.qtcurve',
                       '~/.kde/share/apps/QtCurve/')
        self.copy_file('./classic_blue.colors',
                       '~/.kde/share/apps/color-schemes/')
        self.update_kconfig('./stylerc',
                            '~/.config/qtcurve/stylerc')
        self.update_kconfig('./kwinrc',
                            '~/.kde/share/config/kwinrc')
        self.update_kconfig('./kdeglobals',
                            '~/.kde/share/config/kdeglobals')
