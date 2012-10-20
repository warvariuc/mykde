from scripts import Action


class Action(Action):

    name = 'git'
    description = "Git with helper programs and cusotm settings"

    packages = ['git', 'gitk', 'giggle']

    def proceed(self):
        # push only current branch
        self.call('git config --global push.default current')
        # colorize UI
        self.call('git config --global color.ui true')
        # useful aliases
        self.call('git config --global alias.ci "commit -a"')
        self.call('git config --global alias.co checkout')
        self.call('git config --global alias.st status')
        self.call('git config --global alias.br branch')
