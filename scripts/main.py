__author__ = "Victor Varvariuc <victor.varvariuc@gmail.com>"

import os, sys

from PyQt4 import QtGui, uic

from . import webview, install


def dump_args(func):
    """Decorator to print function call details - parameter names and passed/effective values.
    """
    
    def wrapper(*func_args, **func_kwargs):

        arg_names = func.func_code.co_varnames[:func.func_code.co_argcount]
        args = func_args[:len(arg_names)]
        if func.func_defaults:
            args = args + func.func_defaults[len(func.func_defaults) - func.func_code.co_argcount + len(args):]
        params = zip(arg_names, args)
        args = func_args[len(arg_names):]
        if args:
            params.append(('*', args))
        if func_kwargs:
            params.append(('**', func_kwargs))
        print('{} ( {} )'.format(func.func_name, ', '.join(map('{0[0]!s} = {0[1]!r}'.format, params))))

        return func(*func_args, **func_kwargs)

    return wrapper
