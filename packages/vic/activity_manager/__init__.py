from scripts import Action


class Action(Action):

    name = "Disable activity manager"
    description = "Prevent running KDE activity manager"
    
    def proceed(self):
        command = 'chmod -x /usr/bin/kactivitymanagerd'
        retcode = self.kdesudo(command, self.name)
        if retcode:
#            QtGui.QMessageBox.critical(self.main_window, 'Error',
#                                       'An error occured during apt-get install')
            return False