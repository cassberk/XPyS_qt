import sys, os, random
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import numpy as np
# import matplotlib
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
# from matplotlib.figure import Figure
import lmfit as lm
import pickle
import os
from qtdata_io import load_excel
sys.path.append("/Volumes/GoogleDrive/My Drive/XPS/XPS_Library")
import xps.io
# from xps.sample import xps_sample
# from xps.spectra import xps_spec
from qtsample import xps_sample
from qtspectra import xps_spec


        # options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        # fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        # if fileName:
def load_sample(sample='Res-025'):
    filepath = os.path.join('/Volumes/GoogleDrive/My Drive/XPS/XPS_Library/xps/samples',\
    sample,'sample_attributes.pkl')
    f = open(filepath, 'rb')   # 'r' for reading; can be omitted
    savedict_load = pickle.load(f)         # pickled dictionary with sample attributes
    f.close() 
    print(savedict_load.keys())
    print(savedict_load['sample_name'])
    print(savedict_load['element_scans'])
    return savedict_load, xps_sample(savedict_load,load_sample_object = True,overview = False)
        # return xps_sample(savedict_load,load_sample_object = True,overview = overview)