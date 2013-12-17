from mykde import BaseAction


class Action(BaseAction):

    name = 'Stop Akonadi'
    description = "Make Akonadi MySQL server to not start, thus Akonadi services will not start."

    def proceed(self):
        self.update_kconfig('./akonadiserverrc', '~/.config/akonadi/akonadiserverrc')
