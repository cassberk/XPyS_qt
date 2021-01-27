from ipywidgets.widgets import Label, FloatProgress, FloatSlider, Button, Checkbox,FloatRangeSlider, Button, Text,FloatText,\
Dropdown,SelectMultiple, Layout, HBox, VBox, interactive, interact, Output,jslink
from IPython.display import display, clear_output
from ipywidgets import GridspecLayout
from ipywidgets.widgets.interaction import show_inline_matplotlib_plots

import time
import threading
import logging
import math
import numpy as np
from copy import deepcopy as dc
import matplotlib.pyplot as plt
from tqdm import tqdm_notebook as tqdm
import pickle
import lmfit as lm
# from lmfit.model import load_model

import sys
sys.path.append("/Volumes/GoogleDrive/My Drive/XPS/XPS_Library")
import xps
# from xps.io import loadmodel
from xps import bkgrds as background_sub
from xps.helper_functions import *
from xps.gui_element_dicts import *
from xps.auto_fitting import *

import os
import glob

"""Load pre-defined models fitting"""

def loadmodel(element):

    f = open('/Volumes/GoogleDrive/My Drive/XPS/XPS_Library/xps/models/load_model_info.pkl', 'rb')   # 'r' for reading; can be omitted
    load_dict = pickle.load(f)         # load file content as mydict
    f.close() 

    mod = lm.model.load_model(load_dict[element]['model_path'])
    pars = pickle.load(open(load_dict[element]['params_path'],"rb"))
    pairlist = load_dict[element]['pairlist']
    element_ctrl = load_dict[element]['element_ctrl']

    return mod, pars, pairlist, element_ctrl

class xps_spec:

    def __init__(self,sample_object,orbital,parameters=None,model=None,pairlist=None,element_ctrl=None,\
        spectra_name = None, carbon_adjust = None,load_spectra_object = False,load_model = False, autofit = False):

        if load_spectra_object == False:
        
            self.parent_sample = sample_object.sample_name
            self.orbital = orbital
            if spectra_name == None:
                self.spectra_name = dc(self.parent_sample + '_' + orbital)
            else:
                self.spectra_name = spectra_name + '_' + orbital

            self.carbon_adjust = carbon_adjust
            
            if self.carbon_adjust:
                print('Adjusted energy to carbon reference')
                self.E = dc(sample_object.data[orbital]['esub']) - self.carbon_adjust
            else:
                self.E = dc(sample_object.data[orbital]['esub'])
            self.I = dc(sample_object.data[orbital]['isub'])
            
            self.data = dc(sample_object.data[orbital])

            if load_model == False:
                self.params_full = parameters
                self.mod = model
                self.pairlist = pairlist
                self.element_ctrl = element_ctrl
            else:
                self.mod, self.params_full, self.pairlist, self.element_ctrl = loadmodel(load_model)

            if type(self.params_full) == list:
                self.params = dc(self.params_full[0])
            else:
                self.params = dc(self.params_full)

            self.autofit = autofit
            self.leglist = ['Data','Fit Guess'] + [self.pairlist[i][0] for i in range(len(self.pairlist))]
            self.prefixlist = [self.mod.components[i].prefix for i in range(len(self.mod.components))]


        elif load_spectra_object == True:

            spectra_path = os.path.join('/Volumes/GoogleDrive/My Drive/XPS/XPS_Library/xps/samples',\
                            sample_object,orbital)
            f = open(os.path.join(spectra_path,'spectra_attributes.pkl'), 'rb')   
            savedict_load = pickle.load(f)         
            f.close() 

            """Here is a list of all the spectra object parameters. Although, this may change and should be updated
            accordingly
            parent_sample_object, orbital, spectra_name, carbon_adjust, 'E', 'I', 
            'data', 'loaded_params', 'params_full', 'params', 'pairlist', 'leglist', 'prefixlist', 
            'BE_adjust', 'fit_iter_idx', 'fit_results_idx', 'plot_idx', 'fig', 'axs', 'adjusted_oxide_percentage', 
            'thickness', 'element_ctrl'
            """

            for key in savedict_load:
                self.__dict__[key] = savedict_load[key]

            self.mod = lm.model.load_model(os.path.join(spectra_path,self.spectra_name+'_model.sav'))

            fit_result_path_list = [f for f in glob.glob(spectra_path+"/*.sav") \
                if 'fit_result' in f]
            self.fit_results = [lm.model.load_modelresult(fit_result_path_list[i]) for i in range(len(fit_result_path_list))]


