__author__ = "Victor Varvariuc <victor.varvariuc@gmail.com>"

import os
import sys


base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
os.chdir(base_dir)


import importlib
import html

from pkgutil import iter_modules
from PyQt4 import QtCore, QtGui, uic

from . import ActionSet, Action


app = QtGui.QApplication(sys.argv)


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


def get_object_by_path(object_path, package_path=None):
    """
    Given the path in form 'some.module.object' return the object.
    @param object_path: path to an object
    @param package_path: if objectPath is relative or only object name in it is given, package_path
        should be given.
    """
    module_path, sep, object_name = object_path.rpartition('.')
    if not sep:  # '.' not present - only object name is given in the path
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


FormClass, BaseClass = uic.loadUiType(
    os.path.join(base_dir, 'mykde', 'main_window.ui')
)
assert BaseClass is QtGui.QMainWindow


class MainWindow(QtGui.QMainWindow, FormClass):

    def __init__(self):
        super().__init__()
        # uic adds a function to our class called setupUi
        # calling this creates all the widgets from the .ui file
        self.setupUi(self)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.setWindowIcon(QtGui.QIcon('scripts/icon.png'))
        # open URL in the default KDE browser
        self.textBrowser.setOpenExternalLinks(True)
        self.print_message('<><h3 style="color:blue">Welcome to the KDE transformer!</h3>')

    @QtCore.pyqtSlot(str)
    def on_textBrowser_highlighted(self, url):
        # show link URL in the status bar when cursor is over it
        self.statusBar().showMessage(url)

    def print_message(self, message, end='\n'):
        text_browser = self.textBrowser
        cursor = text_browser.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        text_browser.setTextCursor(cursor)
        if not message.startswith('<>'):
            message = html.escape(message + end).replace('\n', '<br>')
        else:
            if end == '\n':
                end = '<br>'
            message += end
        text_browser.insertHtml(message)
        text_browser.ensureCursorVisible()  # scroll to the new message
        QtGui.QApplication.processEvents()

    @QtCore.pyqtSlot()
    def on_aboutButton_clicked(self):
        self.print_message("""<>\
<hr><div style="background-color:green;color:white;font:bold large">
"My KDE" transformer. Author Victor Varvariuc.<br>
<a href="https://github.com/warvariuc/mykde" style="color:white">Program page here.</a>
</div><hr>
""")

    @QtCore.pyqtSlot()
    def on_proceedButton_clicked(self):
        actions = []
        packages = []
        repositories = {}  # repositories to add
        for index in range(main_window.actionList.count()):
            action_item = main_window.actionList.item(index)
            if action_item.checkState() == QtCore.Qt.Checked:
                action_class = action_item.data(QtCore.Qt.UserRole)
                actions.append(action_class(self))
                packages.extend(action_class.packages)
                repositories.update(action_class.repositories)
        # add new repositories
        res = actions[0].install_repositories(repositories)
        if not res:
            self.print_message('<><b style="color:red">Not all repositories installed. '
                               'Not proceeding further.</b>')
            return
        # install missing packages
        res = actions[0].install_packages(packages)
        if not res:
            self.print_message('<><b style="color:red">Not all packages installed. '
                               'Not proceeding further.</b>')
            return
        # perform the actions
        for action in actions:
            self.print_message('<>Performing action <b>"%s"</b>' % action.name)
            try:
                action.proceed()
            except Exception as exc:
                self.print_message('<><span style="color:red"><b>Error:</b> %s</span>' % exc)
            else:
                self.print_message('<>Finished action <b style="color:green">"%s"</b>'
                                   % action.name)

        # reload KDE configuration
        actions[0].request_kde_reload_config()
        self.print_message(
            '<><b style="background-color:green;color:white">Finished package installation.<br>'
            'Some effects could be seen only after you restart your KDE session.</b>'
        )

    @QtCore.pyqtSlot(int)
    def on_packageCombo_activated(self, index):
        self.actionList.clear()

        package_path = self.packageCombo.itemData(index)
        all_actions = []
        for module in walk_modules(package_path):
            for action in iter_classes(module, Action):
                item = QtGui.QListWidgetItem(action.name)
                all_actions.append(action)
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable
                              | QtCore.Qt.ItemIsEnabled)
                item.setCheckState(QtCore.Qt.Checked)
                item.setToolTip('<div>' + action.description + '</div>')
    #            item.setStatusTip(action.description)
                item.setData(QtCore.Qt.UserRole, action)
                main_window.actionList.addItem(item)

        self.actionSetCombo.clear()

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
            self.actionSetCombo.addItem(action_set.name, action_set)
        self.actionSetCombo.activated.emit(0)


    @QtCore.pyqtSlot(int)
    def on_actionSetCombo_activated(self, index):
        action_set = self.actionSetCombo.itemData(index)
        self.print_message('<>Action set <b>"%s"</b> was selected.' % action_set.name)
    #    main_window.web_view.setHtml(main_window.actionSetCombo.itemText(index))
        if action_set.actions is not None:  # not Custom
            for index in range(main_window.actionList.count()):
                item = main_window.actionList.item(index)
                action = item.data(QtCore.Qt.UserRole)
                check_state = QtCore.Qt.Checked if action in action_set.actions else QtCore.Qt.Unchecked
                item.setCheckState(check_state)
        main_window.actionList.setCurrentItem(None)  # reset selection

    def on_actionList_itemChanged(self, item):
        """Item checked/unchecked.
        """
        check_text = 'Checked' if item.checkState() == QtCore.Qt.Checked else 'Unchecked'
        action = item.data(QtCore.Qt.UserRole)
        self.print_message('<>%s action <b>"%s"</b>' % (check_text, action.name))

        checked_actions = []
        for index in range(main_window.actionList.count()):
            action_item = main_window.actionList.item(index)
            if action_item.checkState() == QtCore.Qt.Checked:
                action = action_item.data(QtCore.Qt.UserRole)
                checked_actions.append(action)
        checked_actions.sort()
        for index in range(self.actionSetCombo.count()):
            if self.actionSetCombo.itemData(index).actions == checked_actions:
                break
        self.actionSetCombo.setCurrentIndex(index)

    def on_actionList_currentRowChanged(self, index):
        if index == -1:  # no row is selected
            return
        item = main_window.actionList.item(index)
        action = item.data(QtCore.Qt.UserRole)
        self.print_message('<>About action <b>%s</b>:<blockquote>%s</blockquote>'
                           % (action.name, action.description))


class NoneActionSet(ActionSet):
    name = 'None'
    description = 'No actions'
    actions = []


class CustomActionSet(ActionSet):
    name = 'Custom'
    description = 'Customly selected set'
    actions = None


main_window = MainWindow()
main_window.proceedButton.setFocus(True)

for _, module_name, _ in iter_modules(['packages']):
    main_window.packageCombo.addItem(module_name, 'packages.' + module_name)

if main_window.packageCombo.count():
    main_window.packageCombo.activated.emit(0)

main_window.show()
app.exec()