__author__ = "Victor Varvariuc <victor.varvariuc@gmail.com>"

import os
import sys
import importlib
import html

from pkgutil import iter_modules
from PyQt4 import QtCore, QtGui, uic
from PyKDE4 import kdecore

from . import ActionSet, BaseAction
from . import signals


def walk_modules(path):
    """Loads a module and all its submodules from a the given module path and returns them.
    If *any* module throws an exception while importing, that exception is thrown back.
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


def iter_classes(module, klass):
    """Return an iterator over all klass subclasses defined in the given module.
    """
    for obj in vars(module).values():
        if isinstance(obj, type) and issubclass(obj, klass) and obj.__module__ == module.__name__:
            yield obj


BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
os.chdir(BASE_DIR)

FormClass, BaseClass = uic.loadUiType(os.path.join(BASE_DIR, 'mykde', 'main_window.ui'))
assert BaseClass is QtGui.QMainWindow


class MainWindow(QtGui.QMainWindow, FormClass):

    def __init__(self):
        super().__init__()
        # uic adds a function to our class called setupUi
        # calling this creates all the widgets from the .ui file
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('mykde/icon.png'))
        # open URL in the default KDE browser
        self.textBrowser.setOpenExternalLinks(True)
        self.print_html('<h3 style="color:#268BD2">Welcome to the KDE transformer!</h3>')
        self.print_text('You are using KDE %s\n' % kdecore.versionString())

    @QtCore.pyqtSlot(str)
    def on_textBrowser_highlighted(self, url):
        # show link URL in the status bar when cursor is over it
        self.statusBar().showMessage(url)

    def _print_html(self, text):
        text_browser = self.textBrowser
        cursor = text_browser.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        text_browser.setTextCursor(cursor)
        text_browser.insertHtml(text)
        text_browser.ensureCursorVisible()  # scroll to the new message
        QtGui.QApplication.processEvents()

    def print_text(self, text, end='\n'):
        self._print_html(html.escape(text + end).replace('\n', '<br>'))

    def print_html(self, text, end='<br>'):
        self._print_html(text + end)

    @QtCore.pyqtSlot()
    def on_aboutButton_clicked(self):
        self.print_html("""
<hr><h3 style="color:#268BD2">
"My KDE" transformer. Author Victor Varvariuc.<br>
<a href="https://github.com/warvariuc/mykde">Project page here.</a>
</h3><hr>
""")

    @QtCore.pyqtSlot()
    def on_proceedButton_clicked(self):
        actions = []
        packages = []
        repositories = {}  # repositories to add
        for index in range(self.actionList.count()):
            action_item = self.actionList.item(index)
            if action_item.checkState() == QtCore.Qt.Checked:
                action_class = action_item.data(QtCore.Qt.UserRole)
                actions.append(action_class(self))
                packages.extend(action_class.packages)
                repositories.update(action_class.repositories)
        # add new repositories
        res = actions[0].install_repositories(repositories)
        if not res:
            self.print_html('<b style="color:red">Not all repositories installed. '
                            'Not proceeding further.</b>')
            return
        # install missing packages
        res = actions[0].install_packages(packages)
        if not res:
            self.print_html('<b style="color:red">Not all packages installed. '
                            'Not proceeding further.</b>')
            return
        # perform the actions
        for action in actions:
            self.print_html('Performing action <b>"%s"</b>' % action.name)
            try:
                action.proceed()
            except Exception as exc:
                self.print_html('<span style="color:red"><b>Error:</b> %s</span>' % exc)
            else:
                self.print_html('Finished action <b style="color:green">"%s"</b>'
                                % action.name)

        signals.action_set_proceeded.send(self, actions=actions)

        self.print_html(
            '<b style="background-color:green;color:white">Finished package installation.<br>'
            'Some effects could be seen only after you restart your KDE session.</b>')

    @QtCore.pyqtSlot(int)
    def on_packageCombo_activated(self, index):
        self.actionList.clear()

        package_path = self.packageCombo.itemData(index)
        all_actions = []
        for module in walk_modules(package_path):
            for action in iter_classes(module, BaseAction):
                item = QtGui.QListWidgetItem(action.name)
                all_actions.append(action)
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable
                              | QtCore.Qt.ItemIsEnabled)
                item.setCheckState(QtCore.Qt.Checked)
                item.setData(QtCore.Qt.UserRole, action)
                self.actionList.addItem(item)

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
        if action_set.actions is not None:  # not Custom
            for index in range(self.actionList.count()):
                item = self.actionList.item(index)
                action = item.data(QtCore.Qt.UserRole)
                check_state = (QtCore.Qt.Checked if action in action_set.actions else
                               QtCore.Qt.Unchecked)
                item.setCheckState(check_state)
        self.actionList.setCurrentItem(None)  # reset selection

    def on_actionList_itemChanged(self, item):
        """Item checked/unchecked.
        """
        checked_actions = []
        for index in range(self.actionList.count()):
            action_item = self.actionList.item(index)
            if action_item.checkState() == QtCore.Qt.Checked:
                action = action_item.data(QtCore.Qt.UserRole)
                checked_actions.append(action)
        checked_actions.sort()
        index = -1
        for index in range(self.actionSetCombo.count()):
            if self.actionSetCombo.itemData(index).actions == checked_actions:
                break
        self.actionSetCombo.setCurrentIndex(index)

    def on_actionList_doubleClicked(self, modelIndex):
        """Item double-clicked.
        """
        for index in range(self.actionList.count()):
            action_item = self.actionList.item(index)
            check_state = QtCore.Qt.Checked if index == modelIndex.row() else QtCore.Qt.Unchecked
            action_item.setCheckState(check_state)

    def on_actionList_currentRowChanged(self, index):
        if index == -1:  # no row is selected
            return
        item = self.actionList.item(index)
        action = item.data(QtCore.Qt.UserRole)
        self.print_html('About action &quot;<b>%s</b>&quot;:<blockquote>%s</blockquote>'
                        % (action.name, action.description.strip()))


class NoneActionSet(ActionSet):
    name = 'None'
    description = 'No actions'
    actions = []


class CustomActionSet(ActionSet):
    name = 'Custom'
    description = 'Customly selected set'
    actions = None


def main(package_module):

    app = QtGui.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.proceedButton.setFocus(True)

    package_module_name = package_module.__name__
    for _, module_name, _ in iter_modules([package_module_name]):
        main_window.packageCombo.addItem(module_name, package_module_name + '.' + module_name)

    if main_window.packageCombo.count():
        main_window.packageCombo.activated.emit(0)

    main_window.show()
    app.exec()
