#!/usr/bin/env python3

__author__ = "Victor Varvariuc <victor.varvariuc@gmail.com>"

import sys
python_required_version = '3.2' # tested with this version or later
if sys.version < python_required_version:
    raise SystemExit('Python %s or newer required (you are using: %s).' %
                     (python_required_version, sys.version))


import os
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
    @param object_path: path to an object
    @param package_path: if objectPath is relative or only object name in it is given, package_path
        should be given.
    """
    module_path, sep, object_name = object_path.rpartition('.')
    if not sep: # '.' not present - only object name is given in the path
        assert package_path, "You've given the object name, but haven't specified the module " \
            "in which i can find it. " + object_path
        (object_name, module_path, package_path) = (object_path, package_path, None)
    module = importlib.import_module(module_path, package_path)
    return getattr(module, object_name)


def iter_action_classes(module):
    """
    Return an iterator over all Action subclasses defined in the given module
    """
    for obj in vars(module).values():
        if isinstance(obj, type) and issubclass(obj, Action) and obj.__module__ == module.__name__:
            yield obj



main_window = uic.loadUi(os.path.join(cur_dir, 'scripts', 'main_window.ui'))
#webview.init(mainWindow.webView)



action_list_widget = main_window.action_list


def handle_package_combo_activated(index):
    main_window.action_list.clear()

    package_path = main_window.package_combo.itemData(index)
    for module in walk_modules(package_path):
        for action_class in iter_action_classes(module):
            item = QtGui.QListWidgetItem(action_class.name)
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable |
                          QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Checked)
            item.setToolTip(action_class.description)
#            item.setStatusTip(action_class.description)
            action_list_widget.addItem(item)

    main_window.action_set_combo.clear()
    # default action sets
    main_window.action_set_combo.addItem('All',
                                         [QtCore.Qt.Checked] * action_list_widget.count())
    main_window.action_set_combo.addItem('None',
                                         [QtCore.Qt.Unchecked] * action_list_widget.count())
    main_window.action_set_combo.addItem('Custom', None)
    
    main_window.action_set_combo.activated.emit(main_window.package_combo.currentIndex())


def handle_action_set_combo_activated(index):
    action_set = main_window.action_set_combo.itemData(index)
    if action_set is not None:
        for index in range(action_list_widget.count()):
            action_list_widget.item(index).setCheckState(action_set[index])

def handle_action_list_item_changed(item):
    action_set = []
    for index in range(action_list_widget.count()):
        action_set.append(action_list_widget.item(index).checkState())
    for index in range(main_window.action_set_combo.count()):
        if action_set == main_window.action_set_combo.itemData(index):
            break
    main_window.action_set_combo.setCurrentIndex(index)


main_window.package_combo.activated[int].connect(handle_package_combo_activated)
main_window.action_set_combo.activated[int].connect(handle_action_set_combo_activated)
main_window.action_list.itemChanged.connect(handle_action_list_item_changed)
#main_window.proceed_button.clicked.connect(lambda: install.install(unicode(mainWindow.themesComboBox.currentText())))
main_window.proceed_button.setFocus(True)

for _, module_name, _ in iter_modules(['packages']):
    main_window.package_combo.addItem(module_name, 'packages.' + module_name)
main_window.package_combo.activated.emit(0)

main_window.show()
app.exec()
