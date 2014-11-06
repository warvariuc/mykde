import mykde


class Action(mykde.BaseAction):

    name = 'LibreOffice'
    description = "LibreOffice with custom settings"
    packages = ['libreoffice', 'libreoffice-style-galaxy']

    def proceed(self):
        self.update_xmlconfig(
            './registrymodifications.xcu',
            '~/.config/libreoffice/4/user/registrymodifications.xcu',
            './registrymodifications.xcu')
