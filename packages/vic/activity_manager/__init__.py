from scripts import Action


class Action(Action):

    name = "Disable activity manager"
    description = "Prevent running KDE activity manager"
    
    def proceed(self):
        pass # self.call('# chmod -x /usr/bin/kactivitymanagerd')
