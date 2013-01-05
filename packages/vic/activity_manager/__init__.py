from scripts import Action


class Action(Action):

    name = "Disable activity manager"
    description = "Prevent running KDE activity manager"
    
    def proceed(self):
        command = 'chmod -x /usr/bin/kactivitymanagerd'
        window_id = self.main_window.effectiveWinId()

        retcode, msg = self.call(
            ['kdesudo', '--comment', self.name, '--attach', str(window_id), '-c', command]
        )
        if retcode:
#            QtGui.QMessageBox.critical(self.main_window, 'Error',
#                                       'An error occured during apt-get install')
            return False