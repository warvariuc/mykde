from mykde import Action, signals


class Action(Action):

    name = "Produkt Plasma theme"
    description = """\
<a href="http://kde-look.org/content/show.php/?content=124213">Produkt Plasma theme</a><br>
<br>
<img src="screenshot.png"/>
"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        signals.plasma_stopped.connect(self.proceed2)

    def proceed(self):
        self.print_message('Action will performed when Plasma is stopped.')

    def proceed2(self, **kwargs):
        self.copy_file('./Produkt/',
                       '~/.kde/share/apps/desktoptheme/')
        self.update_kconfig('./plasmarc',
                            '~/.kde/share/config/plasmarc')
