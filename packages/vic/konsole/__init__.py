from mykde import BaseAction


class Action(BaseAction):

    name = 'Konsole settings'
    description = """Custom settings for Konsole:
- custom color theme
- Ctrl+Shift+X - to clear scrollback and reset
- Ctrl+PageDown/PageUp - to switch to next/previous tab
- enabled unlimited history
- other tweaks
"""

    def proceed(self):
        self.copy_file('./vic.colorscheme',
                       '~/.kde/share/apps/konsole/')
        self.update_kconfig('./Shell.profile',
                            '~/.kde/share/apps/konsole/Shell.profile')
        self.update_xmlconfig('./konsoleui.rc',
                              '~/.kde/share/apps/konsole/konsoleui.rc')
        self.update_xmlconfig('./sessionui.rc',
                              '~/.kde/share/apps/konsole/konsole/sessionui.rc')
