import mykde


class Action(mykde.BaseAction):

    name = "Qmmp"
    description = "Qmmp with custom settings"
    packages = ['qmmp']

    def proceed(self):
        self.copy_file('./.qmmp/', '~/')
