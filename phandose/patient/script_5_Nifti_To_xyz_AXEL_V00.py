# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 21:57:04 2023
@author: Diallo
"""
import os
import numpy as np
import pandas as pd
import nibabel as nib
from skimage import measure
import time
#---------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------------
phantom_path = os.environ.get("PHANTOMLIB_PATH")
PhantomLib = os.path.normpath(os.path.join(phantom_path))

patient_path = os.environ.get("PATIENT_PATH")
Projet = os.path.normpath(os.path.join(patient_path))

_DFS_ = os.path.join(os.path.dirname(Projet),'_DFS_')
PatientsCharacteristicsDf = pd.read_pickle(os.path.join(_DFS_,'PatientsCharacteristicsDf.pkl'))
PatientList = pd.unique(PatientsCharacteristicsDf['PatientID']).tolist()
#-------------------------------------------------------------------------------------------------------------------------------------------------------
for Pat in PatientList:
    start_time = time.time()
    print("------------ c'est ok",Pat)
    Projet = os.path.dirname(os.path.join(patient_path))
    NIFTI_FOLDERS = [x[0] for x in os.walk(os.path.join(Projet,Pat)) if os.path.basename(x[0]) in ['NIFTI_FROM_CT', 'NIFTI_FROM_PET']]
    XYZ_FOLDER = os.path.join(Projet, Pat, 'XYZ')
    if not os.path.exists(XYZ_FOLDER):
        os.makedirs(XYZ_FOLDER)
    for folder in NIFTI_FOLDERS:
        if os.path.basename(folder) == 'NIFTI_FROM_CT':
            PatientCharacteristics = PatientsCharacteristicsDf[(PatientsCharacteristicsDf['PatientID'] == Pat) & \
                                                               (PatientsCharacteristicsDf['Type'] == 'CT_TO_TOTALSEGMENTATOR')].reset_index(drop=True)
            XYZ_Out = os.path.join(XYZ_FOLDER,'Patient.txt')
            if os.path.exists(XYZ_Out):
                os.remove(XYZ_Out)
        if os.path.basename(folder) == 'NIFTI_FROM_PET':
            PatientCharacteristics = PatientsCharacteristicsDf[(PatientsCharacteristicsDf['PatientID'] == Pat) & \
                                                               (PatientsCharacteristicsDf['Type'] == 'PET_TO_TOTALSEGMENTATOR')].reset_index(drop=True)
            XYZ_Out = os.path.join(XYZ_FOLDER,'Phantom.txt')
            if os.path.exists(XYZ_Out):
                os.remove(XYZ_Out)
        print('XYZ_Out :', XYZ_Out )
        Nifti_Files = [name for name in os.listdir(folder) if ((name.endswith('.gz')) and (name not in ['body.nii.gz', 'skin.nii.gz']))]
        if len(Nifti_Files) > 0:
            print(Pat)
            print(folder)
            print('Number of nifti files :', len(Nifti_Files))
            df_CTSet = pd.DataFrame()
            for Nifti_file in Nifti_Files:
                df_Roi = pd.DataFrame()
                ni_obj = nib.load(os.path.join(folder, Nifti_file))
                ni_header = ni_obj.header
                ni_data = ni_obj.get_fdata()
                print(Nifti_file)
                print('Number of slices: ', ni_data.shape[2])
                ContourNumber = 0
                for slice in range(ni_data.shape[2]):
                    df_Coupe = pd.DataFrame()
                    Coupe = ni_data[:,:,slice]
                    contours = measure.find_contours(Coupe, 0.5)
                    if len(contours) > 0:
                        print('Number of contours: ', len(contours))
                        for c in range(len(contours)):
                            ContourNumber = ContourNumber + 1
                            print('c = ', c, ' ContourNumber :',  ContourNumber)
                            df_Contour = pd.DataFrame(data=contours[c], columns=['x','y'])
                            df_Contour['x'] =   df_Contour['x'] - ni_header['qoffset_x'] 
                            df_Contour['y'] = -(df_Contour['y'] + ni_header['qoffset_y'])
                            df_Contour['z'] = slice*ni_header['pixdim'][3] + ni_header['qoffset_z']
                            df_Contour['ROIContourPointNumber'] = 1 + np.arange(len(df_Contour))
                            df_Contour['ROIContourNumber'] = ContourNumber
                            df_Coupe = pd.concat([df_Coupe, df_Contour], ignore_index=True)            
                        df_Roi = pd.concat([df_Roi, df_Coupe], ignore_index=True)            
                df_Roi['ROINumber'] = 1 + Nifti_Files.index(Nifti_file)
                df_Roi['ROIName'] = Nifti_file.split('.')[0].replace('_', ' ')
                df_CTSet = pd.concat([df_CTSet, df_Roi], ignore_index=True)
            df_CTSet = df_CTSet[['ROIName', 'ROINumber', 'ROIContourNumber', 'ROIContourPointNumber', 'x', 'y', 'z']]
            df_CTSet.to_csv(XYZ_Out, sep='\t', encoding='utf-8', index=False)
            #-----------------------------------------------------------------------------------------------------------------------------------------------------
            #Save to PhantomLib
            if set(['brain', 'femur left', 'femur right']).issubset(pd.unique(df_CTSet['ROIName']).tolist()):
                Topz = df_CTSet['z'].max()
                Brain_Topz = df_CTSet[df_CTSet['ROIName']=='brain']['z'].max()
                if Topz > Brain_Topz:
                    PatientPosition = PatientCharacteristics.iloc[0]['PatientPosition']
                    PatientSex = PatientCharacteristics.iloc[0]['PatientSex']
                    Phantom_Name = '_' + PatientPosition + '_' + PatientSex +  '_ ' + Pat.replace(" ", "") + '_.txt'
                    df_CTSet.to_csv(os.path.join(PhantomLib, Phantom_Name), sep='\t', encoding='utf-8', index=False)
    #---------------------------------------------------------------------------------------------------------------------------------
    print(Pat, "--- %s seconds ---" % (time.time() - start_time))
    #---------------------------------------------------------------------------------------------------------------------------------
