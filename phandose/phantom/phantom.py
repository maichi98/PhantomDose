#=====================================================================================================================================================
#-----------------------------------------------------------------------------------------------------------------------------------------------------
import os
import numpy as np
from scipy.interpolate import interp1d
from statistics import mode
import pandas as pd
import cv2
import time
import warnings
import subprocess
import multiprocessing
import json

warnings.filterwarnings("ignore")

exit = False

def exit_signal_handler(signal, frame):
    global exit
    print("Terminate signal received")
    exit = True
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#Arrondi au plus proche multiple de a
def round_nearest(x, a):
    return round(round(x / a) * a, 2)
#--------------------------------#--------------------------------------------------------------------------------
#Cartesian to polar coordinates
def cart_to_pol(x, y, x_c, y_c, deg = True):
    complex_format = x - x_c + 1j * (y - y_c)
    return np.abs(complex_format), np.angle(complex_format, deg = False)
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#Contour Area : Calcule la surface d'un coutour
def Get_Area(SelectedContours):
    ZList = sorted(SelectedContours.z.unique().tolist())
    AreaDf = pd.DataFrame()
    for z in ZList:
        Coupe = SelectedContours[SelectedContours['z'] == z]
        ROINumberList = sorted(Coupe.ROINumber.unique().tolist())
        for r in ROINumberList:
            ROI = Coupe[Coupe['ROINumber'] == r]
            ROIContourNumberList = sorted(ROI.ROIContourNumber.unique().tolist())
            for c in ROIContourNumberList:
                Contour = ROI[ROI['ROIContourNumber'] == c]
                Contour = Contour.round({'x': 0, 'y': 0})
                Contour = Contour.drop_duplicates(subset=['x', 'y'], keep='last')
                ctr = Contour[['x','y']].to_numpy()
                ctrint = np.array([ctr]).astype(np.int32)
                XUL, YUL, WR, HR = cv2.boundingRect(ctrint)
                Centrex = XUL + WR/2
                Centrey = YUL + HR/2
                area = cv2.contourArea(ctrint)
                data = {'Centrex': [Centrex], 'Centrey': [Centrey], 'z': [z] ,
                        'ROIName': [Contour.iloc[0]['ROIName']],
                        'ROINumber': [r],
                        'ROIContourNumber': [c],
                        'Area': [area]}
                df0 = pd.DataFrame (data, columns = ['Centrex', 'Centrey', 'z', 'ROIName', 'ROINumber', 'ROIContourNumber', 'Area'])
                AreaDf = pd.concat([AreaDf,df0], ignore_index=True)            
    return AreaDf
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#Phantoms available : Récupère la liste des fantomes fantomes
phantomLib_path = os.environ.get("PHANTOMLIB_PATH")
print(phantomLib_path)

PhantomLib = os.path.normpath(str(phantomLib_path))
All_Phantoms = [name for name in os.listdir(PhantomLib) if name.endswith('.txt')] #dir de phantomLib
All_Phantoms_df = pd.DataFrame({'Phantom':All_Phantoms})
All_Phantoms_df['Position'] = All_Phantoms_df.apply(lambda x : x.Phantom.split('_')[1], axis = 1)
All_Phantoms_df['Sex'] = All_Phantoms_df.apply(lambda x : x.Phantom.split('_')[2], axis = 1)
All_Vertebrae = ['vertebrae C1', 'vertebrae C2', 'vertebrae C3', 'vertebrae C4', 'vertebrae C5', 'vertebrae C6', 'vertebrae C7',
                 'vertebrae T1', 'vertebrae T2', 'vertebrae T3', 'vertebrae T4', 'vertebrae T5', 'vertebrae T6', 'vertebrae T7', 'vertebrae T8', 'vertebrae T9', 'vertebrae T10', 'vertebrae T11', 'vertebrae T12',
                 'vertebrae L1', 'vertebrae L2', 'vertebrae L3', 'vertebrae L4', 'vertebrae L5',
                 'vertebrae S1']
#-----------------------------------------------------------------------------------------------------------------------------------------------------
patient_path = os.environ.get("PATIENT_PATH")
Projet = os.path.join(patient_path)
_DFS_ = os.path.join(os.path.dirname(Projet),'_DFS_')
print(f"---------------script6 {_DFS_}")
sub_python = os.environ.get("PATH_SUB_PYTHON")
subprocess.run([sub_python, "Phandose_pyside/src/script_2_PatientsCharacteristics_AXEL_V00.py"])
PatientsCharacteristicsDf = pd.read_pickle(os.path.join(_DFS_,'PatientsCharacteristicsDf.pkl')) #On a besoin d'avoir lancé Le programme_2 pour créer _DFS_

PatientList = pd.unique(PatientsCharacteristicsDf[PatientsCharacteristicsDf['Type'] == 'CT_TO_TOTALSEGMENTATOR']['PatientID']).tolist()

#Possibilité de sélectionner un patient de la liste !
PatientList = ['AGORL_P33']

boom = []


def short_stop_subprocess():
    with open("pause_signal.txt", "w") as f:
            f.write("pause")
    time.sleep(5)

    with open("pause_signal.txt", "r") as f:
        signal_ph = f.read().strip()

    while signal_ph == "pause":
        print("Script B paused.")
        # Attendre un court instant
        time.sleep(1)
        # Relire le fichier de signal de pause
        with open("pause_signal.txt", "r") as f:
            signal_ph = f.read().strip() 
    
