from mykde import BaseAction


class Action(BaseAction):

    name = "Qmmp"
    description = "Qmmp with custom settings"
    packages = ['qmmp']

    def proceed(self):
        self.copy_file('./.qmmp/', '~/')
