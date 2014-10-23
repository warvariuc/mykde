__version__ = '1.1.0'
__author__ = 'Victor Varvariuc<victor.varvariuc@gmail.com>'


def get_object_path(obj):
    """Having an object return path to its class in form of `path.to.module.ClassName`
    """
    if isinstance(obj, type):
        suffix = ''
    else:
        suffix = '()'
        obj = obj.__class__
    module_path = '' if obj.__module__ == 'builtins' else obj.__module__ + '.'
    return module_path + obj.__name__ + suffix


def get_object_by_path(object_path, package_path=None):
    """Given the path in form 'some.module.object' return the object.

    Args:
        object_path (str): path to an object
        package_path (str): if object_path is relative or only object name in it is given,
            package_path should be given.
    """
    module_path, sep, object_name = object_path.rpartition('.')
    if not sep:  # '.' not present - only object name is given in the path
        assert package_path, "You've given the object name, but haven't specified the module in ' \
            'which i can find it: %s" % object_path
        object_name, module_path, package_path = object_path, package_path, None
    module = importlib.import_module(module_path, package_path)
    return getattr(module, object_name)


def dump_args(func):
    """Decorator to print function call details - parameter names and passed/effective values.
    """
    def wrapper(*func_args, **func_kwargs):

        arg_names = func.func_code.co_varnames[:func.func_code.co_argcount]
        args = func_args[:len(arg_names)]
        if func.func_defaults:
            args = args + func.func_defaults[len(func.func_defaults) - func.func_code.co_argcount + len(args):]
        params = list(zip(arg_names, args))
        args = func_args[len(arg_names):]
        if args:
            params.append(('*', args))
        if func_kwargs:
            params.append(('**', func_kwargs))
        print('{} ( {} )'.format(func.func_name, ', '.join(map('{0[0]!s} = {0[1]!r}'.format, params))))

        return func(*func_args, **func_kwargs)

    return wrapper


from .base import *
from .main import *

# disable PyQt input hook in order for ipdb to work
QtCore.pyqtRemoveInputHook()
