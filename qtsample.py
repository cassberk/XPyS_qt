import pandas as pd
from copy import deepcopy as dc
from xps.helper_functions import *
from xps import bkgrds as backsub
from qtdata_io import load_excel
import lmfit as lm
import numpy as np
import matplotlib.pyplot as plt

# from xps.spectra import xps_spec
from qtspectra import xps_spec


from ipywidgets.widgets import Checkbox, Button, Layout, HBox, VBox, Output, Text
import os


class xps_sample:

    def __init__(self,dataload,bkgrd_sub_dict = None, data_dict_idx = None, overview = True, offval=0, plotflag = True, plotspan = False,\
        normalize_subtraction = False,load_sample_object = False,name = None):

        if load_sample_object == False:
            if type(dataload) == str:
                data_dict = load_excel(dataload)
                self.data_path = dataload

            if type(dataload) == dict:
                data_dict = dc(dataload)

            if (len(list(data_dict.keys())) > 1) & (data_dict_idx == None):
                print('There are more than 1 experiment files in the excel file! Choose data_dict_idx')
                print(list(enumerate(data_dict.keys())))
                return
            elif (len(list(data_dict.keys())) == 1) & (data_dict_idx == None):
                data_dict_idx = 0


            if name == None:
                self.sample_name = list(data_dict.keys())[data_dict_idx]
                # print(self.sample_name)
            else:
                self.sample_name = name

            # dfSF = pd.read_excel(r'G:/My Drive/XPS/XPS_Library/Sensitivity_Factors.xlsx', keep_default_na = False)
            dfSF = pd.read_excel(r'/Volumes/GoogleDrive/My Drive/XPS/XPS_Library/Sensitivity_Factors.xlsx', keep_default_na = False)

            self.RSF = {dfSF['element'][dfSF['SF'] != ''].iloc[i] : dfSF['SF'][dfSF['SF'] != ''].iloc[i] for i in range(len(dfSF[dfSF['SF'] != '']))}
        

            
            self.data = dc(data_dict[list(data_dict.keys())[data_dict_idx]])
            self.bkgrd_sub_dict = dc(bkgrd_sub_dict)
            self.element_scans = [x for x in list(self.data.keys()) if x not in ('total area', 'Valence','XPS')]
            self.offval = offval
            self.plotflag = plotflag
            self.plotspan = plotspan
            self.normalize_subtraction = normalize_subtraction
            analyze = True

        elif load_sample_object == True:
            
            self.sample_name= dataload['sample_name']
            self.data = dataload['data']
            self.data_path = dataload['data_path']
            self.RSF = dataload['RSF']
            self.bkgrd_sub_dict = dataload['bkgrd_sub_dict']
            self.element_scans =dataload['element_scans']
            self.offval = dataload['offval']
            self.plotflag = dataload['plotflag' ]
            self.plotspan = dataload['plotspan']
            self.normalize_subtraction = dataload['normalize_subtraction']
            
            for key in dataload.keys():
                if (key not in self.__dict__.keys()) and (dataload[key] !='spectra_object'):
                    print('you missed a key!!!')
                    print(key)
                # if dataload[key] != 'spectra_object':
                #     self.__dict__[key] = dataload[key]
                    
                if dataload[key] =='spectra_object':
                    print(dataload['sample_name']+'-'+key)

                    self.__dict__[key] = xps_spec(dataload['sample_name'],key,load_spectra_object = True)

            analyze = False
        print(overview)
        if overview:
            self.xps_overview(analyze)


    # ####
    # def xps_overview(self,analyze = True):
        
    #     if analyze == True:





    #         self.bksub_all(cropdic = self.bkgrd_sub_dict)
    #         self.calc_total_area()

    #     if self.plotflag == True:

        #     save_figs_button = Button(description="Save Figures") 

        #     saved_root_name = Text(
        #         value=self.sample_name,
        #         placeholder='Save filename',
        #         disabled=False,
        #         layout = Layout(width = '200px', margin = '0 5px 0 0')
        #         )
        #     save_figs_chkbxs = {init_fig: Checkbox(
        #         value= False,
        #         description=str(init_fig),
        #         style = {'description_width': 'initial'},
        #         disabled=False,
        #         indent=False
        #         ) for init_fig in ['Raw','Subtracted','Atomic Percent'] }

        #     display( VBox( [saved_root_name,HBox( [HBox( list( save_figs_chkbxs[chks] for chks in save_figs_chkbxs.keys() ) ), save_figs_button] ) ] ) )
        #     # out = Output()
        #     # display(out)

            # fig_dict = {}
            # ax_dict = {}
            # fig_dict['Raw'], ax_dict['Raw']= self.plot_all_spectra(cropdic = self.bkgrd_sub_dict, offval = self.offval, plotspan = self.plotspan, saveflag=0,filepath = '',figdim=(15,10))
            # fig_dict['Subtracted'], ax_dict['Subtracted'] = self.plot_all_sub(cropdic = self.bkgrd_sub_dict)
            # fig_dict['Atomic Percent'], ax_dict['Atomic Percent'] = self.plot_atomic_percent()

        #     @save_figs_button.on_click
        #     def save_figs_on_click(b):
        #         # with out:

        #         if not os.path.exists(os.path.join(os.getcwd(),'figures')):
        #             os.makedirs(os.path.join(os.getcwd(),'figures'))

        #         for figure in save_figs_chkbxs.keys():
        #             if save_figs_chkbxs[figure].value:

        #                 save_location = os.path.join( os.getcwd(),'figures',saved_root_name.value  + '_' + str(figure) )     
        #                 # print(save_location)     
        #                 fig_dict[figure].savefig(save_location, bbox_inches='tight')



    #### Analysis Functions

    
    def subtr_region(self,energy,intensity,crop_details,UT2_params = None):

        if type(crop_details) == tuple:
            croplims = dc(crop_details)

        if type(crop_details) == list:
            
            croplims = dc(crop_details[0])
            subtype = dc(crop_details[1])
        


        if subtype == 'shirley':
            Ei = [index_of(energy,croplims[0]), index_of(energy,croplims[1])]
            energy_crop = energy[min(Ei):max(Ei)]
            intensity_crop = intensity[min(Ei):max(Ei)]
            srl_bkgrd = backsub.shirley(energy_crop, intensity_crop)
            subtracted = intensity_crop - srl_bkgrd  
            
        elif subtype =='linear':
            Ei = [index_of(energy,croplims[0]), index_of(energy,croplims[1])]
            energy_crop = energy[min(Ei):max(Ei)]
            intensity_crop = intensity[min(Ei):max(Ei)]
            srl_bkgrd = backsub.linear(energy_crop, intensity_crop)
            subtracted = intensity_crop - srl_bkgrd  
            
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
                
                srl_bkgrd,subtr = backsub.Tougaard(result_tou.params, intensity,energy)
            
            elif UT2_params != None:
                
                srl_bkgrd,subtr = backsub.Tougaard(UT2_params, intensity,energy)
                
                
            subtracted = dc(subtr) 
            intensity_crop = dc(intensity - intensity[-1])
            energy_crop = dc(energy)


        if (UT2_params is None) & (subtype=='UT2'):
            return energy_crop, subtracted, srl_bkgrd, result_tou.params
        return energy_crop, subtracted, srl_bkgrd



    def area(self,spec, xen):
        return np.trapz(spec,xen)



    def bksub_all(self,cropdic = {}):
        if not bool(cropdic):
            print('No background subtraction dictionary defined')
            return
        
        for spectra in self.element_scans:
            # print(spectra)
            self.data[spectra]['isub'] = dc([[] for k in range(len(self.data[spectra]['intensity']))])
            self.data[spectra]['bkgd'] = dc([[] for k in range(len(self.data[spectra]['intensity']))])
            self.data[spectra]['area'] = dc([[] for k in range(len(self.data[spectra]['intensity']))])  
            if cropdic[spectra][1] =='UT2':
                self.data[spectra]['params'] = dc([[] for k in range(len(self.data[spectra]['intensity']))])  
        
            for i in range(len(self.data[spectra]['intensity'])):

                if cropdic[spectra][1] =='UT2':

                    self.data[spectra]['esub'], self.data[spectra]['isub'][i],self.data[spectra]['bkgd'][i],self.data[spectra]['params'][i] = \
                        self.subtr_region(self.data[spectra]['energy'],self.data[spectra]['intensity'][i],cropdic[spectra])
                else:
                    self.data[spectra]['esub'], self.data[spectra]['isub'][i],self.data[spectra]['bkgd'][i] = \
                        self.subtr_region(self.data[spectra]['energy'],self.data[spectra]['intensity'][i],cropdic[spectra])
                
                self.data[spectra]['area'][i] = self.area( np.flip(self.data[spectra]['isub'][i]) , np.flip(self.data[spectra]['esub']) )
                
                if self.normalize_subtraction == True:

                    if self.data[spectra]['area'][i] > 1000:
                        self.data[spectra]['isub'][i] = self.data[spectra]['isub'][i]/self.data[spectra]['area'][i]
                        self.data[spectra]['bkgd'][i] = self.data[spectra]['bkgd'][i]/self.data[spectra]['area'][i]
                    else:
                        self.data[spectra]['isub'][i] = self.data[spectra]['isub'][i]/1e6
                        self.data[spectra]['bkgd'][i] = self.data[spectra]['bkgd'][i]/1e6
                        
    def calc_total_area(self):
        
        cycles = len(self.data[list(self.data.keys())[0]]['intensity'])

        self.data['total area'] = [[] for k in range(cycles)]

        for i in range(cycles):
            tota = 0

            for spectra in self.element_scans:
                    
                tota += np.abs(self.data[spectra]['area'][i])/self.RSF[spectra]

            self.data['total area'][i] = dc(tota)
            


        for spectra in self.element_scans:

            self.data[spectra]['atperc'] = np.empty(cycles)
            
            for i in range(cycles):  
                                    
                self.data[spectra]['atperc'][i] = (np.abs(self.data[spectra]['area'][i])/self.RSF[spectra])/self.data['total area'][i] 
                    










    ### Plotting functions
    def plot_all_spectra(self, cropdic,offval=0, plotspan=False, saveflag=0,filepath = '',figdim = (15,40)):

        fig,ax = plt.subplots(int(np.ceil((len(self.element_scans)+2)/3)) ,3, figsize = figdim)
        ax = ax.ravel()
        # print(len(ax))
        iter = 0
        for spectra in self.data.keys():

            if spectra not in ('total area'):

                for i in range(len(self.data[spectra]['intensity'])):
                    ax[iter].plot(self.data[spectra]['energy'],self.data[spectra]['intensity'][i]+i*offval,label = spectra)

                ax[iter].set_title(spectra,fontsize=24)
                ax[iter].set_xlim(max(self.data[spectra]['energy']),min(self.data[spectra]['energy']))
                ax[iter].set_xlabel('Binding Energy (eV)',fontsize = 20)
                ax[iter].set_ylabel('Counts/s',fontsize = 20)

                ax[iter].tick_params(labelsize=16)
                ax[iter].tick_params(labelsize=16)

                if plotspan==True:
                    if cropdic[spectra][1] == 'shirley':
                        ax[iter].axvspan( np.min(cropdic[spectra][0]), np.max(cropdic[spectra][0]) , alpha=0.1, color='orange')
                    elif cropdic[spectra][1] == 'linear':
                        ax[iter].axvspan( np.min(cropdic[spectra][0]), np.max(cropdic[spectra][0]) , alpha=0.1, color='green')
                    elif cropdic[spectra][1] == 'UT2':
                        ax[iter].axvspan( np.min(cropdic[spectra][0]), np.max(cropdic[spectra][0]) , alpha=0.1, color='blue')
                iter+=1


        fig.tight_layout(pad=2)


        if saveflag ==True:
            plt.savefig(filepath,bbox_inches = "tight")
        
        return fig, ax
            
            
            
    def plot_all_sub(self,cropdic = {}, offval=0):

        if not bool(cropdic):
            print('No background subtraction dictionary defined')
            return


        fig,ax = plt.subplots(int(np.ceil(len(self.element_scans)/2)) ,2, figsize = (15,15))
        ax = ax.ravel()


        fit_legend = dc(self.data['C1s']['pos names'])

        iter = 0
        for spectra in self.element_scans:

            en = self.data[spectra]['esub']

            for i in range(len(self.data[spectra]['intensity'])):
                
                ax[iter].plot(self.data[spectra]['esub'],self.data[spectra]['isub'][i] + offval*i,label = spectra)


            ax[iter].set_title(spectra,fontsize=24)
            ax[iter].set_xlim(max(self.data[spectra]['esub']),min(self.data[spectra]['esub']))
            if self.normalize_subtraction ==True:
                ax[iter].set_ylim(-0.05,(np.ceil(np.max([np.max(self.data[spectra]['isub'][i]) for i in range(len(self.data[spectra]['isub']))\
                               if np.max(self.data[spectra]['isub'][i]) <1])*10))/10)

            ax[iter].set_xlabel('Binding Energy (eV)',fontsize = 20)
            ax[iter].set_ylabel('Counts/s',fontsize = 20)

            ax[iter].tick_params(labelsize=16)
            ax[iter].tick_params(labelsize=16)

            if cropdic[spectra][1] == 'shirley':
                ax[iter].axvspan( np.min(cropdic[spectra][0]), np.max(cropdic[spectra][0]) , alpha=0.1, color='orange')
            elif cropdic[spectra][1] == 'linear':
                ax[iter].axvspan( np.min(cropdic[spectra][0]), np.max(cropdic[spectra][0]) , alpha=0.1, color='green')
            elif cropdic[spectra][1] == 'UT2':
                ax[iter].axvspan( np.min(cropdic[spectra][0]), np.max(cropdic[spectra][0]) , alpha=0.1, color='blue')

            iter+=1

        fig.legend(fit_legend,loc='center left', bbox_to_anchor=(1.0, 0.5),fontsize=20)

        fig.tight_layout()
        return fig, ax



    def plot_atomic_percent(self):
        
        leglist = []
        fig, ax = plt.subplots(figsize = (12,8))

        x = np.arange(len(self.data['C1s']['atperc']))

        for spectra in self.element_scans:
            ax.plot(x,self.data[spectra]['atperc']*100)
            leglist.append(spectra)


        # ax.title(sample,fontsize = 24)
        ax.set_xlabel('Position',fontsize = 30)
        ax.set_ylabel('Atomic Percent',fontsize = 30)

        ax.tick_params(labelsize=30)
        ax.tick_params(labelsize=30)

        ax.set_xticks(x)
        ax.set_ylim(ymin = 0)
        if 'pos names' in self.data['C1s']:
            ax.set_xticklabels(self.data['C1s']['pos names'],rotation = 80);
        ax.legend(leglist,bbox_to_anchor=(0.85, 0.4, 0.5, 0.5), loc='lower center',fontsize = 20)
        
        return fig, ax