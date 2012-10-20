from scripts import Action


class Action(Action):

    name = "Qmmp"
    description = "Qmmp with custom settings"
    
    packages = ['qmmp']

    def proceed(self):
        self.copy_files('./.qmmp', '~/')
