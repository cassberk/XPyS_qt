"""
This demo demonstrates how to embed a matplotlib (mpl) plot 
into a PyQt5 GUI application, including:

* Using the navigation toolbar
* Adding data to the plot
* Dynamically modifying the plot's properties
* Processing mpl events
* Saving the plot to a file from a menu

The main goal is to serve as a basis for developing rich PyQt GUI
applications featuring mpl plots (using the mpl OO API).

Eli Bendersky (eliben@gmail.com), updated by Ondrej Holesovsky.
License: this code is in the public domain
Last modified: 23.12.2019
"""
import sys, os, random
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import numpy as np
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import lmfit as lm
import pickle
import os
from qtdata_io import load_excel
sys.path.append("/Users/cassberk/code")
import xps_peakfit.io
import xps_peakfit.sample
from copy import deepcopy as dc

from parameter_gui import ParameterWindow
from fitwindow import FitViewWindow
import data_tree
from qtio import load_sample

from IPython import embed as shell


class SampleHandler(QWidget):
    def __init__(self,treeparent = None, treechildren = None):
        QWidget.__init__(self)
        
        self.SpectraWindows = {}
        # cd = combodemo()
        # cd.show()
        s = xps_peakfit.sample.sample(overview=False)
        xps_peakfit.io.load_sample(s, filepath = '/Volumes/GoogleDrive/Shared drives/StOQD/sample_library/ALD/205/XPS_205.hdf5',\
            experiment_name = 'depth_profile_1')
        self.sample_obj = s
        self.show_sampletree_window(treeparent = s.sample_name, \
            treechildren = s.element_scans)


    def show_sampletree_window(self,treeparent = None, treechildren = None):
        self.treeparent = treeparent
        self.children = treechildren
        self.tree = QTreeWidget(self)
        self.tree.itemChanged[QTreeWidgetItem, int].connect(self.vrfs_selected)
        self.iter = 0
        self.add_tree()        
        self.connect_sampletree()
        self.tree.show() 

        self.adtreebutton = QPushButton('addtree', self)
        self.adtreebutton.clicked.connect(self.add_tree)

        self.button = QPushButton('Print', self)
        self.button.clicked.connect(self.vrfs_selected)

        # self.clearbutton = QPushButton('cleartree', self)
        # self.clearbutton.clicked.connect(self.cleartree)

        self.fitwindowbutton = QPushButton('fit window', self)
        self.fitwindowbutton.clicked.connect(self.show_fit_window)

        self.linkampbutton = QPushButton('Link Amplitudes', self)
        self.linkampbutton.clicked.connect(self.link_amplitudes)

        layout = QVBoxLayout(self)
        layout.addWidget(self.tree)
        layout.addWidget(self.adtreebutton)
        layout.addWidget(self.button)
        layout.addWidget(self.linkampbutton)
        layout.addWidget(self.fitwindowbutton)


    def add_tree(self):
        i=self.iter
        parent = QTreeWidgetItem(self.tree)
        # parent.setText(0, "Parent {}".format(i))
        parent.setText(0,self.treeparent)

        parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

        for ch in self.children:
            child1 = QTreeWidgetItem(parent)
            child1.setFlags(child1.flags() | Qt.ItemIsUserCheckable)
            child1.setText(0, ch)
            child1.setCheckState(0, Qt.Unchecked)
            # for x in range(5):
            #     child2 = QTreeWidgetItem(child1)
            #     child2.setFlags(child2.flags() | Qt.ItemIsUserCheckable)
            #     child2.setText(0, "Child {}".format(x))
            #     child2.setCheckState(0, Qt.Unchecked)
        self.iter +=1

    def clear_tree(self):
        self.tree.clear()
        self.iter=0

    def vrfs_selected(self):
        iterlist = []
        iterator = QTreeWidgetItemIterator(self.tree, QTreeWidgetItemIterator.Checked)
        while iterator.value():
            item = iterator.value()
            if item.text(0) not in self.treeparent:
                iterlist.append(item.text(0))    
            iterator += 1
        self.updatelist =  iterlist
        # self.show_fit_window()
        # print(self.updatelist)

    def handleButton(self):
         iterator = QTreeWidgetItemIterator(self.tree)
         while iterator.value():
             item = iterator.value()
             print(item.text(0))
             iterator += 1

    def show_fit_window(self):
        print(self.updatelist)
        # print(dir(self.sample_obj.__dict__[self.updatelist[0]]))
        if self.updatelist != []:
            for spectra in self.updatelist:
                
                self.SpectraWindows[spectra] = FitViewWindow(spectra_obj = self.sample_obj.__dict__[spectra])
                self.SpectraWindows[spectra].show()


    def link_amplitudes(self):

        # plists = []
        # for spectra in self.updatelist:
        #     plists.append([par for component_pars in [model_component._param_names for model_component in self.sample_obj.__dict__[spectra].mod.components]\
        #     for par in component_pars if 'amplitude' in par])
        plists = {}
        for spectra in self.updatelist:
            plists[spectra] = [par for component_pars in [model_component._param_names for model_component in self.sample_obj.__dict__[spectra].mod.components]\
            for par in component_pars if 'amplitude' in par]

        self.amplink_window = LinkAmplitudesWindow(parameter_lists = plists)
        self.amplink_window.show()

        # for i in range(len(plists)):
        #     # print('i',i,'is',self.amplink_window.cb[i].currentText())
        #     for j in range(len(plists)):
        #         # print('j',j,'is',self.amplink_window.cb[j].currentText())
        #         if i!=j:
        #             self.SpectraWindows[spectra].paramsWindow[par].slider.valueChanged.connect(self.SpectraWindows[spectra].update_val)
        #             print(self.amplink_window.cb[i].currentText(),'linked to',self.amplink_window.cb[j].currentText())
        self.parsig = ParSignal(parameter = self.sample_obj.__dict__['Nb3d'].params['Nb_52_amplitude'])
        self.parsig.valueChanged.connect(self.itworked)
        shell()
        # for spectra1 in plists.keys():
        #     # print('i',i,'is',self.amplink_window.cb[i].currentText())
        #     for spectra2 in plists.keys():
        #         # print('j',j,'is',self.amplink_window.cb[j].currentText())
        #         if spectra1 != spectra2:
        #             par1 = self.amplink_window.cb[spectra1].currentText()
        #             par2 = self.amplink_window.cb[spectra2].currentText()
        #             self.SpectraWindows[spectra1].paramsWindow.paramwidgets[par1].slider.valueChanged.connect(self.update_slider)
        #             print(par1,'linked to',par2)
        #             self.parsig = ParSignal(sample_obj.__dict__[spectra1].params[par1])
    def itworked(self,v):
        print('Signal sentm value',v)
    def update_slider(self):
        sender = self.sender()
        m = np.min(self.ctrl_limits_min)
        M = np.max(self.ctrl_limits_max)
        slideval = np.round( (self.numbox.value() - m)/( (M-m)/self.N ) )

        self.slider.setValue(slideval)

    def update_spinbox(self, v):
        sender = self.sender()

        m = np.min(self.ctrl_limits_min)
        M = np.max(self.ctrl_limits_max)
        numboxval = np.round(100*(m + v*(M - m)/self.N ))/100

        self.numbox.setValue(numboxval)

                    # self.amplink_window.cb[i].currentIndexChanged.connect(self.selectionchange)
        # for qlist in self.amplink_window.cb:
        #     print(qlist.currentText())
        # self.SpectraWindows[spectra].paramsWindow[par].slider.valueChanged.connect(self.SpectraWindows[spectra].update_val)
        # self.SpectraWindows[spectra].paramsWindow[par].slider.valueChanged.connect(self.update_val)

    def selectionchange(self):
        for i in range(len(self.amplink_window.cb)):
            print("selection changed ",self.amplink_window.cb[i].currentText())

    def connect_sampletree(self):
        # self.sampletreeWindow.button.clicked.connect(self.plot_tree_choices)  # Not sure why this is here, clicking on window initiates self.plot_tree_choices
        self.tree.itemChanged[QTreeWidgetItem, int].connect(self.plot_tree_choices)
        
        # self.sampletreeWindow.tree.itemClicked[QTreeWidgetItem, int].connect(self.plot_tree_choices)

    def plot_tree_choices(self, item, column):
        print(item.text(0))
        if item.checkState(column) == Qt.Checked:
            print(item.text(0),'Item Checked')
            # self.update_plot(sample = self.xpssamp,data = item.text(0))

