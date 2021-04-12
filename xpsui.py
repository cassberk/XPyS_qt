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

import h5py
import numpy as np
import matplotlib.pyplot as plt
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

import xps_peakfit.models.Nb3d.nb_oxide_analysis as nbox
import xps_peakfit.models.Si2p.si_oxide_analysis as siox

from copy import deepcopy as dc

from parameter_gui import ParameterWindow
from fitwindow import FitViewWindow
from OverviewWindow import OverviewWindow
from bgSubWindow import bgSubWindow
import data_tree
from qtio import load_sample

from IPython import embed as shell

# class bgSubWindow(QWidget):

#     def __init__(self,sample):
#         super().__init__()
#         self.sample = sample
#         self.initUI()

#     def initUI(self):

#         self.bgSpecSelect = QComboBox(self)
#         self.bgSpecSelect.addItems([orb for orb in self.sample.element_scans])
#         self.bgSpecSelect.currentIndexChanged.connect(self.load_bgVals)

#         self.bgTypeBox = QComboBox(self)
#         self.bgTypeBox.addItems(['linear','shirley','UT2'])

#         self.minBox= QDoubleSpinBox()
#         self.maxBox= QDoubleSpinBox()

#         self.par1Box = QDoubleSpinBox()
#         self.par1Box.setMaximum(np.inf)
#         self.par1Box.setMinimum(-np.inf)

#         self.par2Box = QDoubleSpinBox()
#         self.par2Box.setMaximum(np.inf)
#         self.par2Box.setMinimum(-np.inf)

#         self.par1_cb = QCheckBox("B")
#         self.par2_cb= QCheckBox("C")

#         self.setBG_Button = QPushButton('Select', self)
#         self.setBG_Button.setObjectName('setBGbutton')
#         self.setBG_Button.clicked.connect(self.set_bgPars)

#         self.load_bgVals()

#         vbox = QVBoxLayout(self)
#         hbox_bglims = QHBoxLayout()
#         hbox_bgpars = QHBoxLayout()

#         vbox.addWidget(self.bgSpecSelect)
#         vbox.addWidget(self.bgTypeBox)

#         hbox_bglims.addWidget(self.minBox)
#         hbox_bglims.addWidget(self.maxBox)
#         vbox.addLayout(hbox_bglims)

#         hbox_bgpars.addWidget(self.par1Box)
#         hbox_bgpars.addWidget(self.par1_cb)
#         hbox_bgpars.addWidget(self.par2Box)
#         hbox_bgpars.addWidget(self.par2_cb)
#         vbox.addLayout(hbox_bgpars)

#         vbox.addWidget(self.setBG_Button )

#         self.setLayout(vbox)

#         self.setGeometry(300, 300, 350, 250)
#         self.setWindowTitle('QListWidget')
#         self.show()

#     def load_bgVals(self):
#         bgtype_idx = self.bgTypeBox.findText(self.sample.bg_info[self.bgSpecSelect.currentText()][1])
#         self.bgTypeBox.setCurrentIndex(bgtype_idx)

#         self.minBox.setMaximum(np.max(self.sample.__dict__[self.bgSpecSelect.currentText()].E))  # Need to set max and min before value 
#         self.minBox.setMinimum(np.min(self.sample.__dict__[self.bgSpecSelect.currentText()].E)) 
#         self.minBox.setValue(self.sample.bg_info[self.bgSpecSelect.currentText()][0][0])

#         self.maxBox.setMaximum(np.max(self.sample.__dict__[self.bgSpecSelect.currentText()].E))  # Need to set max and min before value 
#         self.maxBox.setMinimum(np.min(self.sample.__dict__[self.bgSpecSelect.currentText()].E)) 
#         self.maxBox.setValue(self.sample.bg_info[self.bgSpecSelect.currentText()][0][1])
        
#         if len(self.sample.bg_info[self.bgSpecSelect.currentText()]) > 2:
#             self.par1Box.setValue(self.sample.bg_info[self.bgSpecSelect.currentText()][2][0])
#             self.par2Box.setValue(self.sample.bg_info[self.bgSpecSelect.currentText()][2][2])

#             self.par1_cb.setChecked(bool(self.sample.bg_info[self.bgSpecSelect.currentText()][2][0]))
#             self.par2_cb.setChecked(bool(self.sample.bg_info[self.bgSpecSelect.currentText()][2][3]))
#         else:

