from mykde import BaseAction, signals


class Action(BaseAction):

    name = "Produkt Plasma theme"
    description = """
<a href="http://kde-look.org/content/show.php/?content=124213">Produkt Plasma theme</a><br>
<br>
<img src="screenshot.png"/>
"""

    def proceed(self):
        self.print_text('Action will be performed when Plasma is stopped.')
        # specifying dispatch_uid to prevent multiple calls
        signals.plasma_stopped.connect(self._proceed, dispatch_uid=self.__class__)
        self.restart_plasma()

    def _proceed(self, **kwargs):
        self.print_text('Installing %r' % self.name)
        self.copy_file('./Produkt/',
                       '~/.kde/share/apps/desktoptheme/')
        self.update_kconfig('./plasmarc',
                            '~/.kde/share/config/plasmarc')
