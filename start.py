#!/usr/bin/env python3

__author__ = "Victor Varvariuc <victor.varvariuc@gmail.com>"

import sys
pythonRequiredVersion = '3.2' # tested with this version or later
if sys.version < pythonRequiredVersion:
    raise SystemExit('Python %s or newer required (you are using: %s).' % (pythonRequiredVersion, sys.version))


import os
from random import randint
from PyQt4 import QtCore, QtGui, uic
#from scripts import main

cur_dir = os.path.dirname(os.path.abspath(__file__))

app = QtGui.QApplication(sys.argv)

if os.geteuid() == 0: # root privileges
    QtGui.QMessageBox.warning(None, 'Root detected', 'Do not run this script as root.\n'\
            'Run it as the user in whose session you want to install themes.')
    sys.exit()


import importlib
from pkgutil import iter_modules
from packages import Action


def walk_modules(path):
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
    """
    Given the path in form 'some.module.object' return the object.
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
    for obj in vars(module).values():
        if isinstance(obj, type) and issubclass(obj, Action) and obj.__module__ == module.__name__:
            yield obj



main_window = uic.loadUi(os.path.join(cur_dir, 'scripts', 'main_window.ui'))
#webview.init(mainWindow.webView)

#mainWindow.themesComboBox.activated[str].connect(lambda text: webview.loadPage(text))
#mainWindow.closePushButton.clicked.connect(mainWindow.close)
#mainWindow.installPushButton.clicked.connect(lambda: install.install(unicode(mainWindow.themesComboBox.currentText())))
#mainWindow.installPushButton.setFocus(True)

action_list_widget = main_window.action_list

for module in walk_modules('packages'):
    for action_class in iter_action_classes(module):
        item = QtGui.QListWidgetItem(action_class.name)
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
#        check = QtCore.Qt.Checked if randint(0, 1) == 1 else QtCore.Qt.Unchecked
        item.setCheckState(QtCore.Qt.Checked)
        item.setToolTip(action_class.description)
        action_list_widget.insertItem(0, item)

main_window.action_set_combo.addItem('All')
main_window.action_set_combo.addItem('None')

main_window.show()
app.exec()
