import sys
# from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class DoubleSlider(QSlider):

    def __init__(self, *args, **kargs):
        super(DoubleSlider, self).__init__( *args, **kargs)
        self._min = 0
        self._max = 99
        self.interval = 1

    def setValue(self, value):
        index = round((value - self._min) / self.interval)
        return super(DoubleSlider, self).setValue(index)

    def value(self):
        return self.index * self.interval + self._min

    @property
    def index(self):
        return super(DoubleSlider, self).value()

    def setIndex(self, index):
        return super(DoubleSlider, self).setValue(index)

    def setMinimum(self, value):
        self._min = value
        self._range_adjusted()

    def setMaximum(self, value):
        self._max = value
        self._range_adjusted()

    def setInterval(self, value):
        # To avoid division by zero
        if not value:
            raise ValueError('Interval of zero specified')
        self.interval = value
        self._range_adjusted()

    def _range_adjusted(self):
        number_of_steps = int((self._max - self._min) / self.interval)
        super(DoubleSlider, self).setMaximum(number_of_steps)
