import os.path

from scripts import Action


class Action(Action):

    name = "Bash"
    description = "Custom prompt, colors. Install emacs"

    packages = ['most', 'emacs23-nox']

    def update_text(self, file_path, text):
        with open(file_path) as file_handler:
            file_content = file_handler.read()
        if text in file_content:
            # text already present
            return
        with open(file_path, 'a') as file_handler:
            if not file_content.endswith('\n'):
                file_handler.write('\n')
            file_handler.write('%s\n' % text)

    def proceed(self):
        bashrc_path = os.path.expanduser('~/.bashrc')

        # set color prompt
        self.update_text(bashrc_path, r"""
# enable color prompt with git and virtualenv marks
blackf=$(tput setaf 0)
green=$(tput setaf 2)
blue=$(tput setaf 4)
bold=$(tput bold)
red=$(tput setaf 1)
yellow=$(tput setaf 3)
und=$(tput sgr 0 1)
reset=$(tput sgr0)
PS1='${debian_chroot:+($debian_chroot)}\[\[$bold$green\]\u@:\[$blue\]\w\[$yellow\]$(__git_ps1)\[$reset\] \$ '
""")
        # Configure 'most' to handle man pages
        self.update_text(bashrc_path, 'export MANPAGER="/usr/bin/most -s"')
        # set emacs as the default editor
        self.update_text(bashrc_path, 'export EDITOR=emacs')
        # show git branch name with dirty state mark
        self.update_text(bashrc_path, 'export GIT_PS1_SHOWDIRTYSTATE=true')
