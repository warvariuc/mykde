from packages import Action

"""
If a font in the browser in not Droid, in Google Chrome right click on the text with the worng font,
select 'Inspect element', find 'Computed style' and 'font-family' in it:

font-family: 'lucida grande', tahoma, verdana, arial, sans-serif;

And for each font do 'fc=match':

vic@wic:~/Documents$ fc-match Helvetica
LiberationSans-Regular.ttf: "Liberation Sans" "Regular"

Ok, you found the offending font. Add it to 'fonts.conf' file.
"""

class Action(Action):
    
    name = 'Droid fonts everywhere'
    
    html_description = "Custom fonts"
    
    def proceed(self):
        self.install_package('fonts-droid')
        self.update_kconfig('./kdeglobals', '~/.kde/share/config/kdeglobals')
        self.request_kconfig_reload()
        self.cp('./fonts.conf', '~/.config/fontconfig/')
        self.delete_file('~/.fonts.conf')  # or patch and then move it to:
        self.copy_file('./fonts.conf', '~/.config/fontconfig/')
        self.copy_file('./fonts.conf', '~/.fonts.conf')  # in 12.04 only this works

    def override_font(self, font, override):
        """Add necessary nodes to fonts.conf """

