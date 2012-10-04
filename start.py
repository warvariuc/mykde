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


main_window = uic.loadUi(os.path.join(cur_dir, 'scripts', 'main_window.ui'))
#webview.init(mainWindow.webView)

#mainWindow.themesComboBox.activated[str].connect(lambda text: webview.loadPage(text))
#mainWindow.closePushButton.clicked.connect(mainWindow.close)
#mainWindow.installPushButton.clicked.connect(lambda: install.install(unicode(mainWindow.themesComboBox.currentText())))
#mainWindow.installPushButton.setFocus(True)

action_list_widget = main_window.action_list

for n in range(10):                   
    item = QtGui.QListWidgetItem('Item %s' % randint(1, 100))
    check = QtCore.Qt.Checked if randint(0, 1) == 1 else QtCore.Qt.Unchecked
    item.setCheckState(check)
    item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
    item.setToolTip(str(randint(1, 100)))
    action_list_widget.insertItem(0, item)


main_window.show()
app.exec()
