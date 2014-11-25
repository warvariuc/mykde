import mykde


class Action(mykde.BaseAction):

    name = 'Emacs'
    description = """\
Emacs-no-X in <a href="http://www.emacswiki.org/CuaMode">Cua-mode</a>
"""
    packages = ['emacs24-nox']

    def proceed(self):
        self.copy_file('./.emacs', '~/')
