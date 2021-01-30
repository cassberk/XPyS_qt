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
import data_tree
from qtio import load_sample

from IPython import embed as shell

# class ParSignal(QWidget,lm.parameter.Parameter):
#     valueChanged = pyqtSignal(object)

#     def __init__(self, parameter=None):
#         super(ParSignal, self).__init__(name = parameter.name)
#         self._par = parameter

#     @property
#     def value(self):
#         return self._par.value

#     @value.setter
#     def value(self, val):
#         self._par.set(value = val)
#         self.valueChanged.emit(val)

class FitViewWindow(QMainWindow):
    
    def __init__(self, parent = None, spectra_obj=None):
        QMainWindow.__init__(self, parent)

        self.setWindowTitle('An lmfit Experience')
        self.paramsWindow = None
        self.sampletreeWindow = None

        # self.mod = None
        self.spectra_obj = spectra_obj
        # shell()
        # self.params = {}
        # for par in spectra_obj.params.keys():
            # self.params[par] = ParSignal(parameter = spectra_obj.params[par])
        # self.params = ParSignal(parameter = spectra_obj.params['Nb_52_amplitude'])
        # shell()
        # print(self.spectra_obj.mod)

        self.create_menu()
        self.create_main_frame()
        
        self.create_status_bar()
        self.textbox.setText('1 2 3 4')
        self.update_plot()
        # shell()
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
        # print(self.spectra_plot_box.value())
        # print(self.fit_result_cb.value())
        # print(self.fit_result_cb.isChecked())
        self.axes.cla()        

        self.axes.grid(self.grid_cb.isChecked())
        

        if not self.fit_result_cb.isChecked():
            self.axes.plot(self.spectra_obj.esub, self.spectra_obj.isub[self.spectra_plot_box.value()],'o')
            self.axes.plot(self.spectra_obj.esub, self.spectra_obj.mod.eval(self.spectra_obj.params, x = self.spectra_obj.esub))
            for pairs in enumerate(self.spectra_obj.pairlist):
                self.axes.fill_between(self.spectra_obj.esub,\
                    sum([self.spectra_obj.mod.eval_components(params = self.spectra_obj.params,x = self.spectra_obj.esub)[comp] for comp in pairs[1]]), alpha=0.3)

        elif self.fit_result_cb.isChecked():
            self.axes.plot(self.spectra_obj.esub, self.spectra_obj.isub[self.spectra_plot_box.value()],'o')
            self.axes.plot(self.spectra_obj.esub, self.spectra_obj.mod.eval(self.spectra_obj.fit_results[self.spectra_plot_box.value()].params, x = self.spectra_obj.esub))
            for pairs in enumerate(self.spectra_obj.pairlist):
                self.axes.fill_between(self.spectra_obj.esub,\
                    sum([self.spectra_obj.mod.eval_components(params = self.spectra_obj.fit_results[self.spectra_plot_box.value()].params,x = self.spectra_obj.esub)[comp] for comp in pairs[1]]), alpha=0.3)
        


        self.axes.set_xlabel('Binding Energy (eV)',fontsize=30)
        self.axes.set_ylabel('Counts/sec',fontsize=30)
        self.axes.set_xlim(np.max(self.spectra_obj.esub),np.min(self.spectra_obj.esub))
        self.axes.tick_params(labelsize=20)
        self.fig.tight_layout()
        self.canvas.draw()

    def connect_sampletree(self):
        # self.sampletreeWindow.button.clicked.connect(self.plot_tree_choices)  # Not sure why this is here, clicking on window initiates self.plot_tree_choices
        self.sampletreeWindow.tree.itemChanged[QTreeWidgetItem, int].connect(self.plot_tree_choices)
        

    """Here we build the window to interactively change the parameters"""
    def show_params_window(self):
        if self.paramsWindow is None:

            self.paramsWindow = ParameterWindow(model = self.spectra_obj.mod, pairlist = self.spectra_obj.pairlist, \
                element_ctrl = self.spectra_obj.element_ctrl, params = self.spectra_obj.params, E = self.spectra_obj.E)

            self.paramsWindow.show()
            shell()
            self.connect_parameters()

        else:
            self.paramsWindow.close()
            self.paramsWindow = None  # Discard reference, close window.
            # self.disconnect_parameter()

  
    def connect_parameters(self):
        for par in self.paramsWindow.paramwidgets.keys():

            self.paramsWindow.paramwidgets[par].slider.valueChanged.connect(self.update_val)
            self.paramsWindow.paramwidgets[par].minbox.editingFinished.connect(self.update_min)
            self.paramsWindow.paramwidgets[par].maxbox.editingFinished.connect(self.update_max)
            self.paramsWindow.paramwidgets[par].expr_text.editingFinished.connect(self.update_expr)
            self.paramsWindow.paramwidgets[par].groupbox.toggled.connect(self.update_vary)

    def update_val(self,v):
        sender = self.sender()

        n = self.paramsWindow.paramwidgets[sender.objectName()].N
        m = self.paramsWindow.paramwidgets[sender.objectName()].ctrl_limits_min
        M = self.paramsWindow.paramwidgets[sender.objectName()].ctrl_limits_max
        pval = np.round(100*(m + v*(M - m)/n))/100

        self.spectra_obj.params[sender.objectName()].set(value = pval )
        print('signalpar',self.paramsWindow.paramwidgets[sender.objectName()].par.value)
        print('spec ob par',self.spectra_obj.params[sender.objectName()].value)
        # print(str(sender.value())+' '+str(self.params[sender.objectName()].value))
        self.update_plot()

    def update_min(self,minimum):
        sender = self.sender()
        self.spectra_obj.params[sender.objectName()].set(min= minimum )
        self.update_plot()

    def update_max(self,maximum):
        sender = self.sender()
        self.spectra_obj.params[sender.objectName()].set(max = maximum )
        self.update_plot()

    def update_expr(self,expression):
        sender = self.sender()
        self.spectra_obj.params[sender.objectName()].set(expr = expression )
        self.update_plot()

    def update_vary(self,var):
        sender = self.sender()
        self.spectra_obj.params[sender.title()].set(vary = var)
        self.update_plot()
        # print(vary)


    """Here we build the window to fit the spectra"""
    def fit_spectra(self):

        fitlist = []
        iterator = QTreeWidgetItemIterator(self.spectra_tree, QTreeWidgetItemIterator.Checked)
        while iterator.value():
            item = iterator.value()
            if item.text(0) != 'All':
                fitlist.append(int(item.text(0)))
            iterator += 1
        print(fitlist)


        self.spectra_obj.fit(specific_points = fitlist,plotflag = False, track = False)
        self.update_plot()

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
        self.textbox = QLineEdit()
        self.textbox.setMinimumWidth(200)
        self.textbox.editingFinished.connect(self.update_plot)

        self.adj_params_button = QPushButton("Adjust Params")
        self.adj_params_button.clicked.connect(self.show_params_window)

        self.fit_button = QPushButton("Fit")
        self.fit_button.clicked.connect(self.fit_spectra)

        self.grid_cb = QCheckBox("Show &Grid")
        self.grid_cb.setChecked(False)
        self.grid_cb.stateChanged.connect(self.update_plot)

        self.spectra_plot_box = QSpinBox()
        self.spectra_plot_box.setMaximum(len(self.spectra_obj.isub)-1)
        self.spectra_plot_box.setMinimum(0)
        self.spectra_plot_box.valueChanged.connect(self.update_plot)

        self.fit_result_cb = QCheckBox("Fit Results")
        self.fit_result_cb.setChecked(False)
        self.fit_result_cb.stateChanged.connect(self.update_plot)

        # slider_label = QLabel('Set xlims:')
        # self.slider = QSlider(Qt.Horizontal)
        # self.slider.setRange(np.min(self.spectra_obj.esub), np.max(self.spectra_obj.esub))
        # self.slider.setValue(np.min(self.spectra_obj.esub))
        # self.slider.setTracking(True)
        # self.slider.setTickPosition(QSlider.TicksBothSides)
        # self.slider.valueChanged.connect(self.update_plot)



        """Tree for choosing which spectra to fit/view"""
        self.spectra_tree = QTreeWidget(self)
        parent = QTreeWidgetItem(self.spectra_tree)
        parent.setText(0,'All')

        parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

        for ch in [str(i) for i in range(len(self.spectra_obj.isub))]:
            child1 = QTreeWidgetItem(parent)
            child1.setFlags(child1.flags() | Qt.ItemIsUserCheckable)
            child1.setText(0, ch)
            child1.setCheckState(0, Qt.Unchecked)      

        """Layout with box sizers"""
        hbox = QHBoxLayout()
        
        for w in [self.adj_params_button, self.fit_button, self.grid_cb, self.fit_result_cb, self.spectra_plot_box]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)

        hboxmain = QHBoxLayout()
        hboxmain.addLayout(vbox)
        hboxmain.addWidget(self.spectra_tree)

        
        self.main_frame.setLayout(hboxmain)
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

