from packages import Action


class Action(Action):

    name = "Qmmp"
    description = "Qmmp with custom settings"

    def proceed(self):
        self.install_package('qmmp')
        self.copy_files('./.qmmp', '~/')
