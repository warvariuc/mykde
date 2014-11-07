import mykde


class Action(mykde.BaseAction):

    name = "Dolphin"
    description = "Custom Dolphin settings"
    
    def proceed(self):
        self.update_kconfig('./dolphinrc', '~/.kde/share/config/dolphinrc')
