from scripts import Action


class Action(Action):

    name = "Produkt Plasma theme"
    description = "Custom widget (QtCurve) and color themes."

    def proceed(self):
        self.copy_file('./Produkt/',
                       '~/.kde/share/apps/desktoptheme/')
        self.update_kconfig('./plasmarc',
                            '~/.kde/share/config/plasmarc')
