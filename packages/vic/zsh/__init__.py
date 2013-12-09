from mykde import BaseAction


class Action(BaseAction):

    name = 'Zsh'
    description = "Zsh with oh-my-zsh"
    packages = ['git', 'zsh', 'most']

    def proceed(self):
        self.copy_file('./.zshrc', '~/')
        self.call('git clone git://github.com/robbyrussell/oh-my-zsh.git ~/.oh-my-zsh')
        self.kdesudo('chsh -s $(which zsh) $USER', 'Confirm user shell change')
