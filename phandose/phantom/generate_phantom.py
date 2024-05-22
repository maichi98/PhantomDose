#=====================================================================================================================================================
#-----------------------------------------------------------------------------------------------------------------------------------------------------
import os
import numpy as np
from scipy.interpolate import interp1d
import pandas as pd
import cv2
from TreePh import TreePh
#-----------------------------------------------------------------------------------------------------------------------------------------------------



final_path_file = []

def round_nearest(x, a):
    return round(round(x / a) * a, 2)
#--------------------------------#--------------------------------------------------------------------------------
#Cartesian to polar coordinates
def cart_to_pol(x, y, x_c, y_c, deg = True):
    complex_format = x - x_c + 1j * (y - y_c)
    return np.abs(complex_format), np.angle(complex_format, deg = False)
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#Contour Area
def Get_Area(SelectedContours):
    ZList = sorted(SelectedContours.z.unique().tolist())
    AreaDf = pd.DataFrame()
    for z in ZList:
        Coupe = SelectedContours[SelectedContours['z'] == z]
        ROINumberList = sorted(Coupe.ROINumber.unique().tolist())
        for r in ROINumberList:
            ROI = Coupe[Coupe['ROINumber'] == r]
            ROIContourIndexList = sorted(ROI.ROIContourIndex.unique().tolist())
            for c in ROIContourIndexList:
                Contour = ROI[ROI['ROIContourIndex'] == c]
                Contour = Contour.round({'x': 0, 'y': 0})
                Contour = Contour.drop_duplicates(subset=['x', 'y'], keep='last')
                ctr = Contour[['x','y']].to_numpy()
                ctrint = np.array([ctr]).astype(np.int32)
                XUL, YUL, WR, HR = cv2.boundingRect(ctrint)
                Centrex = XUL + WR/2
                Centrey = YUL + HR/2
                area = cv2.contourArea(ctrint)
                data = {'Centrex': [Centrex], 'Centrey': [Centrey], 'z': [z] ,
                        'RTROIInterpretedType': [Contour.iloc[0]['RTROIInterpretedType']],
                        'ROIName': [Contour.iloc[0]['ROIName']], 'ROINumber': [r], 'ROIContourIndex': [c], 'Area': [area]}
                df0 = pd.DataFrame (data, columns = ['Centrex', 'Centrey', 'z', 'RTROIInterpretedType', 'ROIName', 'ROINumber', 'ROIContourIndex', 'Area'])
                AreaDf = pd.concat([AreaDf,df0], ignore_index=True)            
    return AreaDf
