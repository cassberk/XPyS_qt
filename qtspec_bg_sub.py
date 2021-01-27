import pandas as pd
from copy import deepcopy as dc
from xps.helper_functions import *
from xps import bkgrds as backsub
from xps.data_io import load_excel
import lmfit as lm
import numpy as np
import matplotlib.pyplot as plt

# from xps.spectra import xps_spec
from qtspectra import xps_spec


from ipywidgets.widgets import Checkbox, Button, Layout, HBox, VBox, Output, Text
import os


def subtr_region(spectra,energy,intensity,crop_details,UT2_params = None):

        if type(crop_details) == tuple:
            croplims = dc(crop_details)

        if type(crop_details) == list:
            
            croplims = dc(crop_details[0])
            subtype = dc(crop_details[1])


        if subtype == 'shirley':
            Ei = [index_of(energy,croplims[0]), index_of(energy,croplims[1])]
            energy_crop = energy[min(Ei):max(Ei)]
            intensity_crop = intensity[min(Ei):max(Ei)]
            bkgrd = backsub.shirley(energy_crop, intensity_crop)
            subtracted = intensity_crop - bkgrd  
            bg_pars = None
            # spectra.bg_pars = None
            # spectra.bg = bkgrd
            # spectra.isub = intensity_crop 
            # spectra.esub = energy_crop

        elif subtype =='linear':
            Ei = [index_of(energy,croplims[0]), index_of(energy,croplims[1])]
            energy_crop = energy[min(Ei):max(Ei)]
            intensity_crop = intensity[min(Ei):max(Ei)]
            bkgrd = backsub.linear(energy_crop, intensity_crop)
            subtracted = intensity_crop - bkgrd
            bg_pars = None
            # spectra.bg_pars = None
            # spectra.bg = bkgrd
            # spectra.isub = intensity_crop 
            # spectra.esub = energy_crop

        elif subtype =='UT2':
            
            if UT2_params is None:
                toupars = lm.Parameters()
                toupars.add('B', value =crop_details[2][0], min = 0,vary = crop_details[2][1])
                toupars.add('C', value =crop_details[2][2], min = 0,vary = crop_details[2][3])
                toupars.add('D', value =0, min = 0,vary = 0)
            
                if crop_details[0] == None:
                    fit_ind = (0,5)
                else:
                    fit_ind = ( index_of(energy,np.max(crop_details[0])),index_of(energy,np.min(crop_details[0])) )
                
                fitter = lm.Minimizer(backsub.Tougaard_fit, toupars,fcn_args=(intensity,energy), fcn_kws={'fit_inds': fit_ind})
                result_tou = fitter.minimize()
                
                bkgrd,subtr = backsub.Tougaard(result_tou.params, intensity,energy)
                bg_pars = result_tou.params
                # spectra.bg = bkgrd
            
            elif UT2_params != None:
                
                bkgrd,subtr = backsub.Tougaard(UT2_params, intensity,energy)
                bg_pars = UT2_params
                # spectra.bg = bkgrd
                
            subtracted = dc(subtr) 
            intensity_crop = dc(intensity - intensity[-1])
            energy_crop = dc(energy)
            # spectra.isub = dc(subtr) 
            # spectra.esub = dc(energy)

        # if (UT2_params is None) & (subtype=='UT2'):
        #     return energy_crop, subtracted, bkgrd, result_tou.params
        return energy_crop, subtracted, bkgrd, bg_pars

