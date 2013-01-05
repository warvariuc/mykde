from scripts import Action


class Action(Action):

    name = "Global keyboard shortcuts"
    description = """\
<ul>
    <li>Meta + L - Lock screen</li>
    <li>Meta + D - Show desktop</li>
</ul>
"""
    
    def proceed(self):
        self.update_kconfig('./kglobalshortcutsrc', '~/.kde/share/config/kglobalshortcutsrc')