#             self.par1Box.setValue(0)
#             self.par2Box.setValue(0)

#             self.par1_cb.setChecked(False)
#             self.par2_cb.setChecked(False)

#     def set_bgPars(self):
#         self.sample.bg_info[self.bgSpecSelect.currentText()][1] = self.bgTypeBox.currentText()
#         self.sample.bg_info[self.bgSpecSelect.currentText()][0] = tuple([self.minBox.value(),self.maxBox.value()])
#         if self.bgTypeBox.currentText() =='UT2':
#             if len(self.sample.bg_info[self.bgSpecSelect.currentText()]) > 2:
#                 self.sample.bg_info[self.bgSpecSelect.currentText()][2] = tuple([self.par1Box.value(),int(self.par1_cb.isChecked()),self.par2Box.value(),int(self.par2_cb.isChecked())])
#             else:
#                 self.sample.bg_info[self.bgSpecSelect.currentText()].append(tuple([self.par1Box.value(),int(self.par1_cb.isChecked()),self.par2Box.value(),int(self.par2_cb.isChecked())]))


class ExpChooseWindow(QWidget):

    def __init__(self,files):
        super().__init__()
        self.files = files
        self.initUI()

    def initUI(self):

        vbox = QVBoxLayout(self)
        hbox = QHBoxLayout()

        self.listWidget = QListWidget(self)

        self.listWidget.addItems([file for file in self.files])

        self.ExperimentSelectButton = QPushButton('Select', self)
        # self.ExperimentSelectButton.clicked.connect(self.onClearClicked)

        vbox.addWidget(self.listWidget)
        hbox.addWidget(self.ExperimentSelectButton )
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('QListWidget')
        self.show()


    # def onClearClicked(self):

    #     self.listWidget.clear()

    # def onCountClicked(self):

    #     QMessageBox.information(self, "Info", 
    #         f'# of birds {self.listWidget.count()}')


