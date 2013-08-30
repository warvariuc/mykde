from mykde import BaseAction


class Action(BaseAction):

    name = 'Zsh'
    description = "Zsh with oh-my-zsh"
    packages = ['git', 'zsh']

    def proceed(self):
        self.copy_file('./.zshrc', '~/')
        # TODO: set zsh as default shell: chsh -s $(which zsh)
