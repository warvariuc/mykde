__version__ = '1.2.0'
__author__ = 'Victor Varvariuc<victor.varvariuc@gmail.com>'


from .base import *

# disable PyQt input hook in order for ipdb to work
QtCore.pyqtRemoveInputHook()
