
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
sys.path.append("/Users/cassberk/code")
import xps_peakfit.io
import xps_peakfit.sample
from xps_peakfit import bkgrds as bksb

import xps_peakfit.models.Nb3d.nb_oxide_analysis as nbox
import xps_peakfit.models.Si2p.si_oxide_analysis as siox

from copy import deepcopy as dc

from parameter_gui import ParameterWindow
from fitwindow import FitViewWindow
from OverviewWindow import OverviewWindow
import data_tree

from IPython import embed as shell


class bgSubWindow(QMainWindow):

    def __init__(self,sample):
        super().__init__()
        self.sample = sample
        self.initUI()
        self.create_main_frame()
        self.update_plot()
        self.setAttribute(Qt.WA_DeleteOnClose, True)

    def initUI(self):

        self.bgSpecSelect = QComboBox(self)
        self.bgSpecSelect.addItems([orb for orb in self.sample.element_scans])
        self.bgSpecSelect.currentIndexChanged.connect(self.load_bgVals)
        self.bgSpecSelect.currentIndexChanged.connect(self.update_plot)

        self.bgTypeBox = QComboBox(self)
        self.bgTypeBox.addItems(['linear','shirley','UT2'])

        self.minBox= QDoubleSpinBox()
        self.maxBox= QDoubleSpinBox()

        self.parB_Box = QDoubleSpinBox()
        self.parB_Box.setMaximum(np.inf)
        self.parB_Box.setMinimum(-np.inf)
        self.parB_Box.setObjectName('B')
        self.parB_Box.editingFinished.connect(self.update_slider)
        self.parB_Box.editingFinished.connect(self.set_bgPars)
        self.parB_Box.editingFinished.connect(self.update_plot)

        self.parC_Box = QDoubleSpinBox()
        self.parC_Box.setMaximum(np.inf)
        self.parC_Box.setMinimum(-np.inf)
        self.parC_Box.setObjectName('C')
        self.parC_Box.editingFinished.connect(self.update_slider)
        self.parC_Box.editingFinished.connect(self.set_bgPars)
        self.parC_Box.editingFinished.connect(self.update_plot)

        self.parB_cb = QCheckBox("B")
        self.parC_cb= QCheckBox("C")


        self.BminBox = QDoubleSpinBox()
        self.BminBox.setMaximum(3000)
        self.BminBox.setMinimum(0)
        self.BminBox.setValue(0)

        self.BmaxBox = QDoubleSpinBox()
        self.BmaxBox.setMaximum(3000)
        self.BmaxBox.setMinimum(0)
        self.BmaxBox.setValue(3000)

        self.Bslider = QSlider(Qt.Horizontal)
        self.Bslider.setObjectName('B')
        self.Bslider.setMinimum(0)
        self.Bslider.setMaximum(3000)
        self.Bslider.valueChanged.connect(self.update_spinbox)
        self.Bslider.valueChanged.connect(self.update_plot)

        self.CminBox = QDoubleSpinBox()
        self.CminBox.setMaximum(3000)
        self.CminBox.setMinimum(0)
        self.CminBox.setValue(0)

        self.CmaxBox = QDoubleSpinBox()
        self.CmaxBox.setMaximum(3000)
        self.CmaxBox.setMinimum(0)
        self.CmaxBox.setValue(3000)

        self.Cslider = QSlider(Qt.Horizontal)
        self.Cslider.setObjectName('C')
        self.Cslider.setMinimum(0)
        self.Cslider.setMaximum(3000)
        self.Cslider.valueChanged.connect(self.update_spinbox)
        self.Cslider.valueChanged.connect(self.update_plot)

        self.setBG_Button = QPushButton('Select', self)
        self.setBG_Button.setObjectName('setBGbutton')
        self.setBG_Button.clicked.connect(self.set_bgPars)
        self.setBG_Button.clicked.connect(self.update_plot)

        self.BGSubtract_Button = QPushButton('BG Subtract', self)
        self.BGSubtract_Button.setObjectName('BGSubtractButton')
        self.BGSubtract_Button.clicked.connect(self.BGSubtract)

        self.spectra_plot_box = QSpinBox()
        self.spectra_plot_box.valueChanged.connect(self.update_plot)

        self.UT2params = lm.Parameters()
        self.UT2params.add('B',value = 355)
        self.UT2params.add('C',value = 655)
        self.UT2params.add('D')


        self.load_bgVals()



    def load_bgVals(self):
        bgtype_idx = self.bgTypeBox.findText(self.sample.bg_info[self.bgSpecSelect.currentText()][1])
        self.bgTypeBox.setCurrentIndex(bgtype_idx)

        self.minBox.setMaximum(np.max(self.sample.__dict__[self.bgSpecSelect.currentText()].E))  # Need to set max and min before value 
        self.minBox.setMinimum(np.min(self.sample.__dict__[self.bgSpecSelect.currentText()].E)) 
        self.minBox.setValue(self.sample.bg_info[self.bgSpecSelect.currentText()][0][0])
        self.minBox.valueChanged.connect(self.update_plot)

        self.maxBox.setMaximum(np.max(self.sample.__dict__[self.bgSpecSelect.currentText()].E))  # Need to set max and min before value 
        self.maxBox.setMinimum(np.min(self.sample.__dict__[self.bgSpecSelect.currentText()].E)) 
        self.maxBox.setValue(self.sample.bg_info[self.bgSpecSelect.currentText()][0][1])
        self.maxBox.valueChanged.connect(self.update_plot)

        self.spectra_plot_box.setMaximum(len(self.sample.__dict__[self.bgSpecSelect.currentText()].I)-1)
        self.spectra_plot_box.setMinimum(0)

        
        if len(self.sample.bg_info[self.bgSpecSelect.currentText()]) > 2:
            self.parB_Box.setValue(self.sample.bg_info[self.bgSpecSelect.currentText()][2][0])
            self.parC_Box.setValue(self.sample.bg_info[self.bgSpecSelect.currentText()][2][2])
            self.Bslider.setValue(self.sample.bg_info[self.bgSpecSelect.currentText()][2][0])
            self.Cslider.setValue(self.sample.bg_info[self.bgSpecSelect.currentText()][2][2])
            self.parB_cb.setChecked(bool(self.sample.bg_info[self.bgSpecSelect.currentText()][2][0]))
            self.parC_cb.setChecked(bool(self.sample.bg_info[self.bgSpecSelect.currentText()][2][3]))
            
            self.UT2params['B'].set(value =self.sample.bg_info[self.bgSpecSelect.currentText()][2][0], min = 0,vary = self.sample.bg_info[self.bgSpecSelect.currentText()][2][1])
            self.UT2params['C'].set(value =self.sample.bg_info[self.bgSpecSelect.currentText()][2][2], min = 0,vary = self.sample.bg_info[self.bgSpecSelect.currentText()][2][3])
            self.UT2params['D'].set(value =0, min = 0,vary = 0)
        else:

            self.parB_Box.setValue(0)
            self.parC_Box.setValue(0)

            self.parB_cb.setChecked(False)
            self.parC_cb.setChecked(False)

    def set_bgPars(self):
        self.sample.bg_info[self.bgSpecSelect.currentText()][1] = self.bgTypeBox.currentText()
        self.sample.bg_info[self.bgSpecSelect.currentText()][0] = tuple([self.minBox.value(),self.maxBox.value()])
        if self.bgTypeBox.currentText() =='UT2':
            if len(self.sample.bg_info[self.bgSpecSelect.currentText()]) > 2:
                self.sample.bg_info[self.bgSpecSelect.currentText()][2] = tuple([self.parB_Box.value(),int(self.parB_cb.isChecked()),self.parC_Box.value(),int(self.parC_cb.isChecked())])
            else:
                self.sample.bg_info[self.bgSpecSelect.currentText()].append(tuple([self.parB_Box.value(),int(self.parB_cb.isChecked()),self.parC_Box.value(),int(self.parC_cb.isChecked())]))


    def BGSubtract(self):
        orbital = self.bgSpecSelect.currentText()
        bgtype = self.bgTypeBox.currentText()
        bg_limits = [self.minBox.value(),self.maxBox.value()]
        subpars = [bg_limits,bgtype]
        if bgtype == 'UT2':
            subpars.append([self.parB_Box.value(),int(self.parB_cb.isChecked()),self.parC_Box.value(),int(self.parC_cb.isChecked())])
        self.sample.__dict__[orbital].bg_sub(subpars=subpars)

        self.sample.bg_info[orbital] = self.sample.__dict__[orbital].bg_info
        self.load_bgVals()
        self.update_plot()


    def update_slider(self):
        sender = self.sender()
        sliderpts = 100
        if sender.objectName() == 'B':
            v = self.parB_Box.value()
            self.Bslider.setValue(v)
            self.UT2params['B'].set(v)

        elif sender.objectName() == 'C':
            v = self.parC_Box.value()
            self.Cslider.setValue(v)
            self.UT2params['C'].set(v)


    def update_spinbox(self, v):
        sender = self.sender()
        sliderpts = 100

        if sender.objectName() == 'B':
            self.parB_Box.setValue(v)
            self.UT2params['B'].set(v)

        elif sender.objectName() == 'C':
            self.parC_Box.setValue(v)
            self.UT2params['C'].set(v)



        
    # def closeEvent(self,event):
    #     self.close()








    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"
        
        path, ext = QFileDialog.getSaveFileName(self, 
                        'Save file', '', 
                        file_choices)
        path = path.encode('utf-8')
        if not path[-4:] == file_choices[-4:].encode('utf-8'):
            path += file_choices[-4:].encode('utf-8')
        print(path)
        if path:
            self.canvas.print_figure(path.decode(), dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)



    def load_file(self):
        print('Naaa')
  

    def on_about(self):
        msg = """ A demo of using PyQt with matplotlib:
        
         * Use the matplotlib navigation bar
         * Add values to the text box and press Enter (or click "Draw")
         * Show or hide the grid
         * Drag the slider to modify the width of the bars
         * Save the plot to a file using the File menu
         * Click on a bar to receive an informative message
        """
        QMessageBox.about(self, "About the demo", msg.strip())
    
    def on_pick(self, event):
        """The event received here is of the type
        matplotlib.backend_bases.PickEvent
        
        It carries lots of information, of which we're using
        only a small amount here.
        """
        
        box_points = event.artist.get_bbox().get_points()
        msg = "You've clicked on a bar with coords:\n %s" % box_points
        
        QMessageBox.information(self, "Click!", msg)
    
    def update_plot(self):
        """ Redraws the figure
        """

        # clear the axes and redraw the plot anew
        #

        self.axes.cla()        

        self.axes.grid(self.grid_cb.isChecked())
        
        self.axes.plot(self.sample.__dict__[self.bgSpecSelect.currentText()].E, self.sample.__dict__[self.bgSpecSelect.currentText()].I[self.spectra_plot_box.value()],'o')

        if hasattr(self.sample.__dict__[self.bgSpecSelect.currentText()],'bg'):
            if self.sample.bg_info[self.bgSpecSelect.currentText()][1] == 'UT2':
                bgoffset = self.sample.__dict__[self.bgSpecSelect.currentText()].I[self.spectra_plot_box.value()][-1]

                UTbg,subtr = bksb.Tougaard(self.UT2params, self.sample.__dict__[self.bgSpecSelect.currentText()].I[self.spectra_plot_box.value()],self.sample.__dict__[self.bgSpecSelect.currentText()].E)
                self.axes.plot(self.sample.__dict__[self.bgSpecSelect.currentText()].E, UTbg+bgoffset,'-')
            else:
                bgoffset = 0
                self.axes.plot(self.sample.__dict__[self.bgSpecSelect.currentText()].esub, self.sample.__dict__[self.bgSpecSelect.currentText()].bg[self.spectra_plot_box.value()]+bgoffset,'-')

        if self.sample.bg_info[self.bgSpecSelect.currentText()][1] == 'shirley':
            # self.axes.axvspan( np.min(self.sample.bg_info[self.bgSpecSelect.currentText()][0]), np.max(self.sample.bg_info[self.bgSpecSelect.currentText()][0]) , alpha=0.1, color='orange')
            self.axes.axvspan( self.minBox.value(), self.maxBox.value(), alpha=0.1, color='orange')

        elif self.sample.bg_info[self.bgSpecSelect.currentText()][1] == 'linear':
            # self.axes.axvspan( np.min(self.sample.bg_info[self.bgSpecSelect.currentText()][0]), np.max(self.sample.bg_info[self.bgSpecSelect.currentText()][0]) , alpha=0.1, color='green')
            self.axes.axvspan( self.minBox.value(), self.maxBox.value(), alpha=0.1, color='green')

        elif self.sample.bg_info[self.bgSpecSelect.currentText()][1] == 'UT2':
            # self.axes.axvspan( np.min(self.sample.bg_info[self.bgSpecSelect.currentText()][0]), np.max(self.sample.bg_info[self.bgSpecSelect.currentText()][0]) , alpha=0.1, color='blue')
            self.axes.axvspan( self.minBox.value(), self.maxBox.value(), alpha=0.1, color='blue')




        self.axes.set_xlabel('Binding Energy (eV)',fontsize=24)
        self.axes.set_ylabel('Counts/sec',fontsize=24)
        self.axes.set_xlim(np.max(self.sample.__dict__[self.bgSpecSelect.currentText()].E),np.min(self.sample.__dict__[self.bgSpecSelect.currentText()].E))
        self.axes.tick_params(labelsize=20)
        self.fig.tight_layout()
        self.canvas.draw()




    """Build the Main window"""
    def create_main_frame(self):
        self.main_frame = QWidget()
        
        """Create the mpl Figure and FigCanvas objects. 
        5x4 inches, 100 dots-per-inch
        """
        self.dpi = 100
        self.fig = Figure((5.0, 4.0), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        
        """Since we have only one plot, we can use add_axes 
        instead of add_subplot, but then the subplot
        configuration tool in the navigation toolbar wouldn't
        work.
        """
        self.axes = self.fig.add_subplot(111)
        
        """Bind the 'pick' event for clicking on one of the bars"""
        self.canvas.mpl_connect('pick_event', self.on_pick)
        
        """Create the navigation toolbar, tied to the canvas"""
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
        
        """Other GUI controls"""




        self.grid_cb = QCheckBox("Show &Grid")
        self.grid_cb.setChecked(False)
        self.grid_cb.stateChanged.connect(self.update_plot)




        """Layout with box sizers"""
        
        vbox_select = QVBoxLayout()
        vboxpars = QVBoxLayout()
        hbox_bglims = QHBoxLayout()
        hbox_bgpars = QHBoxLayout()
        BBox_layout= QHBoxLayout()
        CBox_layout= QHBoxLayout()

        hbox_main = QHBoxLayout()

        vbox_select.addWidget(self.bgSpecSelect)
        vbox_select.addWidget(self.bgTypeBox)

        hbox_bglims.addWidget(self.minBox)
        hbox_bglims.addWidget(self.maxBox)
        vbox_select.addLayout(hbox_bglims)

        hbox_bgpars.addWidget(self.parB_Box)
        hbox_bgpars.addWidget(self.parB_cb)
        hbox_bgpars.addWidget(self.parC_Box)
        hbox_bgpars.addWidget(self.parC_cb)

        BBox_layout.addWidget(self.BminBox)
        BBox_layout.addWidget(self.Bslider)
        BBox_layout.addWidget(self.BmaxBox)

        CBox_layout.addWidget(self.CminBox)
        CBox_layout.addWidget(self.Cslider)
        CBox_layout.addWidget(self.CmaxBox)

        vboxpars.addLayout(hbox_bgpars)
        vboxpars.addLayout(BBox_layout)
        vboxpars.addLayout(CBox_layout)

        hbox_main.addLayout(vbox_select)
        hbox_main.addLayout(vboxpars)
        hbox_main.addWidget(self.setBG_Button)

        hbox_main.addWidget(self.BGSubtract_Button)

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox_main)


        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)



    def create_status_bar(self):
        self.status_text = QLabel("This is a demo")
        self.statusBar().addWidget(self.status_text, 1)
        
    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu("&File")
        
        open_file_action = self.create_action("&Open file", slot=self.load_file,
            shortcut="Ctrl+O", tip="Open a file")

        save_file_action = self.create_action("&Save plot",
            shortcut="Ctrl+S", slot=self.save_plot, 
            tip="Save the plot")

        quit_action = self.create_action("&Quit", slot=self.close, 
            shortcut="Ctrl+Q", tip="Close the application")
        
        self.add_actions(self.file_menu, 
            (open_file_action, save_file_action, None, quit_action))
        
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About the demo')
        
        self.add_actions(self.help_menu, (about_action,))

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(  self, text, slot=None, shortcut=None, 
                        icon=None, tip=None, checkable=False):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            action.triggered.connect(slot)
        if checkable:
            action.setCheckable(True)
        return action

