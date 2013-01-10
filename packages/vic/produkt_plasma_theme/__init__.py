from scripts import Action


class Action(Action):

    name = "Produkt Plasma theme"
    description = """\
<a href="http://kde-look.org/content/show.php/?content=124213">Produkt Plasma theme</a><br>
<br>
<img src="screenshot.png"/>
"""

    def proceed(self):
        self.copy_file('./Produkt/',
                       '~/.kde/share/apps/desktoptheme/')
        self.update_kconfig('./plasmarc',
                            '~/.kde/share/config/plasmarc')
