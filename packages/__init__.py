import importlib
from pkgutil import iter_modules


def walk_modules(path, load = False):
    """Loads a module and all its submodules from a the given module path and
    returns them. If *any* module throws an exception while importing, that
    exception is thrown back.

    For example: walk_modules('scrapy.utils')
    """

    modules = []
    module = __import__(path, {}, {}, [''])
    modules.append(module)
    if hasattr(module, '__path__'):  # is a package
        for _, subpath, ispkg in iter_modules(module.__path__):
            fullpath = path + '.' + subpath
            if ispkg:
                modules += walk_modules(fullpath)
            else:
                submod = __import__(fullpath, {}, {}, [''])
                modules.append(submod)
    return modules


def get_object_by_path(object_path, package_path = None):
    """Given the path in form 'some.module.object' return the object.
    @param objectPath: path to an object
    @param packagePath: if objectPath is relative or only object name in it is given, packagePath
        should be given.
    """
    modulePath, sep, objectName = object_path.rpartition('.')
    if not sep: # '.' not present - only object name is given in the path
        assert package_path, "You've given the object name, but haven't specified the module " \
            "in which i can find it. " + object_path
        (objectName, modulePath, packagePath) = (object_path, package_path, None)
    module = importlib.import_module(modulePath, packagePath)
    return getattr(module, objectName)


def iter_action_classes(module):
    """
    Return an iterator over all Action subclasses defined in the given module
    """
    for obj in vars(module).itervalues():
        if isinstance(obj, type) and issubclass(obj, Action) and obj.__module__ == module.__name__:
            yield obj


class Action():

    def html_description(self):
        """
        Return HTML description of the action
        """
        return ''

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
