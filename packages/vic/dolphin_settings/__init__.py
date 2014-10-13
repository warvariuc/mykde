from mykde import BaseAction


class Action(BaseAction):

    name = "Dolphin"
    description = "Custom Dolphin settings"
    
    def proceed(self):
        self.update_kconfig('./dolphinrc', '~/.kde/share/config/dolphinrc')
