from packages import Action


class Action(Action):

    name = 'Krusader'
    description = "Krusader with custom settings"

    def proceed(self):
        self.install_package('krusader', 'kompare')
        self.update_kconfig('./krusaderrc', '~/.kde/share/config/krusaderrc')
