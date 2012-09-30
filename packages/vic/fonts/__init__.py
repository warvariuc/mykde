"Custom fonts"
install_package('fonts-droid')
update_config('./kdeglobals', '~/.kde/share/config/kdeglobals')
request_config_reload()
cp('./fonts.conf', '~/.config/fontconfig/')
"""
If a font in the browser in not Dorid, in Google Chrome right click on the text with the worng font,
select 'Inspect element', find 'Computed style' and 'font-family' in it:

font-family: 'lucida grande', tahoma, verdana, arial, sans-serif;

And for each font do 'fc=match':

vic@wic:~/Documents$ fc-match Helvetica
LiberationSans-Regular.ttf: "Liberation Sans" "Regular"

Ok, you found the offending font. Add it to 'fonts.conf' file.
"""
def override_font(font, override):
    """Add necessary nodes to fonts.conf """