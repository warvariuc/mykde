import mykde


class Action(mykde.BaseAction):

    name = "Produkt Plasma theme"
    description = """
<a href="http://kde-look.org/content/show.php/?content=124213">Produkt Plasma theme</a><br>
<br>
<img src="screenshot.png"/>
"""

    affects = [mykde.Plasma]

    def proceed(self):
        self.print_text('Installing %r' % self.name)
        self.copy_file('./Produkt/', '~/.kde/share/apps/desktoptheme/')
        self.update_kconfig('./plasmarc', '~/.kde/share/config/plasmarc')
