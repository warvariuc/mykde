
class Action():

    name = None
    description = \
        """
        HTML description of the action
        """

    def install_package(self):
        """
        apt-get install a package
        """

    def update_kconfig(self):
        """
        Update a configuration file which is in format of kconfig
        """

    def copy_file(self, src, dst):
        """
        Copy a file
        """