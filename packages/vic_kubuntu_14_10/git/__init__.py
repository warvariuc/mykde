import os.path

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

        # global .gitignore
        self.print_text('Checking current global `gitignore` file...')
        retcode, output = self.call('git config --get core.excludesfile')
        if retcode:
            self.print_text('Failed')
        else:
            file_path = self.make_abs_path('\n'.join(output).strip())
            if os.path.exists(file_path):
                self.print_text('There is existing global `gitignore` file: %s' % file_path)
                self.print_text('Not replacing it')
            else:
                self.copy_file('./.gitignore_global', '~/')
                self.call('git config --global core.excludesfile "~/.gitignore_global"')
