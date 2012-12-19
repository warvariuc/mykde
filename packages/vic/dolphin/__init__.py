from scripts import Action


class Action(Action):

    name = "Dolphin"
    description = "Custom Dolphin settings"
    
    packages = ['afuse']

    def proceed(self):
        self.update_kconfig('./dolphinrc', '~/_dolphinrc')
#        self.update_kconfig('./dolphinrc', '~/.kde/share/config/dolphinrc')
