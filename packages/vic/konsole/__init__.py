from mykde import BaseAction


class Action(BaseAction):

    name = 'Konsole settings'
    description = "Custom settings for Konsole"

    def proceed(self):
        self.copy_file('./vic.colorscheme',
                       '~/.kde/share/apps/konsole/')
        self.update_kconfig('./Shell.profile',
                            '~/.kde/share/apps/konsole/Shell.profile')
        self.update_xmlconfig('./konsoleui.rc',
                              '~/.kde/share/apps/konsole/konsoleui.rc')
        self.update_xmlconfig('./sessionui.rc',
                              '~/.kde/share/apps/konsole/konsole/sessionui.rc')
