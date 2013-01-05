from scripts import Action


class Action(Action):

    name = 'Krusader'
    description = "Krusader with custom settings"
    packages = ['krusader', 'kompare']

    def proceed(self):
        self.update_kconfig('./krusaderrc', '~/.kde/share/config/krusaderrc')
