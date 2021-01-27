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
sys.path.append("/Volumes/GoogleDrive/My Drive/XPS/XPS_Library")
import xps.io
from copy import deepcopy as dc

from parameter_gui import ParameterWindow
import data_tree
from qtio import load_sample

from IPython import embed as shell


class FitViewWindow(QMainWindow):
    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.setWindowTitle('An lmfit Experience')
        self.paramsWindow = None
        self.sampletreeWindow = None

        self.mod = None

        self.loaded_samples = {}
        self.ddict, self.xpssamp = load_sample()
        self.loaded_samples[self.xpssamp.sample_name] = self.xpssamp
        # del self.xpssamp
        print('loaded smple')
        print(self.loaded_samples.keys())

        # self.params = self.xpssamp.Nb3d.params
        # self.mod = self.xpssamp.Nb3d.mod
        # self.pairlist = self.xpssamp.Nb3d.pairlist
        # self.element_ctrl = self.xpssamp.Nb3d.element_ctrl
        # self.E = self.xpssamp.Nb3d.E

        self.show_sampletree_window(treeparent = self.ddict['sample_name'], \
            treechildren = self.ddict['element_scans'])

        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()
        self.textbox.setText('1 2 3 4')
        # self.update_plot()

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
    
    def update_plot(self,sample = None,data = None):
        """ Redraws the figure
        """
        str = self.textbox.text().encode('utf-8')
        # self.data = [int(s) for s in str.split()]
        
        # x = range(len(self.data))

        # clear the axes and redraw the plot anew
        #
        print('inplot')
        # self.axes.clear()
        self.axes.cla()        

        self.axes.grid(self.grid_cb.isChecked())
        

        if self.mod is not None:
            self.axes.plot(self.E, self.I[0],'o')
            self.axes.plot(self.E, self.mod.eval(self.params, x = self.E))
            for pairs in enumerate(self.pairlist):
                self.axes.fill_between(self.E,\
                    sum([self.mod.eval_components(params = self.params,x = self.E)[comp] for comp in pairs[1]]), alpha=0.3)
        
        # if sample is not None:
        #     plotsamp = sample.__dict__[data]
        #     self.axes.plot(plotsamp.E, plotsamp.data['isub'][0],'o')
        #     self.axes.plot(plotsamp.E, plotsamp.mod.eval(plotsamp.params, x = plotsamp.E))
        #     for pairs in enumerate(plotsamp.pairlist):
        #         self.axes.fill_between(plotsamp.E,\
        #             sum([plotsamp.mod.eval_components(params = plotsamp.params,x = plotsamp.E)[comp] for comp in pairs[1]]), alpha=0.3)
                    
                                                            # color = element_color[pairs[1][0]], alpha=0.3)

        # p2 = plt.plot(self.E,self.mod.eval(self.params,x=self.E) , color = 'black')
        if self.mod is not None:
            self.axes.set_xlabel('Binding Energy (eV)',fontsize=30)
            self.axes.set_ylabel('Counts/sec',fontsize=30)
            self.axes.set_xlim(np.max(self.E),np.min(self.E))
            self.axes.tick_params(labelsize=20)
            self.fig.tight_layout()
        self.canvas.draw()

    """A QTree Widget Window for controlling which samples are plotted and fit"""
    def show_sampletree_window(self,treeparent = None, treechildren = None):
        if self.sampletreeWindow is None:
            self.sampletreeWindow = data_tree.DataTreeHandler(treeparent = treeparent,treechildren=treechildren)
            self.sampletreeWindow.show()
            self.connect_sampletree()
            # shell()

        else:
            self.sampletreeWindow.close()
            self.sampletreeWindow = None  # Discard reference, close window.
            # self.disconnect_parameter()

    def connect_sampletree(self):
        # self.sampletreeWindow.button.clicked.connect(self.plot_tree_choices)  # Not sure why this is here, clicking on window initiates self.plot_tree_choices
        self.sampletreeWindow.tree.itemChanged[QTreeWidgetItem, int].connect(self.plot_tree_choices)
        
        # self.sampletreeWindow.tree.itemClicked[QTreeWidgetItem, int].connect(self.plot_tree_choices)

    # def plot_tree_choices(self, item, column):
    #     print(item.text(0))
    #     if item.checkState(column) == Qt.Checked:
    #         print(item.text(0),'Item Checked')
    #         self.update_plot(sample = self.xpssamp,data = item.text(0))

    #     elif item.checkState(column) == Qt.Unchecked:
    #         print('yay')
            # shell()
            # print(item.text(0),'Item Unchecked')
            # print(dir(item.parent))
            # print(item.parent())
            # print(item.parent().text(0))
            # self.canvas.axes.cla()

    def plot_tree_choices(self,val, column):
    #     sender = self.sender()
    #     print('itemclicked')
    #     # print(self.sampletreeWindow.updatelist)
    #     # print(dir(sender))
    #     # print(dir(sender.itemWidget))
    #     # print(sender.itemWidget)
    #     # print(sender.text)
    #     # for spec in self.sampletreeWindow.updatelist:
    #     #     self.update_plot(sample = self.xpssamp,data = spec)
    #     # self.create_main_frame()
    #     # print(self.sampletreeWindow.tree.selectedItems())
    #     self.axes.cla()  
        iterator = QTreeWidgetItemIterator(self.sampletreeWindow.tree, QTreeWidgetItemIterator.Checked)
        while iterator.value():
            item = iterator.value()
            if item.text(0) not in self.sampletreeWindow.treeparent:
                # print(item.text(0),item.parent().text(0))
                sample = item.parent().text(0)
                spectra = item.text(0)
                self.mod = self.loaded_samples[sample].__dict__[spectra].mod
                self.pairlist = self.loaded_samples[sample].__dict__[spectra].pairlist
                self.element_ctrl = self.loaded_samples[sample].__dict__[spectra].element_ctrl
                self.params = self.loaded_samples[sample].__dict__[spectra].params
                self.E = self.loaded_samples[sample].__dict__[spectra].E
                self.I = self.loaded_samples[sample].__dict__[spectra].I
                print('wehere')
                self.update_plot(sample = self.loaded_samples[sample],data = item.text(0))
            # print(item.text(0),item.isSelected())
            # print(item.text(0),item.checkState(column))
            iterator += 1
            # if item.text(0) not in self.parent:
            # #     print(item.text(0))
            #     iterlist.append(item.text(0))  


    """Here we build the window to interactively change the parameters"""
    def show_params_window(self):
        if self.paramsWindow is None:
            iterator = QTreeWidgetItemIterator(self.sampletreeWindow.tree, QTreeWidgetItemIterator.Checked)
            while iterator.value():
                item = iterator.value()
                if item.text(0) not in self.sampletreeWindow.treeparent:
                    sample = item.parent().text(0)
                    spectra = item.text(0)
                    # print(item.text(0),item.parent().text(0))
                iterator += 1

            # print(dir(self.loaded_samples[sample].__dict__[spectra].mod))
            self.mod = self.loaded_samples[sample].__dict__[spectra].mod
            self.pairlist = self.loaded_samples[sample].__dict__[spectra].pairlist
            self.element_ctrl = self.loaded_samples[sample].__dict__[spectra].element_ctrl
            self.params = self.loaded_samples[sample].__dict__[spectra].params
            self.E = self.loaded_samples[sample].__dict__[spectra].E
            self.I = self.loaded_samples[sample].__dict__[spectra].I

            self.paramsWindow = ParameterWindow(model = self.mod, pairlist = self.pairlist, \
                element_ctrl = self.element_ctrl, params = self.params, E = self.E)

            self.paramsWindow.show()
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


        m = np.min(self.paramsWindow.ctrl_lims[sender.objectName()])    # Is this inefficient?
        M = np.max(self.paramsWindow.ctrl_lims[sender.objectName()])
        n = self.paramsWindow.paramwidgets[sender.objectName()].N

        pval = np.round(100*(m + v*(M - m)/n))/100

        self.params[sender.objectName()].set(value = pval )

        # print(str(sender.value())+' '+str(self.params[sender.objectName()].value))
        self.update_plot()

    def update_min(self,minimum):
        sender = self.sender()
        self.params[sender.objectName()].set(min= minimum )
        self.update_plot()

    def update_max(self,maximum):
        sender = self.sender()
        self.params[sender.objectName()].set(max = maximum )
        self.update_plot()

    def update_expr(self,expression):
        sender = self.sender()
        self.params[sender.objectName()].set(expr = expression )
        self.update_plot()

    def update_vary(self,var):
        sender = self.sender()
        self.params[sender.title()].set(vary = var)
        self.update_plot()
        # print(vary)


    """Build the Main window"""
# class MainWin(QMainWindow):
#     def __init__(self, parent=None):
#         QMainWindow.__init__(self, parent)

#         self.create_main_frame()

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
        
        self.draw_button = QPushButton("&Draw")
        self.draw_button.clicked.connect(self.update_plot)

        self.fit_button = QPushButton("Fit")
        self.fit_button.clicked.connect(self.show_params_window)

        self.grid_cb = QCheckBox("Show &Grid")
        self.grid_cb.setChecked(False)
        self.grid_cb.stateChanged.connect(self.update_plot)


        slider_label = QLabel('Bar width (%):')
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 100)
        self.slider.setValue(20)
        self.slider.setTracking(True)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.slider.valueChanged.connect(self.update_plot)
        
        """Layout with box sizers"""
        hbox = QHBoxLayout()
        
        for w in [  self.textbox, self.draw_button,self.fit_button, self.grid_cb,
                    slider_label, self.slider]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)
        
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




def main():
    app = QApplication(sys.argv)
    form = FitViewWindow()
    form.show()
    app.exec_()


if __name__ == "__main__":
    main()