class SampleHandler(QWidget):
    def __init__(self,treeparent = None, treechildren = None):
        QWidget.__init__(self)
        
        self.SpectraWindows = {}
        self.OverviewWindow = {}
        self.show_sampletree_window()
        # cd = combodemo()
        # cd.show()
        # s = xps_peakfit.sample.sample(overview=False)
        # s = xps_peakfit.io.load_sample(filepath = '/Volumes/GoogleDrive/Shared drives/StOQD/sample_library/Films/A205/XPS/A205.hdf5',\
        #     experiment_name = 'depth_profile_1')
        # self.sample = s
        # self.show_sampletree_window(treeparent = s.sample_name, \
        #     treechildren = s.element_scans)


    def show_sampletree_window(self,treeparent = None, treechildren = None):
        self.treeparent = treeparent
        self.children = treechildren
        self.tree = QTreeWidget(self)
        if treeparent != None:
            self.tree.itemChanged[QTreeWidgetItem, int].connect(self.vrfs_selected)
            self.iter = 0
            self.add_tree()        
            self.connect_sampletree()
        self.tree.show() 

        self.addSampleButton = QPushButton('Load Sample', self)
        self.addSampleButton.clicked.connect(self.loadFiles)

        self.LoadRecentButton = QPushButton('Load Recent Sample', self)
        self.LoadRecentButton.clicked.connect(self.loadRecent)

        self.button = QPushButton('Print', self)
        self.button.clicked.connect(self.vrfs_selected)

        self.overview_button = QPushButton('Overview Analysis', self)
        self.overview_button.clicked.connect(self.plot_overview)
        self.overview_button.setObjectName('overview_analysis')
        self.plot_all_cb = QCheckBox("Raw Plot")
        self.plot_all_cb.setChecked(False)
        self.plot_all_cb.setObjectName('raw')
        self.plot_bg_cb = QCheckBox("Background Sub")
        self.plot_bg_cb.setChecked(False)
        self.plot_bg_cb.setObjectName('bg')
        self.plot_atp_cb = QCheckBox("Atomic Percent Plot")
        self.plot_atp_cb.setChecked(False)
        self.plot_atp_cb.setObjectName('atomic_percent')


        self.overview_plot_button = QPushButton("Plot Overview")
        self.overview_plot_button.clicked.connect(self.plot_overview)
        self.overview_plot_button.setObjectName('overview_plot')

        self.clearbutton = QPushButton('Remove Sample', self)
        self.clearbutton.clicked.connect(self.clear_sample)

        self.fitwindowbutton = QPushButton('Fit', self)
        self.fitwindowbutton.clicked.connect(self.show_fit_window)

        self.saveSampleButton = QPushButton('Save Sample', self)
        self.saveSampleButton.clicked.connect(self.saveSample)
        self.saveSpectraButton = QPushButton('Save Spectra', self)
        self.saveSpectraButton.clicked.connect(self.saveSpectra)

        self.linkampbutton = QPushButton('Link Amplitudes', self)
        self.linkampbutton.clicked.connect(self.link_amplitudes)

        self.shellbutton = QPushButton('Shell Debug', self)
        self.shellbutton.clicked.connect(self.shelldebug)

        self.bgSubButton = QPushButton('bg Sub', self)
        self.bgSubButton.clicked.connect(self.bgsub)

        overviewHbox = QHBoxLayout()
        overviewHbox.addWidget(self.plot_all_cb)
        overviewHbox.addWidget(self.plot_bg_cb)
        overviewHbox.addWidget(self.plot_atp_cb)
        overviewHbox.addWidget(self.overview_plot_button)

        SaveLayout = QHBoxLayout()
        SaveLayout.addWidget(self.saveSampleButton)
        SaveLayout.addWidget(self.saveSpectraButton)

        layout = QVBoxLayout(self)
        layout.addWidget(self.tree)
        layout.addWidget(self.addSampleButton)
        layout.addWidget(self.LoadRecentButton)
        layout.addLayout(overviewHbox)
        layout.addWidget(self.overview_button)
        layout.addWidget(self.fitwindowbutton)
        layout.addLayout(SaveLayout)
        layout.addWidget(self.clearbutton)
        layout.addWidget(self.linkampbutton)
        layout.addWidget(self.shellbutton)
        layout.addWidget(self.button)
        layout.addWidget(self.bgSubButton)

    def loadFiles(self):
        filter = "All Files (*)"
        file_name = QFileDialog()
        file_name.setFileMode(QFileDialog.ExistingFiles)
        _files,_ = file_name.getOpenFileNames(self, ".hdf5", "/Volumes/GoogleDrive/Shared drives/StOQD/sample_library", filter)
        # shell()
        if not _files == []:
            with h5py.File(_files[0],'r+') as f:
                self.experiments = [grp for grp in f.keys()]
            print(self.experiments)
            # if len([grp for grp in self.experiments]) > 1:
            self.expchooseWindow = ExpChooseWindow(self.experiments)
            self.expchooseWindow.ExperimentSelectButton.clicked.connect(lambda: self.choose_experiment(_files[0]))
            self.expchooseWindow.show()
        # else:
        # self.sample = xps_peakfit.io.load_sample(filepath = _files[0],\
        #     experiment_name = self.experiments[0])
    def saveSample(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()",self.sample.load_path,"All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            self.savehdf5_sample()

    def saveSpectra(self):
        self.vrfs_selected()
        print(self.updatelist)
            # print(fileName)
        for spec in self.updatelist:
            # print(spec,'will be saved to', self.sample.load_path)
            xps_peakfit.io.save_spectra_analysis(self.sample.__dict__[spec],filepath = self.sample.load_path, experiment_name = self.sample.experiment_name,force = True)
            # print(self.sample.experiment_name)

    def build_sample_tree(self):
        self.treeparent = self.sample.sample_name
        self.children = self.sample.element_scans
        self.tree.itemChanged[QTreeWidgetItem, int].connect(self.vrfs_selected)
        self.iter = 0
        self.add_tree()        
        self.connect_sampletree()

    def choose_experiment(self,file):
        self.loadhdf5_sample(filepath = file, experiment_name = self.expchooseWindow.listWidget.selectedItems()[0].text())
        self.expchooseWindow.close()   

    def loadhdf5_sample(self,filepath,experiment_name):
        self.sample = xps_peakfit.io.load_sample(filepath = filepath, experiment_name = experiment_name)
        self.build_sample_tree()
        with open('recentfile.txt','w') as f:
            f.write(filepath+','+experiment_name)
    
    def savehdf5_sample(self):
        xps_peakfit.io.save_sample(self.sample,filepath = self.sample.load_path, experiment_name = self.sample.experiment_name,force = True)

    def loadRecent(self):
        with open('recentfile.txt') as f:
            paths = [p for p in f.readlines()][0].split(',')
        print('Opened file: ',paths[0],'Experiment: ',paths[1])
        self.loadhdf5_sample(paths[0],paths[1])

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

    def clear_sample(self):
        del self.sample
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
        print(self.updatelist)

    def handleButton(self):
         iterator = QTreeWidgetItemIterator(self.tree)
         while iterator.value():
             item = iterator.value()
             print(item.text(0))
             iterator += 1

    def show_fit_window(self):
        # print(self.updatelist)
        # print(dir(self.sample.__dict__[self.updatelist[0]]))
        

        if self.updatelist != []:
            for spectra in self.updatelist:
                if hasattr(self.sample.__dict__[spectra],'isub'):
                    self.SpectraWindows[spectra] = FitViewWindow(spectra_obj = self.sample.__dict__[spectra])
                    self.SpectraWindows[spectra].show()
                else:
                    print('No bg Subtraction data!')


    def plot_overview(self):

        sender = self.sender()

        if (sender.objectName() == 'overview_analysis') or (sender.objectName() == 'setBGbutton'):
            self.sample.xps_overview(plotflag = False)
        for cb in [self.plot_all_cb,self.plot_bg_cb,self.plot_atp_cb]:
            if cb.isChecked():
                overview_type = cb.objectName()
                self.OverviewWindow[overview_type] = OverviewWindow(sample_obj = self.sample,which_plot = overview_type)
                self.OverviewWindow[overview_type].show()



    def bgsub(self):
        self.bgSubWin = bgSubWindow(sample = self.sample)
        self.bgSubWin.setBG_Button.clicked.connect(self.plot_overview)
        self.bgSubWin.show()

    def shelldebug(self):
        shell()


    ### Linking Parameter amplitudes
    def link_amplitudes(self):
        self.plists = {}
        for spectra in self.updatelist:
            self.plists[spectra] = [par for component_pars in [model_component._param_names for model_component in self.sample.__dict__[spectra].mod.components]\
            for par in component_pars if 'amplitude' in par]

        self.amplink_window = LinkAmplitudesWindow(parameter_lists = self.plists)
        self.amplink_window.show()

        self.amplink_window.link_button.clicked.connect(self.link_parameters)

        # for spectra1 in plists.keys():
        #     # print('i',i,'is',self.amplink_window.cb[i].currentText())
        #     for spectra2 in plists.keys():
        #         # print('j',j,'is',self.amplink_window.cb[j].currentText())
        #         if spectra1 != spectra2:
        #             par1 = self.amplink_window.cb[spectra1].currentText()
        #             par2 = self.amplink_window.cb[spectra2].currentText()
        # #             self.SpectraWindows[spectra1].paramsWindow.paramwidgets[par1].slider.valueChanged.connect(self.update_slider)
        #             print(par1,'linked to',par2)
        #             self.parsig = ParSignal(sample_obj.__dict__[spectra1].params[par1])

    # def write_link_pars(self):
    #     self.linked_pars = 
    def link_parameters(self,v):
        for spectra1 in self.plists.keys():
            # print('i',i,'is',self.amplink_window.cb[i].currentText())
            for spectra2 in self.plists.keys():
                # print('j',j,'is',self.amplink_window.cb[j].currentText())
                if spectra1 != spectra2:
                    par1 = self.amplink_window.cb[spectra1].currentText()
                    par2 = self.amplink_window.cb[spectra2].currentText()

                    self.SpectraWindows[spectra1].params[par1].valueChanged.connect(self.SpectraWindows[spectra2].params[par2].slotvalue)


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



class LinkAmplitudesWindow(QWidget):
    def __init__(self, parameter_lists = {}):
        QWidget.__init__(self)

        layout = QHBoxLayout()

        self.cb = {}
        for spectra,plist in parameter_lists.items():
            self.cb[spectra] = QComboBox()
            self.cb[spectra].addItems(plist)
            # self.cb[plist[0]].currentIndexChanged.connect(self.selectionchange)
            layout.addWidget(self.cb[spectra])

        self.link_button = QPushButton('Link', self)
        layout.addWidget(self.link_button)
        # self.button.clicked.connect(self.vrfs_selected)

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