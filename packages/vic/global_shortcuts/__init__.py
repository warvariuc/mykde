from mykde import BaseAction


class Action(BaseAction):

    name = "Global keyboard shortcuts"
    description = """
<ul>
    <li><kbd>Meta+L</kbd> - Lock screen</li>
    <li><kbd>Meta+D</kbd> - Show desktop</li>
</ul>
"""
    
    def proceed(self):
        self.update_kconfig('./kglobalshortcutsrc', '~/.kde/share/config/kglobalshortcutsrc')
