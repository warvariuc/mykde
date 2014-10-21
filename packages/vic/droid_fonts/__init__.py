import mykde

"""
If a font in the browser is not Droid, in Google Chrome right click on the text
with the wrong font, select 'Inspect element', find 'Computed style' and
'font-family' in it:

font-family: 'lucida grande', tahoma, verdana, arial, sans-serif;

And for each font do 'fc=match':

$ fc-match Helvetica
LiberationSans-Regular.ttf: "Liberation Sans" "Regular"

Ok, you found the offending font. Add it to 'fonts.conf' file.
"""


class Action(mykde.BaseAction):

    name = 'Droid fonts everywhere'
    description = """
Droid fonts are used everywhere possible, because they render very nice.<br>
In browser they should replace Verdana, Arial and other MS fonts.<br>
<br>
<img src="screenshot.png"/>
"""

    packages = ['fonts-droid']
    affects = [mykde.KdeSettings]

    def proceed(self):
        self.update_kconfig('./kdeglobals', '~/.kde/share/config/kdeglobals')
        self.copy_file('./fonts.conf', '~/.config/fontconfig/')
        self.delete_file('~/.fonts.conf')
#        self.create_symlink('~/.config/fontconfig/fonts.conf', '~/.fonts.conf')  # in 12.04 only this works

    def override_font(self, font, override):
        """Add necessary nodes to fonts.conf """
        raise NotImplemented
