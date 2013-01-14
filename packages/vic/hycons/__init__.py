from mykde import Action


class Action(Action):

    name = "Hycons icons"
    description = """\
<a href="http://kde-look.org/content/show.php/?content=101767">Hycons icons</a><br>
<br>
<img src="screenshot.png"/>
"""
    packages = ['qtcurve', 'fonts-droid']

    def proceed(self):
        self.copy_file('./Hycons', '~/.kde/share/icons/')
        self.update_kconfig('./kdeglobals', '~/.kde/share/config/kdeglobals')
