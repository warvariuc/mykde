"""Signals for MyKDE
"""

from .dispatch import Signal


action_set_proceeded = Signal()

kwin_stopped = Signal()
kwin_started = Signal()

plasma_stopped = Signal()
plasma_started = Signal()
