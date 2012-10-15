class ActionMeta(type):

    def __lt__(self, other):
        return id(self) < id(other)

    def __eq__(self, other):
        return id(self) == id(other)


class Action(metaclass=ActionMeta):

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


class ActionSet():
    "Action set properties: description"
    name = ''
    description = ''
    actions = []  # list of action names contained in this action set 


class ActionPackage():
    "Action package properties: desription, author, etc."
    author = ''
    version = 0
    description = ''