#-----------------------------------------------------------------------------------------------------------------------------------------------------
# PATIENT --------------------------------------------------------------------------------------------------------------------------------------------
#Specify root to Current Project
def run_pre_traitement(self):
    
    PantomLibrary = str(self.tree_view.get_phantom_clicked()) #------> PATIENT PATH
    path = str(self.tree_view.get_patient_clicked()) #------> PHANTOM PATH
    print(self.tree_view.get_phantom_clicked())
    print(self.tree_view.get_patient_clicked())
    for repert_actu, sous_repert, fichiers in os.walk(path):
        for fichier in fichiers:
            if (fichier.endswith('.txt') & fichier.startswith('RS')):
                print('Patient :', os.path.join(repert_actu, fichier))
                Patient_Contours=pd.read_csv(os.path.join(repert_actu, fichier), encoding = "ISO-8859-1", sep='\t',header=0)
                # PHANTOM --------------------------------------------------------------------------------------------------------------------------------------------
                for rep, sous_rep, phants in os.walk(PantomLibrary):
                    for phant in phants:
                        if (phant.endswith('.txt') & phant.startswith('RS')):
                            print('Phantom :', os.path.join(rep, phant))
                            Phantom_Contours=pd.read_csv(os.path.join(rep, phant), encoding = "ISO-8859-1", sep='\t',header=0)
                            Phantom_Contours.loc[Phantom_Contours['ROIName'] == '0301_spinal-cord', 'ROIName'] = 'Moelle' 
                            Phantom_Contours.loc[Phantom_Contours['ROIName'] == '0309_lung_R', 'ROIName'] = 'Poumon D' 
                            Phantom_Contours.loc[Phantom_Contours['ROIName'] == '0310_lung_L', 'ROIName'] = 'Poumon G' 
                            ExternalList = ['0500_external-contours_M',
                                            '0500_external-contours-head',
                                            '0500_external-contours-trunk',
                                            '0500_external-contours-leg_R',
                                            '0500_external-contours-leg_L',
                                            '0500_external-contours-arm_L',
                                            '0500_external-contours-arm_R',
                                            '0500_external-contours_1',
                                            '0500_external-contours_2']
                            Phantom_Contours.loc[Phantom_Contours['ROIName'].isin(ExternalList), 'ROIName'] = 'Contour_Externe'
                            Phantom_Contours.loc[Phantom_Contours['ROIName'] == 'Contour_Externe', 'RTROIInterpretedType'] = 'EXTERNAL'
                            #-----------------------------------------------------------------------------------------------------------------------------------------------------
                            # Set Axial Position
                            #-----------------------------------------------------------------------------------------------------------------------------------------------------
                            RTSLIST = [Patient_Contours,    Phantom_Contours]
                            RTSNAME = ['Patient_Contours', 'Phantom_Contours']
                            Barydf = pd.DataFrame()
                            for org in ['Moelle', 'Poumon G', 'Poumon D']:
                                for idx, df in enumerate(RTSLIST):
                                    Topz = df[df['ROIName'] == org]['z'].max()
                                    Barx = df[(df['ROIName'] == org) & (df['z'] >= (Topz - 10))]['x'].mean()
                                    Bary = df[(df['ROIName'] == org) & (df['z'] >= (Topz - 10))]['y'].mean()
                                    Barz = df[(df['ROIName'] == org) & (df['z'] >= (Topz - 10))]['z'].mean()
                                    df0 = pd.DataFrame(data={'Organ': [org], 'Rts': [RTSNAME[idx]],'Barx': [Barx], 'Bary': [Bary],'Barz': [Barz]})
                                    Barydf = pd.concat([Barydf, df0], ignore_index=True)
                            Barydf = Barydf.dropna()
                            Both = Barydf.groupby('Organ', as_index = False).agg(Both=('Organ','count'))
                            Barydf = pd.merge(Barydf, Both, on='Organ', how ='left')
                            print('len Both', len(Barydf[Barydf['Both'] == 2]))
                            Barycentre = Barydf[Barydf['Both'] == 2].groupby('Rts', as_index = False).agg(xb=('Barx','mean'), yb=('Bary','mean'), zb=('Barz','mean'))
                            xbpat = Barycentre.loc[Barycentre['Rts'] == 'Patient_Contours', 'xb'].values[0]
                            xbfan = Barycentre.loc[Barycentre['Rts'] == 'Phantom_Contours', 'xb'].values[0]
                            ybpat = Barycentre.loc[Barycentre['Rts'] == 'Patient_Contours', 'yb'].values[0]
                            ybfan = Barycentre.loc[Barycentre['Rts'] == 'Phantom_Contours', 'yb'].values[0]
                            zbpat = Barycentre.loc[Barycentre['Rts'] == 'Patient_Contours', 'zb'].values[0]
                            zbfan = Barycentre.loc[Barycentre['Rts'] == 'Phantom_Contours', 'zb'].values[0]
                            Phantom_Contours['x'] = Phantom_Contours['x'] + (xbpat - xbfan)
                            Phantom_Contours['y'] = Phantom_Contours['y'] + (ybpat - ybfan)
                            Phantom_Contours['z'] = Phantom_Contours['z'] + (zbpat - zbfan)
                            #-----------------------------------------------------------------------------------------------------------------------------------------------------
                            #Jonction Patient
                            XMoelleMean = Patient_Contours[Patient_Contours['ROIName'] == 'Moelle']['x'].mean()
                            ZMoelleList = sorted(Patient_Contours[Patient_Contours['ROIName'] == 'Moelle'].z.unique().tolist())
                            JunctionPatient = Patient_Contours[(Patient_Contours['RTROIInterpretedType'] == 'EXTERNAL') &
                                                            (Patient_Contours['z'] <= ZMoelleList[-1])]
                            AreaJunctionPatient = Get_Area(JunctionPatient)
                            AreaJunctionPatient['arearank'] = AreaJunctionPatient.groupby(['z', 'ROIName'])['Area'].rank(method='first', ascending=False)
                            AreaJunctionPatient = AreaJunctionPatient[AreaJunctionPatient['arearank'] == 1]
                            AreaJunctionPatient['dx'] = abs(AreaJunctionPatient['Centrex'] - XMoelleMean)
                            P75dx = np.percentile(AreaJunctionPatient['dx'].to_numpy(), 75)
                            AreaJunctionPatient = AreaJunctionPatient[AreaJunctionPatient['dx'] <= P75dx]
                            Areamin = AreaJunctionPatient['Area'].min()
                            Junctionz = AreaJunctionPatient.loc[AreaJunctionPatient['Area'] == Areamin, 'z'].values[0]
                            JunctionROINumber = AreaJunctionPatient.loc[AreaJunctionPatient['Area'] == Areamin, 'ROINumber'].values[0]
                            JunctionROIContourIndex = AreaJunctionPatient.loc[AreaJunctionPatient['Area'] == Areamin, 'ROIContourIndex'].values[0]
                            JunctionPat = Patient_Contours[(Patient_Contours['ROINumber'] == JunctionROINumber) & 
                                                        (Patient_Contours['ROIContourIndex'] == JunctionROIContourIndex) &
                                                        (Patient_Contours['z'] == Junctionz)]
                            CentreJonctionPatient_x = AreaJunctionPatient.loc[(AreaJunctionPatient['z'] == Junctionz) &
                                                                            (AreaJunctionPatient['ROINumber'] == JunctionROINumber) &
                                                                            (AreaJunctionPatient['ROIContourIndex'] == JunctionROIContourIndex)
                                                                            , 'Centrex'].values[0]
                            CentreJonctionPatient_y = AreaJunctionPatient.loc[(AreaJunctionPatient['z'] == Junctionz) &
                                                                            (AreaJunctionPatient['ROINumber'] == JunctionROINumber) &
                                                                            (AreaJunctionPatient['ROIContourIndex'] == JunctionROIContourIndex)
                                                                            , 'Centrey'].values[0]
                            #-----------------------------------------------------------------------------------------------------------------------------------------------------
                            #Jonction Phantom
                            Fantomez = sorted(Phantom_Contours[(Phantom_Contours['RTROIInterpretedType'] == 'EXTERNAL') & (Phantom_Contours['z'] <= Junctionz)].z.unique().tolist())
                            Fantomedz = [abs(x-Junctionz) for x in Fantomez]
                            DistanceMin = min(Fantomedz)
                            Matchz = Fantomez[Fantomedz.index(DistanceMin)]
                            JunctionPhantom = Phantom_Contours[(Phantom_Contours['RTROIInterpretedType'] == 'EXTERNAL') & (Phantom_Contours['z'] == Matchz)]
                            AreaJunctionPhantom = Get_Area(JunctionPhantom)
                            AreaJunctionPhantom['arearank'] = AreaJunctionPhantom.groupby(['z', 'ROIName'])['Area'].rank(method='first', ascending=False)
                            AreaJunctionPhantom = AreaJunctionPhantom[AreaJunctionPhantom['arearank'] == 1]
                            JunctionROINumber = AreaJunctionPhantom.loc[AreaJunctionPhantom['arearank'] == 1, 'ROINumber'].values[0]
                            JunctionROIContourIndex = AreaJunctionPhantom.loc[AreaJunctionPhantom['arearank'] == 1, 'ROIContourIndex'].values[0]
                            JunctionPhan = Phantom_Contours[(Phantom_Contours['ROINumber'] == JunctionROINumber) & 
                                                            (Phantom_Contours['ROIContourIndex'] == JunctionROIContourIndex) &
                                                            (Phantom_Contours['z'] == Matchz)]
                            #-----------------------------------------------------------------------------------------------------------------------------------------------------
                            #Remove the phantom organs fully includen in the patient imaging
                            PhantomOrganZRange = Phantom_Contours[Phantom_Contours['RTROIInterpretedType'] == 'ORGAN'].groupby('ROIName', as_index = False).agg(zmin=('z','min'), zmax=('z','max'))
                            PhantomOrganExclude = PhantomOrganZRange[PhantomOrganZRange['zmin'] >= Matchz]
                            PhantomOrganExcludeList = PhantomOrganExclude.ROIName.unique().tolist()
                            Phantom_Organs  = Phantom_Contours[((Phantom_Contours['RTROIInterpretedType'] == 'ORGAN') & (~Phantom_Contours['ROIName'].isin(PhantomOrganExcludeList)))]
                            Pantom_External = Phantom_Contours[((Phantom_Contours['RTROIInterpretedType'] == 'EXTERNAL') & (Phantom_Contours['z'] <= Matchz))]
                            Phantom_Contours = pd.concat([Pantom_External,Phantom_Organs], ignore_index=True)            
                            #-----------------------------------------------------------------------------------------------------------------------------------------------------
                            # Set transversal Position #Get homography matrix
                            #-----------------------------------------------------------------------------------------------------------------------------------------------------
                            CtrPatient = JunctionPat[['x','y']].to_numpy()
                            CtrintPatient = np.array([CtrPatient]).astype(np.int32)
                            XULPatient, YULPatient, WRPatient, HRPatient = cv2.boundingRect(CtrintPatient)
                            RectanglePatient = np.array([[XULPatient, YULPatient] ,[XULPatient, YULPatient + HRPatient], [XULPatient + WRPatient,YULPatient + HRPatient] , [XULPatient + WRPatient,YULPatient]])
                            CtrPhantom = JunctionPhan[['x','y']].to_numpy()
                            CtrintPhantom = np.array([CtrPhantom]).astype(np.int32)
                            XULPhantom, YULPhantom, WRPhantom, HRPhantom = cv2.boundingRect(CtrintPhantom)
                            RectanglePhantom = np.array([[XULPhantom, YULPhantom] ,[XULPhantom, YULPhantom + HRPhantom], [XULPhantom + WRPhantom,YULPhantom + HRPhantom] , [XULPhantom + WRPhantom,YULPhantom]])
                            h, status = cv2.findHomography(RectanglePhantom, RectanglePatient)
                            #=====================================================================================================================================================
                            #Apply Homograpy to phantom contours
                            # Uniquement si cela le fait grossir
                            #-----------------------------------------------------------------------------------------------------------------------------------------------------
                            if WRPatient > WRPhantom and HRPatient > HRPhantom :
                                Phantom_Contours['xh'] = Phantom_Contours.apply(lambda row: (h[0,0]*row['x'] + h[0,1]*row['y'] + h[0,2])/(h[2,0]*row['x'] + h[2,1]*row['y'] + h[2,2])
                                                                                if row['RTROIInterpretedType'] == 'EXTERNAL' else row['x'], axis=1) 
                                Phantom_Contours['yh'] = Phantom_Contours.apply(lambda row: (h[1,0]*row['x'] + h[1,1]*row['y'] + h[1,2])/(h[2,0]*row['x'] + h[2,1]*row['y'] + h[2,2])
                                                                                if row['RTROIInterpretedType'] == 'EXTERNAL' else row['y'] , axis=1) 
                            else :
                                Phantom_Contours['xh'] = Phantom_Contours['x']
                                Phantom_Contours['yh'] = Phantom_Contours['y']
                            Phantom_Contours['zh'] = Phantom_Contours['z']
                            #-----------------------------------------------------------------------------------------------------------------------------------------------------
                            #Smooth Junction
                            #-----------------------------------------------------------------------------------------------------------------------------------------------------
                            #Jonction sup
                            JunctionPat['Polar']  = JunctionPat.apply(lambda row: cart_to_pol(row['x'], row['y'], CentreJonctionPatient_x, CentreJonctionPatient_y) , axis=1)
                            JunctionPat['rpat']  = JunctionPat.apply(lambda row: row['Polar'][0] , axis=1)
                            JunctionPat['tpat_round']  = JunctionPat.apply(lambda row: round_nearest(row['Polar'][1], 0.1) , axis=1)
                            JunctionPat_round = JunctionPat.groupby('tpat_round', as_index = False).agg(rpat_round=('rpat','mean'))
                            JunctionPat = JunctionPat.drop_duplicates(subset=['tpat_round'], keep='last')
                            JunctionPat = JunctionPat.sort_values(by='tpat_round', ascending=True)
                            X = JunctionPat_round['tpat_round'].to_numpy()
                            y = JunctionPat_round['rpat_round'].to_numpy()
                            Interpsup = interp1d(X, y, fill_value="extrapolate", kind='linear')
                            #-----------------------------------------------------------------------------------------------------------------------------------------------------
                            #Jonctinf Inf                        
                            Lsmooth = 50
                            Phantom_Contours_External = Phantom_Contours[Phantom_Contours['RTROIInterpretedType'] == 'EXTERNAL']
                            Fantomezh = sorted(Phantom_Contours_External.zh.unique().tolist())
                            Fantomedzh = [abs(x-(Junctionz-Lsmooth)) for x in Fantomezh]
                            dzhMin = min(Fantomedzh)
                            Matchzh = Fantomezh[Fantomedzh.index(dzhMin)]
                            JunctionPhantom = Phantom_Contours[(Phantom_Contours['RTROIInterpretedType'] == 'EXTERNAL') & (Phantom_Contours['zh'] == Matchzh)]
                            AreaJunctionPhantom = Get_Area(JunctionPhantom)
                            AreaJunctionPhantom['arearank'] = AreaJunctionPhantom.groupby(['z', 'ROIName'])['Area'].rank(method='first', ascending=False)
                            AreaJunctionPhantom = AreaJunctionPhantom[AreaJunctionPhantom['arearank'] == 1]
                            JunctionROINumber = AreaJunctionPhantom.loc[AreaJunctionPhantom['arearank'] == 1, 'ROINumber'].values[0]
                            JunctionROIContourIndex = AreaJunctionPhantom.loc[AreaJunctionPhantom['arearank'] == 1, 'ROIContourIndex'].values[0]
                            JunctionPhan = Phantom_Contours[(Phantom_Contours['ROINumber'] == JunctionROINumber) & 
                                                            (Phantom_Contours['ROIContourIndex'] == JunctionROIContourIndex) &
                                                            (Phantom_Contours['z'] == Matchzh)]
                            JunctionPhan['Polar']  = JunctionPhan.apply(lambda row: cart_to_pol(row['xh'], row['yh'], CentreJonctionPatient_x, CentreJonctionPatient_y) , axis=1)
                            JunctionPhan['rphan']  = JunctionPhan.apply(lambda row: row['Polar'][0] , axis=1)
                            JunctionPhan['tphan_round']  = JunctionPhan.apply(lambda row: round_nearest(row['Polar'][1], 0.1) , axis=1)
                            JunctionPhan_round = JunctionPhan.groupby('tphan_round', as_index = False).agg(rphan_round=('rphan','mean'))
                            JunctionPhan = JunctionPhan.drop_duplicates(subset=['tphan_round'], keep='last')
                            JunctionPhan = JunctionPhan.sort_values(by='tphan_round', ascending=True)
                            X = JunctionPhan_round['tphan_round'].to_numpy()
                            y = JunctionPhan_round['rphan_round'].to_numpy()
                            Interpinf = interp1d(X, y, fill_value="extrapolate", kind='linear')
                            Phantom_Contours_External['Polar'] = Phantom_Contours_External.apply(lambda row: cart_to_pol(row['xh'], row['yh'], CentreJonctionPatient_x, CentreJonctionPatient_y) , axis=1)
                            Phantom_Contours_External['rphan']   = Phantom_Contours_External.apply(lambda row: row['Polar'][0] , axis=1)
                            Phantom_Contours_External['tphan']   = Phantom_Contours_External.apply(lambda row: row['Polar'][1] , axis=1)
                            Phantom_Contours_External['rsup'] = Phantom_Contours_External.apply(lambda row: Interpsup(row['tphan']) if abs(row['zh']-Matchz)<Lsmooth else 0, axis=1)
                            Phantom_Contours_External['rinf'] = Phantom_Contours_External.apply(lambda row: Interpinf(row['tphan']) if abs(row['zh']-Matchz)<Lsmooth else 0, axis=1)
                            Phantom_Contours_External['pond'] = Phantom_Contours_External.apply(lambda row: 1-abs(row['zh']-Matchz)/Lsmooth if abs(row['zh']-Matchz)<Lsmooth else 0, axis=1)
                            Phantom_Contours_External['rcor'] = Phantom_Contours_External.apply(lambda row: row['pond']*row['rsup'] + (1-row['pond'])*row['rinf'] if abs(row['zh']-Matchz)<Lsmooth else row['rphan'], axis=1)
                            Phantom_Contours_External['xcor'] = Phantom_Contours_External.apply(lambda row: row['rcor']*np.cos(row['tphan']) + CentreJonctionPatient_x, axis=1)
                            Phantom_Contours_External['ycor'] = Phantom_Contours_External.apply(lambda row: row['rcor']*np.sin(row['tphan']) + CentreJonctionPatient_y, axis=1)
                            Phantom_Contours_External = Phantom_Contours_External[['PatientID',
                                                                                'RTROIInterpretedType',
                                                                                'ROIName',
                                                                                'ROINumber',
                                                                                'ROIContourNumber',
                                                                                'ROIContourIndex', 
                                                                                'ROIContourPointNumber',
                                                                                'xcor',
                                                                                'ycor',
                                                                                'zh']]
                            Phantom_Contours_External = Phantom_Contours_External.rename(columns={'xcor': 'x', 'ycor': 'y', 'zh': 'z'})
                            Phantom_Contours_Internal = Phantom_Contours[~(Phantom_Contours['RTROIInterpretedType'] == 'EXTERNAL')]
                            Phantom_Contours_Internal = Phantom_Contours_Internal[['PatientID',
                                                                                'RTROIInterpretedType',
                                                                                'ROIName',
                                                                                'ROINumber',
                                                                                'ROIContourNumber',
                                                                                'ROIContourIndex', 
                                                                                'ROIContourPointNumber',
                                                                                'xh',
                                                                                'yh',
                                                                                'zh']]
                            Phantom_Contours_Internal = Phantom_Contours_Internal.rename(columns={'xh': 'x', 'yh': 'y', 'zh': 'z'})
                            Phantom_Contours_Internal = Phantom_Contours_Internal[~(Phantom_Contours_Internal['ROIName'].isin(['0057_humerus_R',
                                                                                                                            '0058_humerus_L',
                                                                                                                            '0359_nipple_R',
                                                                                                                            '0360_nipple_L',
                                                                                                                            '0401_medullary-cavity-humerus_R',
                                                                                                                            '0402_medullary-cavity-humerus_L',
                                                                                                                            '0403_medullary-cavity-radius_R',
                                                                                                                            '0404_medullary-cavity-radius_L',
                                                                                                                            '0405_medullary-cavity-ulna_R',
                                                                                                                            '0406_medullary-cavity-ulna_L',
                                                                                                                            '0413_breast_lower-inner_R',
                                                                                                                            '0414_breast_lower-inner_L',
                                                                                                                            '0415_breast_lower-outer_R',
                                                                                                                            '0416_breast_lower-outer_L',
                                                                                                                            '0417_breast_upper-inner_R',
                                                                                                                            '0418_breast_upper-inner_L',
                                                                                                                            '0419_breast_upper-outer_R',
                                                                                                                            '0420_breast_upper-outer_L',
                                                                                                                            '0423_vertebral-artery-region_R',
                                                                                                                            '0424_vertebral-artery-region_L',
                                                                                                                            '0501_abdominal-regions_right-hypochondriac',
                                                                                                                            '0502_abdominal-regions_epigastric',
                                                                                                                            '0503_abdominal-regions_left-hypochondriac',
                                                                                                                            '0504_abdominal-regions_right-lumbar',
                                                                                                                            '0505_abdominal-regions_umbilical',
                                                                                                                            '0506_abdominal-regions_left-lumbar',
                                                                                                                            '0507_abdominal-regions_right-iliac',
                                                                                                                            '0508_abdominal-regions_hypogastric',
                                                                                                                            '0509_abdominal-regions_left-iliac',
                                                                                                                            '0510_connection-leg_R',
                                                                                                                            '0511_connection-leg_L',
                                                                                                                            '0513_connection-arm_L'
                                                                                                                            '0616_humeri-upper-half_activemarrow_L',
                                                                                                                            '0616_humeri-upper-half_activemarrow_R',
                                                                                                                            '0617_humeri-lower-half_activemarrow_L',
                                                                                                                            '0617_humeri-lower-half_activemarrow_R',
                                                                                                                            '0618_ulnae-and-radii_activemarrow_radius_L',
                                                                                                                            '0618_ulnae-and-radii_activemarrow_radius_R',
                                                                                                                            '0618_ulnae-and-radii_activemarrow_ulna_L',
                                                                                                                            '0618_ulnae-and-radii_activemarrow_ulna_R',
                                                                                                                            '0619_wrist-and-hand-bones_activemarrow_L',
                                                                                                                            '0619_wrist-and-hand-bones_activemarrow_R']))]
                            Patient = Patient_Contours[~((Patient_Contours['RTROIInterpretedType'] == 'EXTERNAL') & (Patient_Contours['z'] <= Junctionz))]
                            Patient = Patient[~(Patient['ROIName'].isin(['lefthumeralhead', 'righthumeralhead']))]
                            Patient['Source'] = 0
                            Phantom_Contours_External['Source'] = 1
                            Phantom_Contours_Internal['Source'] = 1
                            Phantom = pd.concat([Phantom_Contours_Internal, Phantom_Contours_External], ignore_index=True)
                            #-----------------------------------------------------------------------------------------------------------------------------------------------------
                            #Correct slice thickness
                            ListPatientz  = sorted(Patient['z'].unique().tolist())
                            PST = min([t - s for s, t in zip(ListPatientz, ListPatientz[1:])])
                            ListZPSTPhantom = np.arange(round_nearest(Phantom['z'].min(), PST),
                                                        round_nearest(Phantom['z'].max(), PST) + PST, PST, dtype=float)
                            ListPhantomz  = sorted(Phantom['z'].unique().tolist())
                            df_phantout_ST = Patient
                            for height in ListZPSTPhantom:
                                ListPhantomdz = [abs(x-height) for x in ListPhantomz]
                                dzmin = min(ListPhantomdz)
                                z0 = ListPhantomz[ListPhantomdz.index(dzmin)]
                                df0 = Phantom[Phantom['z']==z0]
                                df0['z'] = height
                                df_phantout_ST = pd.concat([df_phantout_ST,df0], ignore_index=True)            
                            #-----------------------------------------------------------------------------------------------------------------------------------------------------
                            Sources_Dict = df_phantout_ST.drop_duplicates(subset=['z', 'Source'], keep='last')[['z', 'Source']]['z'].value_counts().to_dict()
                            df_phantout_ST['NSources'] = df_phantout_ST.z.apply(lambda x: Sources_Dict.get(x))
                            df_phantout_ST['Polar']  = df_phantout_ST.apply(lambda row: cart_to_pol(row['x'], row['y'], CentreJonctionPatient_x, CentreJonctionPatient_y) , axis=1)
                            df_phantout_ST['rpol']  = df_phantout_ST.apply(lambda row: row['Polar'][0] , axis=1)
                            df_phantout_ST['tpol']  = df_phantout_ST.apply(lambda row: row['Polar'][1] , axis=1)
                            df_phantout_ST['tpolr']  = df_phantout_ST.apply(lambda row: round_nearest(row['Polar'][1], 0.1) , axis=1)
                            Rmax_Dict = df_phantout_ST.groupby(['z', 'tpolr'])['rpol'].max().to_dict()
                            Rmax_External_Dict = df_phantout_ST[df_phantout_ST['RTROIInterpretedType'] == 'EXTERNAL'].groupby(['z', 'tpolr'])['rpol'].max().to_dict()
                            df_phantout_ST['z_tpolr'] = df_phantout_ST[['z', 'tpolr']].apply(tuple, axis=1)                        
                            df_phantout_ST['Rmax'] = df_phantout_ST.z_tpolr.apply(lambda x: Rmax_Dict.get(x))
                            df_phantout_ST['Rmax_External'] = df_phantout_ST.z_tpolr.apply(lambda x: Rmax_External_Dict.get(x))
                            df_phantout_ST['Check_r'] = df_phantout_ST.apply(lambda row: row['Rmax_External'] - row['Rmax'], axis=1)
                            df_phantout_ST['x'] = df_phantout_ST.apply(lambda row: (row['rpol'] + abs(row['Check_r']) + 5)*np.cos(row['tpol']) + CentreJonctionPatient_x 
                                                                    if ((row['NSources'] == 2) & (row['Source'] == 1) & (row['RTROIInterpretedType']=='EXTERNAL') & (row['Check_r'] <= 0)) else row['x'] , axis=1)
                            df_phantout_ST['y'] = df_phantout_ST.apply(lambda row: (row['rpol']  + abs(row['Check_r']) + 5)*np.sin(row['tpol']) + CentreJonctionPatient_y 
                                                                    if ((row['NSources'] == 2) & (row['Source'] == 1) & (row['RTROIInterpretedType']=='EXTERNAL') & (row['Check_r'] <= 0)) else row['y'] , axis=1)
                            df_phantout_ST = df_phantout_ST[['PatientID',
                                                            'RTROIInterpretedType',
                                                            'ROIName',
                                                            'ROINumber',
                                                            'ROIContourNumber',
                                                            'ROIContourIndex', 
                                                            'ROIContourPointNumber',
                                                            'x',
                                                            'y',
                                                            'z',
                                                            'Source']]
                            df_phantout_ST['Color']  = df_phantout_ST.apply(lambda row: -100 if ((row['Source']==1) & (row['RTROIInterpretedType']=='EXTERNAL')) else row['ROINumber'], axis=1)
                            PatientFinal = 'Patient_' + Patient.iloc[0]['PatientID'] + '_' + Phantom.iloc[0]['PatientID'] + '.txt'
                            df_phantout_ST[df_phantout_ST['Source']==0].to_csv(os.path.join(repert_actu, PatientFinal), sep='\t', encoding='utf-8', index=False)

                            PhantomFinal = 'Phantom_' + Patient.iloc[0]['PatientID'] + '_' + Phantom.iloc[0]['PatientID'] + '.txt'
                            df_phantout_ST[df_phantout_ST['Source']==1].to_csv(os.path.join(repert_actu, PhantomFinal), sep='\t', encoding='utf-8', index=False)
    
                            Patient_Phantom = Patient.iloc[0]['PatientID'] + '_' + Phantom.iloc[0]['PatientID'] + '.txt'
                            
                            df_phantout_ST.to_csv(os.path.join(repert_actu, Patient_Phantom), sep='\t', encoding='utf-8', index=False)
                            print('------------------------','path : repert_actu', repert_actu)
                            print('------------------------','path : Patient phantom final', Patient_Phantom)
                            final_path_file.append(repert_actu + '/' + Patient_Phantom)
                            print('------------------------','final path path : ', final_path_file)

                        #=====================================================================================================================================================

def get_final_path():
    return final_path_file[-1]
#df_phantout_ST[df_phantout_ST['Source']==1]['ROIName'].unique().tolist()
