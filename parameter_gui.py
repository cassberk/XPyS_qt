import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
                             QMenu, QPushButton, QRadioButton, QVBoxLayout, 
                             QWidget, QSlider, QLabel, QHBoxLayout, QScrollArea, QDoubleSpinBox)
import lmfit as lm
import pickle
import os
import numpy as np


class ParameterWindow(QMainWindow):
    def __init__(self, parent=None,model = None, pairlist = None, element_ctrl = None, params = None, E = None):
        super(ParameterWindow, self).__init__(parent)


        self.mod = model
        self.pairlist = pairlist
        self.element_ctrl = element_ctrl
        self.params = params
        self.E = E

        self.rel_pars = [par for component_pars in [model_component._param_names for model_component in self.mod.components] \
            for par in component_pars]
    
        ctrl_prefixes = [[prefix for pairs in self.pairlist \
            for prefix in pairs][i] for i in self.element_ctrl]
        print(ctrl_prefixes)
        
        self.ctrl_pars = {par: any(x in par for x in ctrl_prefixes) for par in self.rel_pars}
        self.ctrl_lims = {}

        for par in self.rel_pars:
            if 'amplitude' in par:
                self.ctrl_lims[par] = (0,2*np.max(self.params[par].value))
            if 'center' in par:
                self.ctrl_lims[par] = ( np.min(self.E), np.max(self.E) )
            if 'sigma' in par:
                self.ctrl_lims[par] = ( 0, np.max([5,int(2*self.params[par].value)]) )
            if ('fraction' in par) or ('skew' in par):
                self.ctrl_lims[par] = (0,1)

        self.modgroups = [[comp_name for comp_name in self.mod.components[i]._param_names] for i in range(len(self.mod.components))]

        self.setWindowTitle("Fit Parameters")
        # self.resize(425, 392)        


        self.paramwidgets = {_:ParamGroupBox(par = p,limits = self.ctrl_lims)\
                for _, p in self.params.items() if _ in self.rel_pars}


        layout = QVBoxLayout()
        for group in self.modgroups:
            hbox = QHBoxLayout()
            for par in group:
                hbox.addWidget(self.paramwidgets[par].groupbox)
            layout.addLayout(hbox)

        widget = QWidget()
        widget.setLayout(layout)
        Area = QScrollArea()
        Area.setWidgetResizable(True)
        Area.setWidget(widget) 

        self.setCentralWidget(Area)
        # self.show(Area)

class ParamGroupBox(QWidget):
    def __init__(self, par,limits, number_of_slider_points = 100):
        super(ParamGroupBox, self).__init__()
        self.par = par
        self.limits = limits
        self.N = number_of_slider_points 
        print(self.par.name)
        print(limits[self.par.name])
        # print('min: '+str(int(np.round(np.min(limits[self.par.name])*100))))
        # print('max: '+str(int(np.round(np.max(limits[self.par.name])*100))))
        # print('val: '+str(int(np.round(self.par.value*100))))
        

        self.label = QLabel()  
        self.label.setObjectName(self.par.name)
        self.slider = QSlider(Qt.Horizontal)
        # self.slider = DoubleSlider(Qt.Horizontal)
        self.slider.setObjectName(self.par.name)
        
        # self.slider.setMaximum( np.max(limits[self.par.name]) )
        # self.slider.setMinimum( np.min(limits[self.par.name]) ) 
        # self.slider.setInterval(1/100) 
        m = np.min(self.limits[self.par.name])
        M = np.max(self.limits[self.par.name])

        slideval = np.round( (self.par.value - m)/( (M-m)/self.N ) )

        self.slider.setValue(slideval)

        # self.slider.setMinimum(int(np.round(np.min(limits[self.par.name])/100 ) ) )
        # self.slider.setMaximum(int(np.round(np.max(limits[self.par.name])/100 ) ) )
        # self.slider.setValue(self.par.value)

        # self.slider.setMinimum(int(np.round(np.min(limits[self.par.name])/100 ) ) )
        # self.slider.setMaximum(int(np.round(np.max(limits[self.par.name])/100 ) ) )
        # self.slider.setValue(int(np.round(self.par.value/100)))

        # self.slider.setFocusPolicy(Qt.StrongFocus)
        # self.slider.setTickPosition(QSlider.TicksBothSides)
        # self.slider.setTickInterval(2000)
        # self.slider.setSingleStep(1)

        self.numbox = QDoubleSpinBox()
        self.numbox.setMaximum(np.max(self.limits[par.name]))
        self.numbox.setMinimum(np.min(self.limits[par.name]))

        self.numbox.setValue(self.par.value)

        self.minbox = QDoubleSpinBox()
        # self.minbox.setMinimum(np.min(limits[par.name]))
        # self.minbox.setMaximum(np.max(limits[par.name]))
        self.minbox.setValue(self.par.min)

        self.maxbox = QDoubleSpinBox()
        # self.maxbox.setMinimum(np.min(limits[par.name]))
        # self.maxbox.setMaximum(np.max(limits[par.name]))
        self.maxbox.setValue(self.par.max)
        # print('max' + str(self.par.max))
        # print('min' + str(self.par.min))
        self.expr_text = QLineEdit()
        self.expr_text.setText(self.par.expr)

        
        self.slider.valueChanged[int].connect(self.update_spinbox)  #When the slider is modified
        self.numbox.editingFinished.connect(self.update_slider)  # When the numbox is modified

        self.layout = QGridLayout()
        self.groupbox = QGroupBox(self.par.name)
        self.groupbox.setCheckable(True)
        self.groupbox.setChecked(self.par.vary)
        self.layout.addWidget(self.groupbox)
        

        limlay = QHBoxLayout()
        limlay.addWidget(self.minbox)
        limlay.addWidget(self.maxbox)
        vbox = QVBoxLayout()
        self.groupbox.setLayout(vbox)
        vbox.addWidget(self.numbox)
        vbox.addWidget(self.expr_text)
        vbox.addLayout(limlay)
        vbox.addWidget(self.slider)


    def update_slider(self):
        sender = self.sender()
        
        # print('numboxtrig' + str(sender.minimum()))
        
        # spinbox_value uses float/ doubles type
        # '*100' is used to convert it into integer as QSlider
        # only register integer type
        m = np.min(self.limits[sender.objectName()])
        M = np.max(self.limits[sender.objectName()])

        slideval = np.round( (self.numbox.value() - m)/( (M-m)/self.N ) )

        self.slider.setValue(slideval)

    def update_spinbox(self, v):
        sender = self.sender()

        # print('slideertrig' + str(sender.minimum()))
        # QSlider only uses integer type
        # Need to convert the value from integer into float
        # and divides it by 100
        # self.numbox.setValue(float(value))
        m = np.min(self.limits[sender.objectName()])
        M = np.max(self.limits[sender.objectName()])

        numboxval = np.round(100*(m + v*(M - m)/self.N ))/100

        self.numbox.setValue(numboxval)


    # def changeparvalue(self, val):
    #     scaledValue = float(val)/100 
    #     sender = self.sender()
    #     print(sender.objectName())
    #     # label  = getattr(self, sender.objectName())
    #     # label.setText("{:>9,}".format(val))
    #     self.par.set(value = scaledValue )
    #     print(self.par.value)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    clock = ParameterWindow()
    clock.show()
    sys.exit(app.exec_())


