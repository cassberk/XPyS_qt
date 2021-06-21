import sys, os, random
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import lmfit as lm
import pickle
import os
sys.path.append("/Users/cassberk/code")
import XPyS.io
import XPyS.sample
import XPyS.models


from copy import deepcopy as dc

from parameter_gui import ParameterWindow
import data_tree

from IPython import embed as shell



class OverviewWindow(QMainWindow):
    
    def __init__(self, parent = None, sample_obj=None,which_plot = None):
        QMainWindow.__init__(self, parent)

        self.setWindowTitle('An lmfit Experience')


        self.sample = sample_obj
        self.which_plot = which_plot

        self.create_menu()
        self.create_main_frame()
        
        self.create_status_bar()
        self.textbox.setText('1 2 3 4')
        self.update_plot()

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

        # for ax in self.axes:
        #     ax.cla()        

        # self.sample.plot_all_spectra(offval = 0, plotspan = True, fig = self.fig, ax = self.axes,saveflag=0,filepath = '',figdim=(15,10))
        print('yee')
        self.fig.tight_layout()
        self.canvas.draw()
        # self.canvas.draw()

    """Build the Main window"""
    def create_main_frame(self):
        self.main_frame = QWidget()
        
        """Create the mpl Figure and FigCanvas objects. 
        5x4 inches, 100 dots-per-inch
        """
        self.dpi = 100
        # self.fig = Figure((5.0, 4.0), dpi=self.dpi)
        # self.canvas = FigureCanvas(self.fig)
        # self.canvas.setParent(self.main_frame)
        
        """Since we have only one plot, we can use add_axes 
        instead of add_subplot, but then the subplot
        configuration tool in the navigation toolbar wouldn't
        work.
        """
        # self.fig,self.axes = plt.subplots(int(np.ceil((len(self.sample.element_scans)+2)/3)) ,3,figsize = (5.0, 4.0), dpi=self.dpi)
        # self.axes = self.axes.ravel()
        done_it = {spectra:False for spectra in self.sample.all_scans}

        if self.which_plot == 'raw':
            self.fig, self.axes = self.sample.plot_all_spectra(offval = 0, plotspan = True,saveflag=0,filepath = '',figdim=(15,10),done_it = done_it)
        elif self.which_plot == 'bg':
            self.fig, self.axes = self.sample.plot_all_sub()
        elif self.which_plot == 'atomic_percent':
            self.fig, self.axes = self.sample.plot_atomic_percent()

        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        self.canvas.draw()
        self.fig.tight_layout()
        
        """Bind the 'pick' event for clicking on one of the bars"""
        self.canvas.mpl_connect('pick_event', self.on_pick)
        
        """Create the navigation toolbar, tied to the canvas"""
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
        
        """Other GUI controls"""
        self.textbox = QLineEdit()
        self.textbox.setMinimumWidth(200)
        self.textbox.editingFinished.connect(self.update_plot)

        # self.adj_params_button = QPushButton("Adjust Params")
        # self.adj_params_button.clicked.connect(self.show_params_window)

        # self.load_model_button = QPushButton("Load Model")
        # self.load_model_button.clicked.connect(self.choose_model)

        # self.fit_button = QPushButton("Fit")
        # self.fit_button.clicked.connect(self.fit_spectra)

        self.grid_cb = QCheckBox("Show &Grid")
        self.grid_cb.setChecked(False)
        self.grid_cb.stateChanged.connect(self.update_plot)

        # self.spectra_plot_box = QSpinBox()
        # self.spectra_plot_box.setMaximum(len(self.spectra_obj.isub)-1)
        # self.spectra_plot_box.setMinimum(0)
        # self.spectra_plot_box.valueChanged.connect(self.update_plot)

        # self.fit_result_cb = QCheckBox("Fit Results")
        # self.fit_result_cb.setChecked(False)
        # self.fit_result_cb.stateChanged.connect(self.update_plot)
        # self.canvas.draw()






        """Layout with box sizers"""
        hbox = QHBoxLayout()
        
        for w in [self.grid_cb]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)

        # hboxmain = QHBoxLayout()
        # hboxmain.addLayout(vbox)
        # hboxmain.addWidget(self.spectra_tree)

        
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

