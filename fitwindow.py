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
import xps_peakfit.models.models
from xps_peakfit.gui_element_dicts import *
from copy import deepcopy as dc

from parameter_gui import ParameterWindow
import data_tree
from qtio import load_sample

from IPython import embed as shell

class OptionListWindow(QWidget):

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
        self.setWindowTitle('Choose Model')
        self.show()

class QParameter(QWidget,lm.parameter.Parameter):
    valueChanged = pyqtSignal(object)

    def __init__(self, parameter=None):
        super(QParameter, self).__init__(name = parameter.name, value=parameter.value, vary=parameter.vary, min=parameter.min, max=parameter.max,
                 expr=parameter.expr, brute_step=parameter.brute_step, user_data=parameter.user_data)
        self._par = parameter

    @property
    def value(self):
        return self._par.value

    @value.setter
    def value(self, val):
        self._par.set(value = val)
        self.valueChanged.emit(val)

    @property
    def expr(self):
        return self._par.expr

    @expr.setter
    def expr(self, exp):
        self._par.set(expr = exp)
        self.valueChanged.emit(exp)

    def slotvalue(self,v):
        if v > self._par.min:
            v = self._par.min
        self._par.set(value = v)


    # @property
    # def min(self):
    #     return self._par.min

    # @min.setter
    # def min(self, m):
    #     self._par.set(min = m)
    #     self.valueChanged.emit(m)

    # @property
    # def max(self):
    #     return self._par.max

    # @max.setter
    # def expr(self, M):
    #     self._par.set(max = M)
    #     self.valueChanged.emit(M)

    # @property
    # def vary(self):
    #     return self._par.vary

    # @vary.setter
    # def expr(self, v):
    #     self._par.set(vary = v)
    #     self.valueChanged.emit(v)


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
        if hasattr(self.spectra_obj,'params'):
            self.params = {par:QParameter(parameter = self.spectra_obj.params[par]) for par in spectra_obj.params.keys()}
        # self.params = ParSignal(parameter = spectra_obj.params['Nb_52_amplitude'])
        # shell()
        # print(self.spectra_obj.mod)
        # self.par = QParameter(parameter = spectra_obj.params['Nb_52_amplitude'])
        # print(self.par)
        # print(self.spectra_obj.params['Nb_52_amplitude'])
        # shell()
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
            if hasattr(self.spectra_obj,'params'):
                self.axes.plot(self.spectra_obj.esub, self.spectra_obj.mod.eval(self.params, x = self.spectra_obj.esub))
                for pairs in enumerate(self.spectra_obj.pairlist):
                    self.axes.fill_between(self.spectra_obj.esub,\
                        sum([self.spectra_obj.mod.eval_components(params = self.params,x = self.spectra_obj.esub)[comp] for comp in pairs[1]]), \
                            color = element_color[pairs[1][0]],alpha=0.3)

        elif self.fit_result_cb.isChecked():
            self.axes.plot(self.spectra_obj.esub, self.spectra_obj.isub[self.spectra_plot_box.value()],'o')
            if hasattr(self.spectra_obj,'fit_results') and (self.spectra_obj.fit_results[self.spectra_plot_box.value()] != []):
                self.axes.plot(self.spectra_obj.esub, self.spectra_obj.mod.eval(self.spectra_obj.fit_results[self.spectra_plot_box.value()].params, x = self.spectra_obj.esub))
                for pairs in enumerate(self.spectra_obj.pairlist):
                    self.axes.fill_between(self.spectra_obj.esub,\
                        sum([self.spectra_obj.mod.eval_components(params = self.spectra_obj.fit_results[self.spectra_plot_box.value()].params,x = self.spectra_obj.esub)[comp] for comp in pairs[1]]), \
                            color = element_color[pairs[1][0]],alpha=0.3)
        


        self.axes.set_xlabel('Binding Energy (eV)',fontsize=24)
        self.axes.set_ylabel('Counts/sec',fontsize=24)
        self.axes.set_xlim(np.max(self.spectra_obj.esub),np.min(self.spectra_obj.esub))
        self.axes.tick_params(labelsize=20)
        self.fig.tight_layout()
        self.canvas.draw()



    def autofit(self):
        sender = self.sender()
        if sender.objectName() == 'afButton':
            self.spectra_obj.autofit = xps_peakfit.autofit.autofit.autofit(self.spectra_obj.esub,self.spectra_obj.isub[self.spectra_plot_box.value()],self.spectra_obj.orbital)

        if self.autofit_cb.isChecked():
            if not hasattr(self.spectra_obj,'autofit'):
                self.spectra_obj.autofit = xps_peakfit.autofit.autofit.autofit(self.spectra_obj.esub,self.spectra_obj.isub[self.spectra_plot_box.value()],self.spectra_obj.orbital)
            elif hasattr(self,'autofit'):
                self.spectra_obj.autofit.guess_params(energy = self.spectra_obj.esub,intensity = self.spectra_obj.isub[self.spectra_plot_box.value()])
            for par in self.spectra_obj.autofit.guess_pars.keys():
                self.spectra_obj.params[par].value = self.spectra_obj.autofit.guess_pars[par]
                print(par,self.spectra_obj.autofit.guess_pars[par])
            self.update_plot()

    # self.autofit = xps_peakfit.autofit.autofit.autofit(self.spectra_object.esub,self.spectra_object.isub[specnum[0]],self.spectra_object.orbital)

    def connect_sampletree(self):
        # self.sampletreeWindow.button.clicked.connect(self.plot_tree_choices)  # Not sure why this is here, clicking on window initiates self.plot_tree_choices
        self.sampletreeWindow.tree.itemChanged[QTreeWidgetItem, int].connect(self.plot_tree_choices)
        

    """Here we build the window to interactively change the parameters"""
    def show_params_window(self):
        if not hasattr(self.spectra_obj,'mod'):
            print('No Model Loaded')
            return
        if self.paramsWindow is None:

            self.paramsWindow = ParameterWindow(model = self.spectra_obj.mod, pairlist = self.spectra_obj.pairlist, \
                element_ctrl = self.spectra_obj.element_ctrl, params = self.params, E = self.spectra_obj.E)

            self.paramsWindow.show()
            self.connect_parameters()

        else:
            self.paramsWindow.close()
            self.paramsWindow = None  # Discard reference, close window.
            # self.disconnect_parameter()

  
    def connect_parameters(self):
        for par in self.paramsWindow.paramwidgets.keys():

            # Connect QParameter and Slider
            self.paramsWindow.paramwidgets[par].slider.valueChanged.connect(self.update_Qpar_val_from_slider)
            self.params[par].valueChanged.connect(self.update_slider)

            # Connect QParameter and Numbox
            self.paramsWindow.paramwidgets[par].numbox.valueChanged.connect(self.update_Qpar_val_from_numbox)
            self.params[par].valueChanged.connect(self.update_numbox)
            self.paramsWindow.paramwidgets[par].minbox.valueChanged.connect(self.update_min)
            self.paramsWindow.paramwidgets[par].maxbox.valueChanged.connect(self.update_max)
            self.paramsWindow.paramwidgets[par].expr_text.editingFinished.connect(self.update_expr)
            self.paramsWindow.paramwidgets[par].groupbox.toggled.connect(self.update_vary)

    def update_Qpar_val_from_slider(self,v):
        sender = self.sender()

        n = self.paramsWindow.paramwidgets[sender.objectName()].N
        m = self.paramsWindow.paramwidgets[sender.objectName()].ctrl_limits_min
        M = self.paramsWindow.paramwidgets[sender.objectName()].ctrl_limits_max
        pval = np.round(100*(m + v*(M - m)/n))/100

        self.params[sender.objectName()].set(value = pval )
        self.update_plot()

    def update_Qpar_val_from_numbox(self,v):
        sender = self.sender()
        nval = np.round(100*v)/100

        self.params[sender.objectName()].set(value = nval )
        self.update_plot()

    def update_slider(self, v):
        sender = self.sender()
        m = self.paramsWindow.paramwidgets[sender.name].ctrl_limits_min
        M = self.paramsWindow.paramwidgets[sender.name].ctrl_limits_max
        slideval = np.round( (v - m)/( (M-m)/self.paramsWindow.paramwidgets[sender.name].N ) )
        self.paramsWindow.paramwidgets[sender.name].slider.setValue(slideval)
        # self.update_plot()

    def update_numbox(self, v):
        sender = self.sender()
        parval = np.round(100*v)/100
        self.paramsWindow.paramwidgets[sender.name].numbox.setValue(parval)

    def update_min(self,minimum):
        sender = self.sender()
        # shell()
        self.spectra_obj.params[sender.objectName()].min = minimum
        self.params[sender.objectName()].min = minimum

    def update_max(self,maximum):
        sender = self.sender()
        # shell()
        self.spectra_obj.params[sender.objectName()].max = maximum 
        self.params[sender.objectName()].max = maximum 

    def update_expr(self,expression):
        sender = self.sender()
        self.spectra_obj.params[sender.objectName()].set(expr = expression )
        self.params[sender.objectName()].set(expr = expression )
        self.update_plot()

    def update_vary(self,var):
        sender = self.sender()
        print(var)
        self.spectra_obj.params[sender.title()].set(vary = var)
        self.params[sender.title()].set(vary = var)
        self.update_plot()
        # print(vary)


    def load_model(self):
        # model_filename = self.spectra_obj.orbital
        # model_filepath = find_files(model_filename,'/Users/cassberk/code/xps_peakfit/models/self.spectra_obj.orbital')

        ldd_mod = xps_peakfit.models.models.load_model(self.ModelListWindow.listWidget.selectedItems()[0].text())
        self.spectra_obj.mod = ldd_mod[0]
        self.spectra_obj.params = ldd_mod[1]
        self.spectra_obj.pairlist = ldd_mod[2]
        self.spectra_obj.element_ctrl = ldd_mod[3]
        self.params = {par:QParameter(parameter = self.spectra_obj.params[par]) for par in self.spectra_obj.params.keys()}
        self.ModelListWindow.close()

    def choose_model(self):
        self.ModelListWindow = OptionListWindow(xps_peakfit.models.models.model_list(startpath = os.path.join('/Users/cassberk/code/xps_peakfit/models',self.spectra_obj.orbital)))
        self.ModelListWindow.ExperimentSelectButton.clicked.connect(self.load_model)
        self.ModelListWindow.show()


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


        self.spectra_obj.fit(specific_points = fitlist,autofit = self.autofit_cb.isChecked(), update_with_prev_pars = self.update_prev_pars_cb.isChecked(),plotflag = False, track = False)
        self.update_plot()

    def fit_result_to_params(self):

        self.spectra_obj.params = self.spectra_obj.fit_results[self.spectra_plot_box.value()].params.copy() 
        self.params = {par:QParameter(parameter = self.spectra_obj.params[par]) for par in self.spectra_obj.params.keys()}



    """Build the Main window"""
    def create_main_frame(self):
        self.main_frame = QWidget()
        
        """Create the mpl Figure and FigCanvas objects. 
        5x4 inches, 100 dots-per-inch
        """
        self.dpi = 100
        self.fig = Figure((7.0, 6.0), dpi=self.dpi)
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

        self.load_model_button = QPushButton("Load Model")
        self.load_model_button.clicked.connect(self.choose_model)

        self.fit_button = QPushButton("Fit")
        self.fit_button.clicked.connect(self.fit_spectra)

        self.grid_cb = QCheckBox("Show &Grid")
        self.grid_cb.setChecked(False)
        self.grid_cb.stateChanged.connect(self.update_plot)

        self.spectra_plot_box = QSpinBox()
        self.spectra_plot_box.setMaximum(len(self.spectra_obj.isub)-1)
        self.spectra_plot_box.setMinimum(0)
        self.spectra_plot_box.valueChanged.connect(self.autofit)
        self.spectra_plot_box.valueChanged.connect(self.update_plot)

        self.fit_result_to_param_button = QPushButton("Fit Result to Params")
        self.fit_result_to_param_button.clicked.connect(self.fit_result_to_params)


        self.fit_result_cb = QCheckBox("Fit Results")
        self.fit_result_cb.setChecked(False)
        self.fit_result_cb.stateChanged.connect(self.update_plot)

        self.autofitButton = QPushButton("Autofit")
        self.autofitButton.clicked.connect(self.autofit)
        self.autofitButton.setObjectName('afButton')

        self.autofit_cb = QCheckBox("Autofit")
        self.autofit_cb.setChecked(False)

        self.update_prev_pars_cb = QCheckBox("Update with prev pars")
        self.update_prev_pars_cb.setChecked(False)
        # self.autofit_cb.stateChanged.connect(self.autofit)

# self.autofit = xps_peakfit.autofit.autofit.autofit(self.spectra_object.esub,self.spectra_object.isub[specnum[0]],self.spectra_object.orbital)
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
        
        fitControlLayout = QVBoxLayout()
        fitControlLayout.addWidget(self.fit_button)
        fitControlLayout.addWidget(self.update_prev_pars_cb)

        specControlLayout = QVBoxLayout()
        specControlLayout.addWidget(self.spectra_plot_box)
        specControlLayout.addWidget(self.fit_result_to_param_button)

        for w in [self.adj_params_button,self.load_model_button, fitControlLayout, self.grid_cb, self.autofitButton, self.autofit_cb,self.fit_result_cb, specControlLayout]:
            if (w is fitControlLayout) or (w is specControlLayout):
                hbox.addLayout(w)
            else:
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