##### Old Code
        # grid = QGridLayout()
        # scrollWidget = QWidget()
        # scrollWidget.setLayout(grid)
        # scrollArea = QScrollArea()
        # scrollArea.setWidgetResizable(True)
        # scrollArea.setWidget(scrollWidget)   
        # self.mainLayout = QHBoxLayout()
        # self.mainLayout.addWidget(scrollArea)
        # self.setLayout(self.mainLayout)

        # for row in range(len(self.modgroups)):
        #     for col in range(len(self.modgroups[row])):
        #         # grid.addWidget(self.createExampleGroup(row, col), row, col)
        #         grid.addWidget(CustomSlider, row, col)

        # slider1 = CustomSlider(par = self.params['Nb_52_amplitude'])



        # layout = QVBoxLayout(self)
        # layout.addWidget(self.numbox)
        # layout.addWidget(self.slider)



        # vbox = QVBoxLayout(self)
        # # vbox.addWidget(self.label)
        # vbox.addWidget(self.numbox)
        # vbox.addWidget(self.slider)
        # vbox.addStretch(1)
        # self.groupBox.setLayout(vbox)



          # grid.addWidget(slider2)
    # def createExampleGroup(self, row, column):
    #     numSlider = row*2+column if row==0 else row*2+column+row
    #     groupBox = QGroupBox(self.rel_pars[numSlider].format(numSlider))

    #     self.label = QLabel()  
    #     self.label.setObjectName("label{}".format(numSlider))

    #     slider = QSlider(Qt.Horizontal)
    #     numbox = QDoubleSpinBox()

    #     name = self.rel_pars[numSlider].format(numSlider)
    #     slider.setObjectName(name)
    #     numbox.setObjectName(name)

    #     setattr(self, name, self.label) 
    #     slider.setRange(1, 2000000)
    #     numbox.setRange(1, 2000000)
    #     slider.setFocusPolicy(Qt.StrongFocus)
    #     slider.setTickPosition(QSlider.TicksBothSides)
    #     slider.setTickInterval(200000)
    #     slider.setSingleStep(0.01)
    #     slider.valueChanged[int].connect(self.changevalue)
    #     slider.valueChanged.connect(numbox.setValue)
    #     # slider.rangeChanged.connect(numbox.setRange)
    #     numbox.valueChanged.connect(slider.setValue)


    #     # numbox = QDoubleSpinBox()
    #     # INPUT = textfield.text()
    #     # INPUT2 = float(INPUT)
    #     # name = self.rel_pars[numSlider].format(numSlider)
    #     # numbox.setObjectName(name) 
    #     # setattr(self, name, self.label) 
    #     # slider.setRange(1, 2000000)
    #     # slider.setFocusPolicy(Qt.StrongFocus)
    #     # slider.setTickPosition(QSlider.TicksBothSides)
    #     # slider.setTickInterval(200000)
    #     # slider.setSingleStep(1)
    #     # slider.valueChanged[int].connect(self.changevalue)

    #     vbox = QVBoxLayout()
    #     vbox.addWidget(self.label)
    #     vbox.addWidget(numbox)
    #     vbox.addWidget(slider)
    #     vbox.addStretch(1)
    #     groupBox.setLayout(vbox)

    #     return groupBox

    # def changevalue(self, val):
    #     sender = self.sender()
    #     print(sender.objectName())
    #     label  = getattr(self, sender.objectName())
    #     label.setText("{:>9,}".format(val))
    #     self.params[sender.objectName()].set(value = val)
    #     print(self.params[sender.objectName()].value)
