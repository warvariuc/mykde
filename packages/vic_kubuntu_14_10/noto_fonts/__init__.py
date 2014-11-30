import mykde


class Action(mykde.BaseAction):

    name = 'Noto fonts'
    description = """
<a href="https://www.google.com/get/noto/">Noto</a> is Google’s font family that aims to support 
all the world’s languages. Its design goal is to achieve visual harmonization across languages.
"""

    packages = ['fonts-noto', 'fonts-liberation']
    affects = [mykde.KdeSettings]

    def proceed(self):
        self.update_kconfig('./kdeglobals', '~/.kde/share/config/kdeglobals')
        self.copy_file('./fonts.conf', '~/.config/fontconfig/')
