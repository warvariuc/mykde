import mykde


class Action(mykde.BaseAction):

    name = 'Double Commander'
    description = """\
Double Commander is a cross platform open source file manager with two panels side by side.
It is inspired by Total Commander and features some new ideas."""
    packages = ['doublecmd-qt', 'meld', 'kwrite', 'fonts-droid']

    def proceed(self):
        self.update_xmlconfig(
            './doublecmd.xml',
            '~/.config/doublecmd/doublecmd.xml',
            './doublecmd.xml')
