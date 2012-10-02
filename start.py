#!/usr/bin/env python3

__author__ = "Victor Varvariuc <victor.varvariuc@gmail.com>"

import sys
pythonRequiredVersion = '3.2' # tested with this version or later
if sys.version < pythonRequiredVersion:
    raise SystemExit('Python %s or newer required (you are using: %s).' % (pythonRequiredVersion, sys.version))


import os
from scripts import main

curDir = os.path.dirname(os.path.abspath(__file__))
themesDir = os.path.join(curDir, 'themes')

main.main(themesDir)

from PyQt4 import QtCore, QtGui
import sys
from random import randint


app = QtGui.QApplication(sys.argv)

#model = QStandardItemModel()
#
#for n in range(10):                   
#    item = QStandardItem('Item %s' % randint(1, 100))
#    check = Qt.Checked if randint(0, 1) == 1 else Qt.Unchecked
#    item.setCheckState(check)
#    item.setCheckable(True)
#    model.appendRow(item)
#
#
#view = QListView()
#view.setModel(model)

#listWidget = QListWidget()
#
#for n in range(10):                   
#    item = QListWidgetItem('Item %s' % randint(1, 100))
#    check = Qt.Checked if randint(0, 1) == 1 else Qt.Unchecked
#    item.setCheckState(check)
#    item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
#    item.setToolTip(str(randint(1, 100)))
#    listWidget.insertItem(0, item)
#
#
#listWidget.show()
#app.exec()