class ParSignal(QWidget):
    valueChanged = pyqtSignal(object)

    def __init__(self, parameter=None):
        super(ParSignal, self).__init__()
        self._par = parameter

    @property
    def value(self):
        return self._par.value

    @value.setter
    def value(self, val):
        self._par.set(value = val)
        self.valueChanged.emit(val)


class LinkAmplitudesWindow(QWidget):
    def __init__(self, parameter_lists = {}):
        QWidget.__init__(self)

        layout = QHBoxLayout()
        # self.cb = []
        # for plist in enumerate(parameter_lists):
        #     self.cb.append(QComboBox())
        #     self.cb[plist[0]].addItems(plist[1])
        #     # self.cb[plist[0]].currentIndexChanged.connect(self.selectionchange)
        #     layout.addWidget(self.cb[plist[0]])

        self.cb = {}
        for spectra,plist in parameter_lists.items():
            self.cb[spectra] = QComboBox()
            self.cb[spectra].addItems(plist)
            # self.cb[plist[0]].currentIndexChanged.connect(self.selectionchange)
            layout.addWidget(self.cb[spectra])

        self.setLayout(layout)
        self.setWindowTitle("Link Parameters")
        # self.show()

    # def selectionchange(self,i):
    #     for i in range(len(self.cb)):
    #         print("selection changed ",self.cb[i].currentText())
 

def main():
    app = QApplication(sys.argv)
    # form = FitViewWindow()
    form = SampleHandler()
    form.show()
    app.exec_()


if __name__ == "__main__":
    main()