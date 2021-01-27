import sys
# from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
# from PyQt5.QtWidgets import QSlider
import numpy as np
class DoubleSlider(QSlider):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.decimals = 3
        self._max_int = 10 ** self.decimals

        super().setMinimum(0)
        super().setMaximum(self._max_int)

        self._min_value = 200
        self._max_value = 250

    @property
    def _value_range(self):
        return self._max_value - self._min_value

    def value(self):
        return float(super().value()) / self._max_int * self._value_range + self._min_value

    def setValue(self, value):
        super().setValue(int((value - self._min_value) / self._value_range * self._max_int))

    def setMinimum(self, value):
        if value > self._max_value:
            raise ValueError("Minimum limit cannot be higher than maximum")

        self._min_value = value
        self.setValue(self.value())

    def setMaximum(self, value):
        if value < self._min_value:
            raise ValueError("Minimum limit cannot be higher than maximum")

        self._max_value = value
        self.setValue(self.value())

    def minimum(self):
        return self._min_value

    def maximum(self):
        return self._max_value


# class DoubleSlider(QSlider):

#     def __init__(self, *args, **kargs):
#         super(DoubleSlider, self).__init__( *args, **kargs)
#         self._min = 0
#         self._max = 99
#         self.interval = 1

#     def setValue(self, value):
#         index = round((value - self._min) / self.interval)
#         return super(DoubleSlider, self).setValue(index)

#     def value(self):
#         return self.index * self.interval + self._min

#     @property
#     def index(self):
#         return super(DoubleSlider, self).value()

#     def setIndex(self, index):
#         return super(DoubleSlider, self).setValue(index)

#     def setMinimum(self, value):
#         self._min = value
#         self._range_adjusted()

#     def setMaximum(self, value):
#         self._max = value
#         self._range_adjusted()

#     def setInterval(self, value):
#         # To avoid division by zero
#         if not value:
#             raise ValueError('Interval of zero specified')
#         self.interval = value
#         self._range_adjusted()


#     def _range_adjusted(self):
#         number_of_steps = int((self._max - self._min) / self.interval)
#         super(DoubleSlider, self).setMaximum(number_of_steps)


class Window(QMainWindow):
    def __init__(self, parent = None):
        super(Window, self).__init__(parent)

        self.n = 100
        self.M = 291.98
        self.m = 282.08
        # rng = maxval - minval
        # self.p = (M-m/M)
        self.p = (self.n - 1)/self.n
        slider = QSlider()
        # slider = DoubleSlider()
        # (282.08, 291.98)
        slider.setMaximum(100)
        # slider.setMinimum(self.m)
        
        # slider.setInterval(1/self.n)
        # # slider.setValue(212)

        # print('index: '+ str(slider.index))
        print('sender.value(): ' + str(slider.value()))
        # slider.setTickInterval(200)
        # slider.setSingleStep(200)
        slider.valueChanged.connect(self.valchange)
        self.setCentralWidget(slider)

    def valchange(self,val):
        sender =self.sender()
        # print('index: '+ str(sender.index))
        print('sender.value(): ' + str(sender.value()))
        print('val: ' + str(val))
        print(
        self.m + (self.M - self.m)*(1 - (self.n - val)/self.n)
        )
        print(
            np.round(100*(self.m + val*(self.M - self.m)/self.n))/100
            )
        # print(val*self.p)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Window()
    window.show()

    sys.exit(app.exec_())