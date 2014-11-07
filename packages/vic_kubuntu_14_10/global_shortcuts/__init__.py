import mykde


class Action(mykde.BaseAction):

    name = "Global keyboard shortcuts"
    description = """
<ul>
    <li><kbd>Meta+L</kbd> - Lock screen</li>
    <li><kbd>Meta+D</kbd> - Show desktop</li>
    <li><kbd>Meta - the modifier key for windows (moving, etc.)</li>
</ul>
"""
    
    affects = [mykde.KGlobalAccel, mykde.Kwin]

    def proceed(self):
        self.update_kconfig('./kglobalshortcutsrc', '~/.kde/share/config/kglobalshortcutsrc')
        self.update_kconfig('./kwinrc', '~/.kde/share/config/kwinrc')
