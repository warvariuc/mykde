from scripts import Action


class Action(Action):

    name = "Skype"
    description = "Skype"
    
    packages = ['skype', 'pavucontrol']

    def proceed(self):
        self.install_trusted_key('https://dl-ssl.google.com/linux/linux_signing_key.pub') # 'wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -'
        self.add_repo('http://dl.google.com/linux/chrome/deb/ stable main', 'google.list')# """sudo sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'"""
        self.update_package_index() # 'sudo apt-get update'
