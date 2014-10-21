import mykde


class Action(mykde.BaseAction):

    name = 'Krusader'
    description = "Krusader with custom settings"
    packages = ['krusader', 'kwrite', 'kompare', 'p7zip-full']

    def proceed(self):
        self.update_kconfig('./krusaderrc', '~/.kde/share/config/krusaderrc')
        self.update_xmlconfig('./krusaderui.rc', '~/.kde/share/apps/krusader/krusaderui.rc')
