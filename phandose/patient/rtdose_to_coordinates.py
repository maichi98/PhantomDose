# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 19:25:15 2024
@author: Diallo
"""
#-----------------------------------------------------------------------------------------------------------------------------------------------------
import os
import pickle
import numpy as np
import pandas as pd
import copy
from shapely import geometry
from datetime import datetime
from statistics import mode
import warnings
warnings.filterwarnings("ignore")
#-----------------------------------------------------------------------------------------------------------------------------------------------------
PatLib = os.path.normpath("C:\PredictiveExtension\AGORL\AGORL_P33\PresentationCharlotte")#"A:/CANTO-RT/canto-01/01-00324-M-J/RightBreastRadiotherapyData_part/Extraction")
#--------------------------------#--------------------------------------------------------------------------------------------------------------------
start_time = datetime.now()
for root, dirs, files in os.walk(PatLib):
    if len(dirs) == 0:
        print('---------------------------------------------------------------------------------------------------------------------------------------')
        print('Patient : ', os.path.basename(os.path.normpath(root)))
        ListRD = [f for f in files if (f.endswith('.txt') & f.startswith('RD'))]
        ListRS = [f for f in files if (f.endswith('.txt') & f.startswith('PP_'))]
        for rd in ListRD:
            print(rd)
            RTDose = pd.read_csv(os.path.join(root, rd), encoding = "ISO-8859-1", sep='\t',header=0)
            Vars = RTDose.columns.tolist()
            ListRTDosex  = sorted(RTDose['X'].unique().tolist())
            ListXDiff =  [t - s for s, t in zip(ListRTDosex, ListRTDosex[1:])]
            ListRTDosey  = sorted(RTDose['Y'].unique().tolist())
            ListYDiff =  [t - s for s, t in zip(ListRTDosey, ListRTDosey[1:])]
            ListRTDosez  = sorted(RTDose['Z'].unique().tolist())
            ListZDiff =  [t - s for s, t in zip(ListRTDosez, ListRTDosez[1:])]
            VoxelVolume = (mode(ListXDiff)*mode(ListYDiff)*mode(ListZDiff))/1000
            for rs in ListRS:
                RTStruct = pd.read_csv(os.path.join(root, rs), encoding = "ISO-8859-1", sep='\t',header=0)
                #--------------------------------------------------------------------------------------
                RTStruct = RTStruct.rename(columns={"ROIContourNumber": "ROIContourIndex"})
                #--------------------------------------------------------------------------------------
                NewDosiName = rd[:rd.find('.txt')] + '_' + rs[:rs.find('.txt')] + '_.NewDosi'
                ListRTStructz  = sorted(RTStruct['z'].unique().tolist())
                RSslicethickness = min([t - s for s, t in zip(ListRTStructz, ListRTStructz[1:])])
                Listz = [x for x in ListRTStructz if ( (x >= min(ListRTDosez) - RSslicethickness/2) & (x <= max(ListRTDosez) + RSslicethickness/2))]
                Contours = RTStruct[RTStruct['z'].isin(Listz)]
                ListROIs = sorted(Contours['ROIName'].unique().tolist())
                ListROIs =['external']
                print(ListROIs)
                Dict_of_df = {}
                for roiname in ListROIs:
                    key_name = str(roiname)
                    columnsNames= Vars + [roiname]
                    Dict_of_df[key_name] = copy.deepcopy(pd.DataFrame(columns = columnsNames))
                for r in ListROIs:
                    roi = Contours[Contours['ROIName'] == r]
                    RoiVolume = 0
                    OrganVolumeInDoseMatrix = 0
                    ListZroi = sorted(roi['z'].unique().tolist())
                    #Espacement entre coupes consécutives
                    ListZDiff =  [t - s for s, t in zip(ListZroi, ListZroi[1:])]
                    ListZDiffUnique = list(set(ListZDiff))
                    RTStruct.columns
                    for zr in ListZroi:
                        roi_at_z = roi[roi['z'] == zr]
                        ListROIContourIndex = sorted(roi_at_z['ROIContourIndex'].unique().tolist())
                        for c in ListROIContourIndex:
                            Contour = roi_at_z[roi_at_z['ROIContourIndex'] == c]
                            Contour['Polygone'] = Contour[['x','y']].apply(tuple, axis=1)
                            Polygone = geometry.Polygon(Contour['Polygone'].unique().tolist())
                            # VOLUMES -----------------------------------------------------------------------------------------
                            if len(ListZDiffUnique) == 1:
                                RoiVolume = RoiVolume + (Polygone.area * mode(ListZDiff))/1000
                            # DOSES -----------------------------------------------------------------------------------------
                            ListRDdz = [abs(x-zr) for x in ListRTDosez]
                            dzmin = min(ListRDdz)
                            z0 = ListRTDosez[ListRDdz.index(dzmin)]
                            df0 = RTDose[RTDose['Z']==z0]
                            df0['Z'] = zr
                            df0['point'] = df0[['X','Y']].apply(tuple, axis=1)
                            contains = np.vectorize(lambda p: int(Polygone.contains(geometry.Point(p))), signature='(n)->()')
                            ListPoints = df0['point'].tolist()
                            Contient = contains(np.array(ListPoints))
                            df0[r] = Contient
                            # --------------------------------------------------------------------------------------------------------
                            df0 = df0[['X', 'Y', 'Z', 'DoseGy', r]]
                            df0 = df0[df0[r] == 1]
                            OrganVolumeInDoseMatrix = OrganVolumeInDoseMatrix + VoxelVolume * len(df0)
                            Dict_of_df[r] = pd.concat([Dict_of_df[r], df0], ignore_index=True)
                    print(r, ' RoiVolume: ', round(RoiVolume,1), ' OrganVolumeInDoseMatrix: ', round(OrganVolumeInDoseMatrix, 1))
                pickle.dump(Dict_of_df, open(os.path.join(root, NewDosiName), "wb"))  # save it into a file named save.p
end_time = datetime.now()
print('---------------------------------------------------------------------------------------------------------------------------------------')
print('Duration: {}'.format(end_time - start_time))
print('---------------------------------------------------------------------------------------------------------------------------------------')
