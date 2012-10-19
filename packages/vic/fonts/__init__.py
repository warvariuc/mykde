import os
from scripts import Action

"""
If a font in the browser in not Droid, in Google Chrome right click on the text
with the wrong font, select 'Inspect element', find 'Computed style' and
'font-family' in it:

font-family: 'lucida grande', tahoma, verdana, arial, sans-serif;

And for each font do 'fc=match':

vic@wic:~/Documents$ fc-match Helvetica
LiberationSans-Regular.ttf: "Liberation Sans" "Regular"

Ok, you found the offending font. Add it to 'fonts.conf' file.
"""

class Action(Action):

    name = 'Droid fonts everywhere'
    description = "Custom fonts"

    apt_packages_to_install = ['fonts-droid']

    def proceed(self):
        self.install_package('fonts-droid')
        self.update_kconfig('./kdeglobals', '~/.kde/share/config/kdeglobals')
        self.copy_file('./fonts.conf', '~/.config/fontconfig/')
        self.delete_file('~/.fonts.conf')  # or patch and then move it to:
        self.copy_file('./fonts.conf', '~/.config/fontconfig/')
        self.copy_file('./fonts.conf', '~/.fonts.conf')  # in 12.04 only this works
        self.request_kde_reload_config()

    def override_font(self, font, override):
        """Add necessary nodes to fonts.conf """
