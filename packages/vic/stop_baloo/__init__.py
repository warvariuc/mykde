from mykde import BaseAction


class Action(BaseAction):

    name = 'Turn off Baloo'
    description = "Disable KDE desktop search (Baloo)."

    def proceed(self):
        self.call("kwriteconfig --file baloofilerc --group 'Basic Settings' --key 'Indexing-Enabled' false")
