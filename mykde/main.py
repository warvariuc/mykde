__author__ = "Victor Varvariuc <victor.varvariuc@gmail.com>"

import os
import sys
import importlib
import html

from pkgutil import iter_modules
from PyQt4 import QtCore, QtGui, uic
from PyKDE4 import kdecore

import mykde


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
        self.setWindowIcon(QtGui.QIcon('mykde/icon_kde.svg'))
        # open URL in the default KDE browser
        self.textBrowser.setOpenExternalLinks(True)
        self.print_html('<h3 style="color:#268BD2">Welcome to the KDE transformer!</h3>')
        self.print_text('You are using KDE %s\n' % kdecore.versionString())

    @QtCore.pyqtSlot(str)
    def on_textBrowser_highlighted(self, url):
        # show link URL in the status bar when mouse cursor is over it
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
        for index in range(self.actionList.count()):
            action_item = self.actionList.item(index)
            if action_item.checkState() == QtCore.Qt.Checked:
                action_class = action_item.data(QtCore.Qt.UserRole)
                actions.append(action_class)

        mykde.run_action_set(self, actions)

    @QtCore.pyqtSlot(int)
    def on_packageCombo_activated(self, index):
        self.actionList.clear()

        package_path = self.packageCombo.itemData(index)
        all_actions = []
        for module in walk_modules(package_path):
            for action in iter_classes(module, mykde.BaseAction):
                item = QtGui.QListWidgetItem(action.name)
                all_actions.append(action)
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable |
                              QtCore.Qt.ItemIsEnabled)
                item.setCheckState(QtCore.Qt.Checked)
                item.setData(QtCore.Qt.UserRole, action)
                self.actionList.addItem(item)

        # enable all actions by default
        self.allActionsCheckBox.setChecked(True)

    def on_allActionsCheckBox_stateChanged(self, state):
        if state == QtCore.Qt.PartiallyChecked:
            return

        for index in range(self.actionList.count()):
            item = self.actionList.item(index)
            item.setCheckState(state)
        self.actionList.setCurrentItem(None)  # reset selection

    def on_actionList_itemChanged(self, item):
        """Item checked/unchecked.
        """
        checked_action_count = 0
        for index in range(self.actionList.count()):
            action_item = self.actionList.item(index)
            if action_item.checkState() == QtCore.Qt.Checked:
                checked_action_count += 1

        if checked_action_count == 0:
            self.allActionsCheckBox.setCheckState(QtCore.Qt.Unchecked)
        elif checked_action_count == self.actionList.count():
            self.allActionsCheckBox.setCheckState(QtCore.Qt.Checked)
        else:
            self.allActionsCheckBox.setCheckState(QtCore.Qt.PartiallyChecked)

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


def main(package_module):

    app = QtGui.QApplication(sys.argv)
    main_window = MainWindow()

    package_module_name = package_module.__name__
    for _, module_name, _ in iter_modules([package_module_name]):
        main_window.packageCombo.addItem(module_name, package_module_name + '.' + module_name)

    if main_window.packageCombo.count():
        main_window.packageCombo.activated.emit(0)

    main_window.show()
    main_window.proceedButton.setFocus(True)
    app.exec()
