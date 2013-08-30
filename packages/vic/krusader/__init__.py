from mykde import BaseAction


class Action(BaseAction):

    name = 'Krusader'
    description = "Krusader with custom settings"
    packages = ['krusader', 'kwrite', 'kompare', 'p7zip-full']

    def proceed(self):
        self.update_kconfig('./krusaderrc', '~/.kde/share/config/krusaderrc')
