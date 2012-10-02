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


def listThemes():
    mainWindow.themesComboBox.clear()
    for fileName in os.listdir(themesDir):
        filePath = os.path.join(themesDir, fileName)
        if os.path.isdir(filePath):
            mainWindow.packagesCombo.addItem(filePath)
    mainWindow.themesComboBox.activated[str].emit(mainWindow.packagesCombo.currentText())

def main(_themesDir):
    app = QtGui.QApplication(sys.argv)
    if os.geteuid() == 0: # root privileges
        QtGui.QMessageBox.warning(None, 'Root detected', 'Do not run this script as root.\n'\
                'Run it as the user in whose session you want to install themes.')
        sys.exit()

    global mainWindow, themesDir
    themesDir = _themesDir
    curDir = os.path.dirname(os.path.abspath(__file__))
    mainWindow = uic.loadUi(os.path.join(curDir, 'main_window.ui'))
    webview.init(mainWindow.webView)

    mainWindow.themesComboBox.activated[str].connect(lambda text: webview.loadPage(text))
    mainWindow.closePushButton.clicked.connect(mainWindow.close)
    mainWindow.installPushButton.clicked.connect(lambda: install.install(unicode(mainWindow.themesComboBox.currentText())))
    mainWindow.installPushButton.setFocus(True)

    listThemes()

    mainWindow.show()
    res = app.exec() # start the event loop
    sys.exit(res)
