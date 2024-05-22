# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 14:16:23 2023
@author: Diallo
"""
#-------------------------------------------------------------------------------------------------------------------------------------------------------
import os
import pandas as pd
import pydicom as dcm
import time
#-------------------------------------------------------------------------------------------------------------------------------------------------------
start_time = time.time()
#-------------------------------------------------------------------------------------------------------------------------------------------------------
def is_dicom(file_path):
    try:
        dcm.dcmread(file_path)
        return True
    except dcm.errors.InvalidDicomError:
        return False
#-------------------------------------------------------------------------------------------------------------------------------------------------------
patient_path = os.path.dirname(os.environ.get("PATIENT_PATH"))
print("-------------gtgt",patient_path)
Projet = os.path.normpath(patient_path)
FoldersCT = [x[0] for x in os.walk(Projet) if os.path.basename(x[0])=='CT_TO_TOTALSEGMENTATOR'] 
FoldersPetCT = [x[0] for x in os.walk(Projet) if os.path.basename(x[0])=='PET_TO_TOTALSEGMENTATOR']
Folders_CT_PETCT = FoldersCT + FoldersPetCT
PatientsCharacteristicsDf = pd.DataFrame()
for folder in Folders_CT_PETCT:
    print(folder)
    files_in_folder = os.listdir(folder)
    First_dcm_file = os.path.join(folder, files_in_folder[0])
    if (is_dicom(First_dcm_file)) and dcm.dcmread(First_dcm_file).Modality == 'CT':
        dcm_= dcm.dcmread(First_dcm_file)
        CodeMeaning = 'nan'        
        if 'ProcedureCodeSequence' in dcm_:
            CodeMeaning = dcm_.ProcedureCodeSequence[0].CodeMeaning
        PatientSize = 'nan'
        if 'PatientSize' in dcm_:
            PatientSize = dcm_.PatientSize
        PatientWeight = 'nan'
        if 'PatientWeight' in dcm_:
            PatientWeight = dcm_.PatientWeight
        AcquisitionDate = 'nan'
        if 'AcquisitionDate' in dcm_:
            AcquisitionDate = dcm_.AcquisitionDate
        DataCollectionDiameter = 'nan'
        if 'DataCollectionDiameter' in dcm_:
            DataCollectionDiameter = dcm_.DataCollectionDiameter
        ReconstructionDiameter = 'nan'
        if 'ReconstructionDiameter' in dcm_:
            ReconstructionDiameter = dcm_.ReconstructionDiameter
        PatientPosition = 'nan'
        if 'PatientPosition' in dcm_:
            PatientPosition = dcm_.PatientPosition
        data = {'Folder': [folder],
                'Type' : os.path.basename(folder),
                'PatientID': [dcm_.PatientID],
                'CodeMeaning': [CodeMeaning],
                'AcquisitionDate': [AcquisitionDate],
                'DataCollectionDiameter': [DataCollectionDiameter],
                'ReconstructionDiameter': [ReconstructionDiameter],
                'PatientPosition': [PatientPosition],
                'PatientBirthDate': [dcm_.PatientBirthDate],
                'PatientSex': [dcm_.PatientSex],
                'PatientSize': [PatientSize],
                'PatientWeight': [PatientWeight]}
        df0 = pd.DataFrame (data, columns = ['Folder',
                                             'Type',
                                             'PatientID',
                                             'CodeMeaning',
                                             'AcquisitionDate',
                                             'DataCollectionDiameter',
                                             'ReconstructionDiameter',
                                             'PatientPosition',
                                             'PatientBirthDate',
                                             'PatientSex',
                                             'PatientSize',
                                             'PatientWeight'])
        PatientsCharacteristicsDf = pd.concat([PatientsCharacteristicsDf,df0], ignore_index=True)
            
PatientsCharacteristicsDf.to_pickle(os.path.join(f"{patient_path}\_DFS_\PatientsCharacteristicsDf.pkl"))  

#-------------------------------------------------------------------------------------------------------------------------------------------------------
print("--- %s seconds ---" % (time.time() - start_time))
#-------------------------------------------------------------------------------------------------------------------------------------------------------
