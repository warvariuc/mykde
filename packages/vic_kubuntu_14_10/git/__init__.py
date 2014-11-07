import mykde


class Action(mykde.BaseAction):

    name = 'Git'
    description = "Git with helper programs and custom settings"

    packages = ['git', 'gitk', 'giggle']

    def proceed(self):
        # useful aliases
        self.call('git config --global alias.ci "commit -a"')
        self.call('git config --global alias.co checkout')
        self.call('git config --global alias.st status')
        self.call('git config --global alias.br branch')
        # push only current branch
        self.call('git config --global push.default current')
        # colorize UI
        self.call('git config --global color.ui true')
        # do not call pager for content less than one page
        self.call('git config --global --add core.pager "less -F -X"')
