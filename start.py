#!/usr/bin/env python3

__author__ = "Victor Varvariuc <victor.varvariuc@gmail.com>"

import os
import sys

python_required_version = '3.2' # tested with this version or later
if sys.version < python_required_version:
    raise SystemExit('Python %s or newer required (you are using: %s).' %
                     (python_required_version, sys.version))

import subprocess
from PyQt4 import QtCore, QtGui

app = QtGui.QApplication(sys.argv)

def error(title, message):
    def show_error():
        QtGui.QMessageBox.critical(None, title, message)
        QtGui.QApplication.quit()
    QtCore.QTimer.singleShot(0, show_error)
    app.exec()
    sys.exit(1)

if os.geteuid() == 0:  # root privileges
    error('Root detected', 'Do not run this script as root.\n'
          'Run it as the user in whose session you want to proceed with the actions.')

# the distributor's ID
distro_id = subprocess.check_output(['lsb_release', '--short', '--id'])
distro_id = distro_id.decode().strip().lower()
if distro_id != 'ubuntu':
    error('Wrong distro', 'Ubuntu not found:\n%s.' % distro_id)

# the release number of the currently installed distribution
distro_release_id = subprocess.check_output(['lsb_release', '--short', '--release'])
distro_release_id = distro_release_id.decode().strip()
if distro_id < '12.10':
    error('Wrong release', 'Need Ubuntu 12.10 or younger.')


from PyQt4 import uic
from scripts import webview, ActionSet

cur_dir = os.path.dirname(os.path.abspath(__file__))



import importlib
from pkgutil import iter_modules
from scripts import Action


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


def iter_classes(module, klass):
    """
    Return an iterator over all klass subclasses defined in the given module
    """
    for obj in vars(module).values():
        if isinstance(obj, type) and issubclass(obj, klass) and obj.__module__ == module.__name__:
            yield obj


main_window = uic.loadUi(os.path.join(cur_dir, 'scripts', 'main_window.ui'))
#webview.init(mainWindow.webView)

action_list_widget = main_window.action_list


class NoneActionSet(ActionSet):
    name = 'None'
    description = 'No actions'
    actions = []


class CustomActionSet(ActionSet):
    name = 'Custom'
    description = 'Customly selected set'
    actions = None


def on_package_combo_activated(index):
    main_window.action_list.clear()

    package_path = main_window.package_combo.itemData(index)
    all_actions = []
    for module in walk_modules(package_path):
        for action in iter_classes(module, Action):
            item = QtGui.QListWidgetItem(action.name)
            all_actions.append(action)
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable |
                          QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Checked)
            item.setToolTip(action.description)
#            item.setStatusTip(action.description)
            item.setData(QtCore.Qt.UserRole, action)
            action_list_widget.addItem(item)

    main_window.action_set_combo.clear()

    class AllActionSet(ActionSet):
        name = 'All'
        description = 'All available actions'
        actions = all_actions

    # default action sets
    action_sets = [AllActionSet, NoneActionSet]
    for action_set in iter_classes(importlib.import_module(package_path), ActionSet):
        action_sets.append(action_set)
    action_sets.append(CustomActionSet)  # at the end
    for action_set in action_sets:
        if action_set.actions is not None:
            action_set.actions.sort()
        main_window.action_set_combo.addItem(action_set.name, action_set)
    main_window.action_set_combo.activated.emit(0)


def on_action_set_combo_activated(index):
    action_set = main_window.action_set_combo.itemData(index)
    main_window.web_view.setHtml(main_window.action_set_combo.itemText(index))
    if action_set.actions is not None:  # not Custom
        for index in range(action_list_widget.count()):
            item = action_list_widget.item(index)
            action = item.data(QtCore.Qt.UserRole)
            check_state = QtCore.Qt.Checked if action in action_set.actions else QtCore.Qt.Unchecked
            item.setCheckState(check_state)
    action_list_widget.setCurrentItem(None)  # reset selection


def on_action_list_item_changed(item):
    "Item checked/unchecked"
    checked_actions = []
    for index in range(action_list_widget.count()):
        action_item = action_list_widget.item(index)
        if action_item.checkState() == QtCore.Qt.Checked:
            action = action_item.data(QtCore.Qt.UserRole)
            checked_actions.append(action)
    checked_actions.sort()
    for index in range(main_window.action_set_combo.count()):
        if main_window.action_set_combo.itemData(index).actions == checked_actions:
            break
    main_window.action_set_combo.setCurrentIndex(index)


def on_action_list_current_row_changed(index):
    if index == -1:  # no row is selected
        return
    item = action_list_widget.item(index)
    action = item.data(QtCore.Qt.UserRole)
    main_window.web_view.setHtml(action.description)


def on_proceed_button_clicked(checked=False):
    actions = []
    packages_to_install = []
    for index in range(action_list_widget.count()):
        action_item = action_list_widget.item(index)
        if action_item.checkState() == QtCore.Qt.Checked:
            action_class = action_item.data(QtCore.Qt.UserRole)
            actions.append(action_class(main_window))
            packages_to_install.extend(action_class.packages)
    actions[0].install_packages(packages_to_install)



main_window.package_combo.activated[int].connect(on_package_combo_activated)
main_window.action_set_combo.activated[int].connect(on_action_set_combo_activated)
main_window.action_list.itemChanged.connect(on_action_list_item_changed)
main_window.action_list.currentRowChanged.connect(on_action_list_current_row_changed)
main_window.proceed_button.clicked[bool].connect(on_proceed_button_clicked)
main_window.proceed_button.setFocus(True)

for _, module_name, _ in iter_modules(['packages']):
    main_window.package_combo.addItem(module_name, 'packages.' + module_name)
main_window.package_combo.activated.emit(0)

main_window.show()
app.exec()