def save_selected_phantom(phantom_list):
    data_ph = \
        {
            "phantom_list" : phantom_list 
        
        }
    with open("list_phantom.json", "w") as f:
        json.dump(data_ph, f)


for Pat in PatientList:
    Selected_Phantoms_List = ["_FFDL_M_ 201919998LF_.txt", "_FFDR_F_ 201802212WX_.txt", "_FFS_M_ 201815978BR_.txt"]
    
    # queue = multiprocessing.Queue()
    # queue.put(Selected_Phantoms_List)

    #TODO ecrire un fichier json selectedphant
    save_selected_phantom(Selected_Phantoms_List)
    short_stop_subprocess()

    # TODO Remove SystemExit
    exit()
    # print(" Pause terminé")
    

    print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print('Patient: ', Pat)
    print('-----------------------------------------------------------')
    subprocess.run([sub_python, "Phandose_pyside/src/script_5_Nifti_To_xyz_AXEL_V00.py"])
    Projet = os.path.dirname(os.path.join(patient_path))

    if os.path.isfile(os.path.join(Projet,Pat, 'XYZ', 'Patient.txt')): #Il faut le programme qui crée Patient.txt
        #------------------------------------------------------
        #Phantoms of the same sex and same position as the patient
        PatientCharacteristics = PatientsCharacteristicsDf[PatientsCharacteristicsDf['PatientID'] == Pat].reset_index(drop=True)
        PatientSex = PatientCharacteristics[PatientCharacteristics['Type'] == 'CT_TO_TOTALSEGMENTATOR'].iloc[0]['PatientSex']
        PatientPosition = PatientCharacteristics[PatientCharacteristics['Type'] == 'CT_TO_TOTALSEGMENTATOR'].iloc[0]['PatientPosition']
        Patient_Contours=pd.read_csv(os.path.join(Projet, Pat, 'XYZ', 'Patient.txt'), encoding = "ISO-8859-1", sep='\t',header=0)
        Patient_Contours = Patient_Contours[~Patient_Contours['ROIName'].isin(['body', 'skin'])]
        Patient_Contours[['Origine', 'Section']] = ['Patient', 0]
        Patient_Contours_List =  pd.unique(Patient_Contours['ROIName']).tolist()
        Patient_Bottomz = Patient_Contours['z'].min()
        Patient_Topz = Patient_Contours['z'].max()
        Patient_Vertebrae_List = [x for x in pd.unique(Patient_Contours['ROIName']).tolist() if x.split(' ')[0] == 'vertebrae']
        Patient_Full_Vertebrae_df = pd.DataFrame()
        for v in Patient_Vertebrae_List:
            Vertebrae_Bottomz = Patient_Contours[Patient_Contours['ROIName'] == v]['z'].min()
            Vertebrae_Topz = Patient_Contours[Patient_Contours['ROIName'] == v]['z'].max()
            df0 = pd.DataFrame(data={'ROIName': [v],
                                     'Full': [(Vertebrae_Bottomz > Patient_Bottomz) and (Vertebrae_Topz < Patient_Topz)]})
            Patient_Full_Vertebrae_df = pd.concat([Patient_Full_Vertebrae_df, df0], ignore_index=True)
        Patient_Full_Vertebrae_List = pd.unique(Patient_Full_Vertebrae_df[Patient_Full_Vertebrae_df['Full']==True]['ROIName']).tolist()
        Patient_Full_Vertebrae_Size = Patient_Contours[Patient_Contours['ROIName'].isin(Patient_Full_Vertebrae_List)]['z'].max() - \
                                      Patient_Contours[Patient_Contours['ROIName'].isin(Patient_Full_Vertebrae_List)]['z'].min()
        Barydf_Patient = pd.DataFrame()
        for org in Patient_Full_Vertebrae_List:
            Barx = Patient_Contours[Patient_Contours['ROIName'] == org]['x'].mean()
            Bary = Patient_Contours[Patient_Contours['ROIName'] == org]['y'].mean()
            Barz = Patient_Contours[Patient_Contours['ROIName'] == org]['z'].mean()
            df0 = pd.DataFrame(data={'Organ': [org], 'Rts': ['Patient_Contours'],'Barx': [Barx], 'Bary': [Bary],'Barz': [Barz]})
            Barydf_Patient = pd.concat([Barydf_Patient, df0], ignore_index=True)
        Baryz = sorted(Barydf_Patient['Barz'].unique().tolist())
        Barydz = [t - s for s, t in zip(Baryz, Baryz[1:])]
        dzMean = sum(Barydz)/len(Barydz)
        #-------------------------------------------------------------------------------------------------------------------------
        #Junction Top vertabrae
        if 'skull' in Patient_Contours_List:
            skull_Topz = Patient_Contours[Patient_Contours['ROIName']=='skull']['z'].max()
            SkzullZmin = Patient_Contours[Patient_Contours['ROIName'] == 'skull']['z'].min()
            Barz_TopVertabrae_Patient = Barydf_Patient[Barydf_Patient['Barz'] < (SkzullZmin - 3*dzMean)]['Barz'].max()
            JunctionTop = (skull_Topz == Patient_Topz)
            print('JunctionTop =', JunctionTop)
        else:
            JunctionTop = True
            print('JunctionTop =', JunctionTop)
            Barz_TopVertabrae_Patient = Barydf_Patient['Barz'].max()
        Barx_TopVertabrae_Patient = Barydf_Patient.loc[Barydf_Patient['Barz']== Barz_TopVertabrae_Patient, 'Barx'].values[0]
        Bary_TopVertabrae_Patient = Barydf_Patient.loc[Barydf_Patient['Barz']== Barz_TopVertabrae_Patient, 'Bary'].values[0]
        JunctionTopVertabrae = Barydf_Patient[Barydf_Patient['Barz'] == Barz_TopVertabrae_Patient].iloc[0]['Organ']
        if JunctionTop == True:       
            JunctionPatientTop = Patient_Contours[Patient_Contours['ROIName'] == 'body trunc']
            JunctionPatientTop['Ecart'] = abs(JunctionPatientTop['z'] - Barz_TopVertabrae_Patient)
            EcartMin = JunctionPatientTop['Ecart'].min()
            JunctionPatientTop = JunctionPatientTop[JunctionPatientTop['Ecart'] == EcartMin]
            Patient_Contours = Patient_Contours[Patient_Contours['z'] <= JunctionPatientTop.iloc[0]['z']]
            AreaJunctionPatientTop = Get_Area(JunctionPatientTop)
            AreaJunctionPatientTop['Centrality'] = abs(AreaJunctionPatientTop['Centrex'])
            CentreMin = AreaJunctionPatientTop['Centrality'].min()
            ContourNum = AreaJunctionPatientTop.loc[AreaJunctionPatientTop['Centrality']== CentreMin, 'ROIContourNumber'].values[0]
            JunctionPatientTop = JunctionPatientTop[JunctionPatientTop['ROIContourNumber'] == ContourNum]
            CtrPatient = JunctionPatientTop[['x','y']].to_numpy()
            CtrintPatient = np.array([CtrPatient]).astype(np.int32)
            XULPatient, YULPatient, WRPatient, HRPatient = cv2.boundingRect(CtrintPatient)
            RectanglePatientTop = np.array([[XULPatient, YULPatient] ,[XULPatient, YULPatient + HRPatient], [XULPatient + WRPatient,YULPatient + HRPatient] , [XULPatient + WRPatient,YULPatient]])
            JunctionPatientTop['Polar']  = JunctionPatientTop.apply(lambda row: cart_to_pol(row['x'], row['y'],
                                                                                AreaJunctionPatientTop.iloc[0]['Centrex'],
                                                                                AreaJunctionPatientTop.iloc[0]['Centrey']) , axis=1)
            JunctionPatientTop['rpat'] = JunctionPatientTop.apply(lambda row: row['Polar'][0], axis=1)
            JunctionPatientTop['tpat'] = JunctionPatientTop.apply(lambda row: row['Polar'][1], axis=1)
            JunctionPatientTop = JunctionPatientTop.drop_duplicates(subset=['tpat'], keep='last')
            X = JunctionPatientTop['tpat'].to_numpy()
            y = JunctionPatientTop['rpat'].to_numpy()
            InterpJunctionPatientTop = interp1d(X, y, fill_value="extrapolate", kind='slinear')
        #-------------------------------------------------------------------------------------------------------------------------
        #Junction Bottom vertabrae
        JunctionBottom = ((set(['femur left', 'femur right']).issubset(pd.unique(Patient_Contours['ROIName']).tolist())) == False)
        print('JunctionBottom =', JunctionBottom)
        if JunctionBottom == True:
            Barz_BottomVertabrae_Patient = Barydf_Patient['Barz'].min()
            Barx_BottomVertabrae_Patient = Barydf_Patient.loc[Barydf_Patient['Barz']== Barz_BottomVertabrae_Patient, 'Barx'].values[0]
            Bary_BottomVertabrae_Patient = Barydf_Patient.loc[Barydf_Patient['Barz']== Barz_BottomVertabrae_Patient, 'Bary'].values[0]
            JunctionBottomVertabrae = Barydf_Patient[Barydf_Patient['Barz'] == Barz_BottomVertabrae_Patient].iloc[0]['Organ']
            JunctionPatientBottom = Patient_Contours[Patient_Contours['ROIName'] == 'body trunc']
            JunctionPatientBottom['Ecart'] = abs(JunctionPatientBottom['z'] - Barz_BottomVertabrae_Patient)
            EcartMin = JunctionPatientBottom['Ecart'].min()
            JunctionPatientBottom = JunctionPatientBottom[JunctionPatientBottom['Ecart'] == EcartMin]
            Patient_Contours = Patient_Contours[Patient_Contours['z'] >= JunctionPatientBottom.iloc[0]['z']]
            AreaJunctionPatientBottom = Get_Area(JunctionPatientBottom)
            AreaJunctionPatientBottom['Centrality'] = abs(AreaJunctionPatientBottom['Centrex'])
            CentreMin = AreaJunctionPatientBottom['Centrality'].min()
            ContourNum = AreaJunctionPatientBottom.loc[AreaJunctionPatientBottom['Centrality']== CentreMin, 'ROIContourNumber'].values[0]
            JunctionPatientBottom = JunctionPatientBottom[JunctionPatientBottom['ROIContourNumber'] == ContourNum]
            CtrPatient = JunctionPatientBottom[['x','y']].to_numpy()
            CtrintPatient = np.array([CtrPatient]).astype(np.int32)
            XULPatient, YULPatient, WRPatient, HRPatient = cv2.boundingRect(CtrintPatient)
            RectanglePatientBottom = np.array([[XULPatient, YULPatient] ,[XULPatient, YULPatient + HRPatient], [XULPatient + WRPatient,YULPatient + HRPatient] , [XULPatient + WRPatient,YULPatient]])
            JunctionPatientBottom['Polar']  = JunctionPatientBottom.apply(lambda row: cart_to_pol(row['x'], row['y'],
                                                                                      AreaJunctionPatientBottom.iloc[0]['Centrex'],
                                                                                      AreaJunctionPatientBottom.iloc[0]['Centrey']) , axis=1)
            JunctionPatientBottom['rpat'] = JunctionPatientBottom.apply(lambda row: row['Polar'][0], axis=1)
            JunctionPatientBottom['tpat'] = JunctionPatientBottom.apply(lambda row: row['Polar'][1], axis=1)
            JunctionPatientBottom = JunctionPatientBottom.drop_duplicates(subset=['tpat'], keep='last')
            X = JunctionPatientBottom['tpat'].to_numpy()
            y = JunctionPatientBottom['rpat'].to_numpy()
            InterpJunctionPatientBottom = interp1d(X, y, fill_value="extrapolate", kind='slinear')
        #-----------------------------------------------------------------------------------------------------------------------------------------------------
        #-----------------------------------------------------------------------------------------------------------------------------------------------------
        #-----------------------------------------------------------------------------------------------------------------------------------------------------
        #Il fait une premier filtre sur le sexe et la position du patient
        #Phantom Selection
        #Sex and Position
        Phantoms_df = All_Phantoms_df[(All_Phantoms_df['Sex'] == PatientSex) & 
                                      (All_Phantoms_df['Position'] == PatientPosition)].reset_index(drop=True)
        Phantoms_df['SizeRatio'] = -1
        #-----------------------------------------------------------------------------------------------------------------------------------------------------
        # filtre sur la taille du patient : estimée à partir des vertèbres
        #Comparing Phantoms to Patient according to size
        Phantoms_List = pd.unique(Phantoms_df['Phantom']).tolist()
        for f in Phantoms_List:
            Phantom = pd.read_csv(os.path.join(PhantomLib, f), encoding = "ISO-8859-1", sep='\t',header=0)
            if set(All_Vertebrae).issubset([x for x in pd.unique(Phantom['ROIName']).tolist() if x.split(' ')[0] == 'vertebrae']):
                Phantom_Full_Vertebrae_Size = Phantom[Phantom['ROIName'].isin(Patient_Full_Vertebrae_List)]['z'].max() - \
                                              Phantom[Phantom['ROIName'].isin(Patient_Full_Vertebrae_List)]['z'].min()
                Phantoms_df.loc[Phantoms_df['Phantom'] == f, 'SizeRatio'] = round(100*abs(1 - Phantom_Full_Vertebrae_Size/Patient_Full_Vertebrae_Size))
        Phantoms_df = Phantoms_df[(Phantoms_df['SizeRatio'] != -1) & (Phantoms_df['SizeRatio'] <= 10)]
        #------------------------------------------------------
        #Filtre sur le poids : estimé à partir des boites eglobantes au niveau de la junction inf
        #Comparing Phantoms to Patient according to body weigth
        Patient_Body_At_Last_Full_Vertebra = Patient_Contours[(Patient_Contours['ROIName'] == 'body trunc') &
                                                              (Patient_Contours['z'] == \
                                                               Patient_Contours[Patient_Contours['ROIName'].isin(Patient_Full_Vertebrae_List)]['z'].min())]
        CtrintPatient = Patient_Body_At_Last_Full_Vertebra[['x','y']].to_numpy().astype(np.int32)
        XULPatient, YULPatient, WRPatient, HRPatient = cv2.boundingRect(CtrintPatient)
        Phantoms_List = pd.unique(Phantoms_df['Phantom']).tolist()
        print('Phantoms_List: ', len(Phantoms_List))
        if len(Phantoms_List) > 0:
            for f in Phantoms_List:
                Phantom = pd.read_csv(os.path.join(PhantomLib, f), encoding = "ISO-8859-1", sep='\t',header=0)
                Phantom_Body_At_Last_Full_Vertebra = Phantom[(Phantom['ROIName'] == 'body trunc') &
                                                             (Phantom['z'] == \
                                                              Phantom[Phantom['ROIName'].isin(Patient_Full_Vertebrae_List)]['z'].min())]
                CtrintPhantom = Phantom_Body_At_Last_Full_Vertebra[['x','y']].to_numpy().astype(np.int32)
                XULPhantom, YULPhantom, WRPhantom, HRPhantom = cv2.boundingRect(CtrintPhantom)
                Phantoms_df.loc[Phantoms_df['Phantom'] == f, 'Thinner'] = (WRPatient >= (WRPhantom - 25) and HRPatient >= (HRPhantom - 25))
            Phantoms_df = Phantoms_df[Phantoms_df['Thinner'] == True].reset_index(drop=True)
        #===============================================================================================================================================================================            
            """
            C'est ces phantomes qu'il afficher : ce sont les fantôlmes liés au poatient
            """
        #===============================================================================================================================================================================            
        Selected_Phantoms_List = pd.unique(Phantoms_df['Phantom']).tolist()
        print(Selected_Phantoms_List)
        
        save_selected_phantom(Selected_Phantoms_List)
        short_stop_subprocess()
        print("reprise script 6")
        # time.sleep(15915)

        # load the list that will be use in application
        # os.environ["LIST_PHANTOM_AVAILABLE"] = Selected_Phantoms_List
        
        """
        Donne le possibilité de sécetionner un de ces Phantômes
        """
        Selected_Phantoms_List= ['_HFS_M_ 201709084NS_.txt']
        print('Selected_Phantoms_List: ', len(Selected_Phantoms_List))
        #Fusionne le patient sélectionné et le Fantôme sélectionné
        for sf in Selected_Phantoms_List:
            print('Selected Phantom: ', sf)
            #---------------------------------------------------------------------------------------------------------------------------------
            start_time = time.time()
            #-----------------------------------------------------------------------------------------------------------------------------------------------------
            df_Phantom_Top = pd.DataFrame()
            df_Phantom_Bottom = pd.DataFrame()
            Phantom_Contours = pd.read_csv(os.path.join(PhantomLib, sf), encoding = "ISO-8859-1", sep='\t',header=0)
            Phantom_Contours = Phantom_Contours[~Phantom_Contours['ROIName'].isin(['body', 'skin'])]
            Phantom_Contours['Origine'] = 'Phantom'
            #-----------------------------------------------------------------------------------------------------------------------------------------------------
            if JunctionTop == True:
                print('JunctionTop')
                Barx_Phantom = Phantom_Contours[Phantom_Contours['ROIName'] == JunctionTopVertabrae]['x'].mean()
                Bary_Phantom = Phantom_Contours[Phantom_Contours['ROIName'] == JunctionTopVertabrae]['y'].mean()
                Barz_Phantom = Phantom_Contours[Phantom_Contours['ROIName'] == JunctionTopVertabrae]['z'].mean()
                Phantom_Contours_Top = Phantom_Contours[Phantom_Contours['z'] >= Barz_Phantom]
                Phantom_Contours_Top['x'] = Phantom_Contours_Top['x'] + (Barx_TopVertabrae_Patient - Barx_Phantom)
                Phantom_Contours_Top['y'] = Phantom_Contours_Top['y'] + (Bary_TopVertabrae_Patient - Bary_Phantom)
                Phantom_Contours_Top['z'] = Phantom_Contours_Top['z'] + (Barz_TopVertabrae_Patient - Barz_Phantom)
                Phantom_Contours_Top_Zmin = Phantom_Contours_Top['z'].min()
                JunctionPhantom = Phantom_Contours_Top[(Phantom_Contours_Top['ROIName'].isin(['body trunc'])) &
                                                       (Phantom_Contours_Top['z'] == Phantom_Contours_Top_Zmin)]
                AreaJunctionPhantom = Get_Area(JunctionPhantom)
                AreaJunctionPhantom['Central'] = abs(AreaJunctionPhantom['Centrex'])
                CentreMin = AreaJunctionPhantom['Central'].min()
                ContourNum = AreaJunctionPhantom.loc[AreaJunctionPhantom['Central']== CentreMin, 'ROIContourNumber'].values[0]
                JunctionPhantom = JunctionPhantom[JunctionPhantom['ROIContourNumber'] == ContourNum]
                CtrPhantom = JunctionPhantom[['x','y']].to_numpy()
                CtrintPhantom = np.array([CtrPhantom]).astype(np.int32)
                XULPhantom, YULPhantom, WRPhantom, HRPhantom = cv2.boundingRect(CtrintPhantom)
                RectanglePhantomTop = np.array([[XULPhantom, YULPhantom] ,[XULPhantom, YULPhantom + HRPhantom], [XULPhantom + WRPhantom,YULPhantom + HRPhantom] , [XULPhantom + WRPhantom,YULPhantom]])
                h, status = cv2.findHomography(RectanglePhantomTop, RectanglePatientTop)
                Phantom_Contours_Top['xh'] = Phantom_Contours_Top.apply(lambda row: ((h[0,0]*row['x'] + h[0,1]*row['y'] + h[0,2])/(h[2,0]*row['x'] + h[2,1]*row['y'] + h[2,2])) if row['ROIName'] == 'body trunc' else row['x'], axis=1) 
                Phantom_Contours_Top['yh'] = Phantom_Contours_Top.apply(lambda row: ((h[1,0]*row['x'] + h[1,1]*row['y'] + h[1,2])/(h[2,0]*row['x'] + h[2,1]*row['y'] + h[2,2])) if row['ROIName'] == 'body trunc' else row['y'], axis=1) 
                Phantom_Contours_Top['zh'] = Phantom_Contours_Top['z']
                Phantom_Contours_Top = Phantom_Contours_Top.drop(['x', 'y', 'z'], axis=1)
                Phantom_Contours_Top = Phantom_Contours_Top.rename(columns={'xh': 'x', 'yh': 'y', 'zh': 'z'})
                #-----------------------------------------------------------------------------------------------------------------------------------------------------
                #Phantom                       
                Lsmooth = 20
                Phantom_BodyTrunc = Phantom_Contours_Top[Phantom_Contours_Top['ROIName'] == 'body trunc']
                Phantom_BodyTrunc['dz'] = abs(Phantom_BodyTrunc['z'] - JunctionPatientTop.iloc[0]['z'] - Lsmooth)
                dzmin = Phantom_BodyTrunc['dz'].min()
                SmoothJunctionPhantom = Phantom_BodyTrunc[Phantom_BodyTrunc['dz'] == dzmin]
                SmoothJunctionPhantom['Polar']  = SmoothJunctionPhantom.apply(lambda row: cart_to_pol(row['x'], row['y'],
                                                                                          AreaJunctionPatientTop.iloc[0]['Centrex'],
                                                                                          AreaJunctionPatientTop.iloc[0]['Centrey']) , axis=1)
                SmoothJunctionPhantom['rpat'] = SmoothJunctionPhantom.apply(lambda row: row['Polar'][0], axis=1)
                SmoothJunctionPhantom['tpat'] = SmoothJunctionPhantom.apply(lambda row: row['Polar'][1], axis=1)
                SmoothJunctionPhantom = SmoothJunctionPhantom.drop_duplicates(subset=['tpat'], keep='last')
                X = SmoothJunctionPhantom['tpat'].to_numpy()
                y = SmoothJunctionPhantom['rpat'].to_numpy()
                InterpPhantom = interp1d(X, y, fill_value="extrapolate", kind='slinear')
                #-----------------------------------------------------------------------------------------------------------------------------------------------------
                #Apply interpolations to phantom body
                To_Smooth = Phantom_BodyTrunc[Phantom_BodyTrunc['z'] <= SmoothJunctionPhantom.iloc[0]['z']]
                To_Smooth['Polar'] = To_Smooth.apply(lambda row: cart_to_pol(row['x'], row['y'],
                                                                 AreaJunctionPatientTop.iloc[0]['Centrex'],
                                                                 AreaJunctionPatientTop.iloc[0]['Centrey']) ,
                                                                 axis=1)
                To_Smooth['teta'] = To_Smooth.apply(lambda row: row['Polar'][1] , axis=1)
                To_Smooth['pond'] = To_Smooth.apply(lambda row: (row['z']-JunctionPatientTop.iloc[0]['z'])/Lsmooth, axis=1)
                To_Smooth['rPred'] = To_Smooth.apply(lambda x: x.pond*InterpPhantom(x.teta) + (1-x.pond)*InterpJunctionPatientTop(x.teta), axis=1)
                To_Smooth['xPred'] = To_Smooth.apply(lambda x: x.rPred*np.cos(x.teta) + AreaJunctionPatientTop.iloc[0]['Centrex'], axis=1)
                To_Smooth['yPred'] = To_Smooth.apply(lambda x: x.rPred*np.sin(x.teta) + AreaJunctionPatientTop.iloc[0]['Centrey'], axis=1)
                To_Smooth = To_Smooth.drop(['x', 'y', 'Polar', 'teta', 'pond', 'rPred'], axis=1)
                To_Smooth = To_Smooth.rename(columns={'xPred': 'x', 'yPred': 'y'})
                #-----------------------------------------------------------------------------------------------------------------------------------------------------
                #Concact contours
                Phantom_Contours_Top_Internal = Phantom_Contours_Top[~Phantom_Contours_Top['ROIName'].isin(['body trunc', 'body extremities'])]
                Phantom_Contours_Top_BodyExtremities = Phantom_Contours_Top[Phantom_Contours_Top['ROIName'] == 'body extremities']
                Phantom_Contours_Top_BodyTrunc_NotSmooth = Phantom_Contours_Top[(Phantom_Contours_Top['ROIName'] == 'body trunc') &
                                                                                (Phantom_Contours_Top['z'] > SmoothJunctionPhantom.iloc[0]['z'])]
                df_Phantom_Top = pd.concat([Phantom_Contours_Top_Internal,
                                           Phantom_Contours_Top_BodyExtremities,
                                           Phantom_Contours_Top_BodyTrunc_NotSmooth,
                                           To_Smooth], ignore_index=True)
                df_Phantom_Top[['Origine', 'Section']] = ['Phantom', 1]
            #-----------------------------------------------------------------------------------------------------------------------------------------------------
            if JunctionBottom == True:
                print('JunctionBottom')
                Barx_Phantom = Phantom_Contours[Phantom_Contours['ROIName'] == JunctionBottomVertabrae]['x'].mean()
                Bary_Phantom = Phantom_Contours[Phantom_Contours['ROIName'] == JunctionBottomVertabrae]['y'].mean()
                Barz_Phantom = Phantom_Contours[Phantom_Contours['ROIName'] == JunctionBottomVertabrae]['z'].mean()
                Phantom_Contours_Bottom = Phantom_Contours[Phantom_Contours['z'] <= Barz_Phantom]
                Phantom_Contours_Bottom['x'] = Phantom_Contours_Bottom['x'] + (Barx_BottomVertabrae_Patient - Barx_Phantom)
                Phantom_Contours_Bottom['y'] = Phantom_Contours_Bottom['y'] + (Bary_BottomVertabrae_Patient - Bary_Phantom)
                Phantom_Contours_Bottom['z'] = Phantom_Contours_Bottom['z'] + (Barz_BottomVertabrae_Patient - Barz_Phantom)
                Phantom_Contours_Bottom_Zmax = Phantom_Contours_Bottom['z'].max()
                Phantom_Contours_Bottom_Body = Phantom_Contours_Bottom[Phantom_Contours_Bottom['ROIName'].isin(['body trunc', 'body extremities'])].reset_index(drop=True)
                Phantom_Contours_Bottom_Internal = Phantom_Contours_Bottom[~Phantom_Contours_Bottom['ROIName'].isin(['body trunc', 'body extremities'])].reset_index(drop=True)
                JunctionPhantom = Phantom_Contours_Bottom_Body[Phantom_Contours_Bottom_Body['z'] == Phantom_Contours_Bottom_Zmax].reset_index(drop=True)
                AreaJunctionPhantom = Get_Area(JunctionPhantom)
                AreaJunctionPhantom['Central'] = abs(AreaJunctionPhantom['Centrex'])
                CentreMin = AreaJunctionPhantom['Central'].min()
                ContourNum = AreaJunctionPhantom.loc[AreaJunctionPhantom['Central']== CentreMin, 'ROIContourNumber'].values[0]
                JunctionPhantom = JunctionPhantom[JunctionPhantom['ROIContourNumber'] == ContourNum]
                CtrPhantom = JunctionPhantom[['x','y']].to_numpy()
                CtrintPhantom = np.array([CtrPhantom]).astype(np.int32)
                XULPhantom, YULPhantom, WRPhantom, HRPhantom = cv2.boundingRect(CtrintPhantom)
                RectanglePhantomBottom = np.array([[XULPhantom, YULPhantom] ,[XULPhantom, YULPhantom + HRPhantom], [XULPhantom + WRPhantom,YULPhantom + HRPhantom] , [XULPhantom + WRPhantom,YULPhantom]])
                h, status = cv2.findHomography(RectanglePhantomBottom, RectanglePatientBottom)
                Phantom_Contours_Bottom['xh'] = Phantom_Contours_Bottom.apply(lambda row: (h[0,0]*row['x'] + h[0,1]*row['y'] + h[0,2])/(h[2,0]*row['x'] + h[2,1]*row['y'] + h[2,2]), axis=1) 
                Phantom_Contours_Bottom['yh'] = Phantom_Contours_Bottom.apply(lambda row: (h[1,0]*row['x'] + h[1,1]*row['y'] + h[1,2])/(h[2,0]*row['x'] + h[2,1]*row['y'] + h[2,2]), axis=1) 
                Phantom_Contours_Bottom['zh'] = Phantom_Contours_Bottom['z']
                Phantom_Contours_Bottom = Phantom_Contours_Bottom.drop(['x', 'y', 'z'], axis=1)
                Phantom_Contours_Bottom = Phantom_Contours_Bottom.rename(columns={'xh': 'x', 'yh': 'y', 'zh': 'z'})
                Lsmooth = 50
                Phantom_BodyTrunc = Phantom_Contours_Bottom[Phantom_Contours_Bottom['ROIName'] == 'body trunc']
                Phantom_BodyTrunc['dz'] = abs(abs(Phantom_BodyTrunc['z'] - JunctionPatientBottom.iloc[0]['z']) - Lsmooth)
                dzmin = Phantom_BodyTrunc['dz'].min()
                SmoothJunctionPhantom = Phantom_BodyTrunc[Phantom_BodyTrunc['dz'] == dzmin]
                SmoothJunctionPhantom['Polar']  = SmoothJunctionPhantom.apply(lambda row: cart_to_pol(row['x'], row['y'],
                                                                                          AreaJunctionPatientBottom.iloc[0]['Centrex'],
                                                                                          AreaJunctionPatientBottom.iloc[0]['Centrey']) , axis=1)
                SmoothJunctionPhantom['rpat'] = SmoothJunctionPhantom.apply(lambda row: row['Polar'][0], axis=1)
                SmoothJunctionPhantom['tpat'] = SmoothJunctionPhantom.apply(lambda row: row['Polar'][1], axis=1)
                SmoothJunctionPhantom = SmoothJunctionPhantom.drop_duplicates(subset=['tpat'], keep='last')
                X = SmoothJunctionPhantom['tpat'].to_numpy()
                y = SmoothJunctionPhantom['rpat'].to_numpy()
                InterpPhantom = interp1d(X, y, fill_value="extrapolate", kind='slinear')
                #-----------------------------------------------------------------------------------------------------------------------------------------------------
                #Apply interpolations to phantom body
                To_Smooth = Phantom_BodyTrunc[Phantom_BodyTrunc['z'] >= SmoothJunctionPhantom.iloc[0]['z']]
                To_Smooth['Polar'] = To_Smooth.apply(lambda row: cart_to_pol(row['x'], row['y'],
                                                                 AreaJunctionPatientBottom.iloc[0]['Centrex'],
                                                                 AreaJunctionPatientBottom.iloc[0]['Centrey']) ,
                                                                 axis=1)
                To_Smooth['teta'] = To_Smooth.apply(lambda row: row['Polar'][1] , axis=1)
                To_Smooth['pond'] = To_Smooth.apply(lambda row: (JunctionPatientBottom.iloc[0]['z'] - row['z'])/Lsmooth, axis=1)
                To_Smooth['rPred'] = To_Smooth.apply(lambda x: x.pond*InterpPhantom(x.teta) + (1-x.pond)*InterpJunctionPatientBottom(x.teta), axis=1)
                To_Smooth['xPred'] = To_Smooth.apply(lambda x: x.rPred*np.cos(x.teta) + AreaJunctionPatientBottom.iloc[0]['Centrex'], axis=1)
                To_Smooth['yPred'] = To_Smooth.apply(lambda x: x.rPred*np.sin(x.teta) + AreaJunctionPatientBottom.iloc[0]['Centrey'], axis=1)
                To_Smooth = To_Smooth.drop(['x', 'y', 'Polar', 'teta', 'pond', 'rPred'], axis=1)
                To_Smooth = To_Smooth.rename(columns={'xPred': 'x', 'yPred': 'y'})
                #-----------------------------------------------------------------------------------------------------------------------------------------------------
                #Concact contours
                Phantom_Contours_Bottom_Internal = Phantom_Contours_Bottom[~Phantom_Contours_Bottom['ROIName'].isin(['body trunc', 'body extremities'])]
                Phantom_Contours_Bottom_BodyExtremities = Phantom_Contours_Bottom[Phantom_Contours_Bottom['ROIName'] == 'body extremities']
                Phantom_Contours_Bottom_BodyTrunc_NotSmooth = Phantom_Contours_Bottom[(Phantom_Contours_Bottom['ROIName'] == 'body trunc') &
                                                                                      (Phantom_Contours_Bottom['z'] < SmoothJunctionPhantom.iloc[0]['z'])]
                df_Phantom_Bottom = pd.concat([Phantom_Contours_Bottom_Internal,
                                               Phantom_Contours_Bottom_BodyExtremities,
                                               Phantom_Contours_Bottom_BodyTrunc_NotSmooth,
                                               To_Smooth], ignore_index=True)
                df_Phantom_Bottom[['Origine', 'Section']] = ['Phantom', 2]
            #-----------------------------------------------------------------------------------------------------------------------------------------------------
            df_Patient_Pantom = pd.concat([Patient_Contours,
                                           df_Phantom_Top,
                                           df_Phantom_Bottom], ignore_index=True)
            df_Patient_Pantom = df_Patient_Pantom[['Origine', 'Section', 'ROIName', 'ROINumber', 'ROIContourNumber', 'ROIContourPointNumber', 'x', 'y', 'z']]
            df_Patient_Pantom = df_Patient_Pantom.dropna()
            df_Patient_Pantom.loc[df_Patient_Pantom['ROIName'].isin(['body trunc', 'body extremities']), 'ROIName'] = 'external'
            #------------------------------------------------------------------------------------------------------------------------
            ReSampledContours = pd.DataFrame()
            ListSections = sorted(df_Patient_Pantom['Section'].unique().tolist())
            ListROIs = sorted(df_Patient_Pantom['ROIName'].unique().tolist())
            ListPatient_Pantomz  = sorted(df_Patient_Pantom['z'].unique().tolist())
            ListZDiff =  [t - s for s, t in zip(ListPatient_Pantomz, ListPatient_Pantomz[1:])]
            ListZExpectedFull = np.arange(min(ListPatient_Pantomz), max(ListPatient_Pantomz), max(5, round(mode(ListZDiff))), dtype=float)
            ROINumber = 0
            for roiname in ListROIs:
                ROINumber = ROINumber + 1
                Roi = df_Patient_Pantom[df_Patient_Pantom['ROIName']==roiname]
                for Section in ListSections:
                    RoiSection = Roi[Roi['Section'] == Section]
                    ListRoiz  = sorted(RoiSection['z'].unique().tolist())
                    ListZDisired = [z for z in ListZExpectedFull if RoiSection['z'].min() <= z and z<=RoiSection['z'].max() ]
                    for height in ListZDisired:
                        Listdz = [abs(x-height) for x in ListRoiz]
                        dzmin = min(Listdz)
                        z0 = ListRoiz[Listdz.index(dzmin)]
                        df0 = RoiSection[RoiSection['z']==z0]
                        df0['z'] = height
                        df0['ROINumber'] = ROINumber
                        ListROIContourNumber  = sorted(df0['ROIContourNumber'].unique().tolist())
                        ROIContourNumber = 0
                        for ContourNumb in ListROIContourNumber:
                            ROIContourNumber = ROIContourNumber + 1
                            df00 = df0[df0['ROIContourNumber']==ContourNumb]
                            df00['ROIContourNumber'] = ROIContourNumber
                            df00 = df00.sort_values(by=['ROIContourNumber', 'ROIContourPointNumber', 'x', 'y', 'z'], ascending=([True, True,True,True,True])).reset_index(drop=True)
                            ReSampledContours = pd.concat([ReSampledContours, df00], ignore_index=True)
            #------------------------------------------------------------------------------------------------------------------------
            Patient_Pantom = 'PP_' + Pat + ' ' + sf
            print(os.path.join(os.path.dirname(os.path.join(patient_path)),Pat, 'XYZ', Patient_Pantom))
            ReSampledContours.to_csv(os.path.join(Projet,Pat, 'XYZ', Patient_Pantom), sep='\t', encoding='utf-8', index=False)
            print("--- %s seconds ---" % (time.time() - start_time))
            #---------------------------------------------------------------------------------------------------------------------------------
            #=====================================================================================================================================================


