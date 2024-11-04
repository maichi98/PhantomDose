# ====================================================================================================================
# -----------------------------------------------------------------------------------------------------------------
import os
import numpy as np
from scipy.interpolate import interp1d
from statistics import mode
import pandas as pd
import cv2
import time
import warnings
warnings.filterwarnings("ignore")


# ---------------------------------------------------------------------------------------------------------------------
def round_to_nearest_multiple(x, a) -> float:
    """
    Round a number to the nearest multiple of another number.

    Parameters
    ----------
    x : (float)
        The number to round.
    a : (float)
        The number to which x will be rounded.

    Returns
    -------
    float
        The rounded number.
    """

    return round(round(x / a) * a, 2)
# --------------------------------# --------------------------------------------------------------------------------


# Cartesian to polar coordinates
def cartesian_to_polar_coordinates(x, y, x_c, y_c) -> tuple[float, float]:
    """
    Convert Cartesian coordinates to polar coordinates.

    Parameters
    ----------
    x : (float)
        The x-coordinate of the point.
    y : (float)
        The y-coordinate of the point.
    x_c : (float)
        The x-coordinate of the center point.
    y_c : (float)
        The y-coordinate of the center point.

    Returns
    -------
    tuple[float, float]
        The radius and the angle of the polar coordinates.

    """
    complex_format = x - x_c + 1j * (y - y_c)
    return np.abs(complex_format), np.angle(complex_format, deg=False)


# ------------------------------------------------------------------------------------------------------------
# Calculate the area of a contour
def calculate_contour_area(df_contours: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the area of a contour.

    Parameters
    ----------
    df_contours : (pd.DataFrame)
        A DataFrame containing the contour points.
        The DataFrame must have the following columns:
            - x: x-coordinate of the contour point
            - y: y-coordinate of the contour point

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the area of the contour.
        The DataFrame has the following columns:
            - Centrex: the x-coordinate of the center of the contour
            - Centrey: the y-coordinate of the center of the contour
            - z
            - ROIName
            - ROINumber
            - ROIContourNumber
            - area: the area of the contour
    """

    def calculate_area(contour):
        rounded_contour = contour.round({'x': 0, 'y': 0}).drop_duplicates(subset=['x', 'y'], keep='last')
        center = np.array(rounded_contour[['x', 'y']].to_numpy()).astype(np.int32)
        xul, yul, wr, hr = cv2.boundingRect(center)
        center_x = xul + wr / 2
        center_y = yul + hr / 2
        area = cv2.contourArea(center)
        return pd.Series({'Centrex': center_x, 'Centrey': center_y, 'area': area})

    cols = ['z', 'ROINumber', 'ROIContourNumber']
    df_area = df_contours.groupby(cols).apply(calculate_area).reset_index()
    df_area['ROIName'] = df_contours.groupby(cols)['ROIName'].first().reset_index(drop=True)
    return df_area[['Centrex', 'Centrey', 'z', 'ROIName', 'ROINumber', 'ROIContourNumber', 'area']]


# ------------------------------------------------------------------------------------------------------------
def get_df_contours():

    path_contours = os.path.join(dir_project, patient, 'XYZ', 'Patient.txt')
    df_contours = pd.read_csv(path_contours, encoding="ISO-8859-1", sep='\t', header=0)
    df_contours[['Origine', 'Section']] = ['Patient', 0]

    return df_contours


def get_contours_barycenters(df_contours: pd.DataFrame) -> pd.DataFrame:

    """
    This function calculates the barycenter of each contour in the DataFrame.

    Parameters
    ----------
    df_contours : (pd.DataFrame),
        DataFrame with columns: ['ROIName', 'ROINumber', 'ROIContourNumber', 'ROIContourPointNumber', 'x', 'y', 'z']

    Returns
    -------
    pd.DataFrame
    a pandas DataFrame with columns: ['ROIName', 'ROINumber', 'ROIContourNumber', 'x', 'y', 'z']
    """

    # Check that there are no missing values in the DataFrame :
    if df_contours[["x", "y", "z"]].isnull().values.any():
        raise ValueError("The contours DataFrame shouldn't contain missing values in the columns 'x', 'y', 'z' !")

    # Compute the barycenter of each contour :
    df_barycenter = df_contours.groupby("ROIName")[["x", "y", "z"]].mean().reset_index()
    df_barycenter["Rts"] = 'Patient_Contours'

    df_barycenter = df_barycenter[["ROIName", "Rts", "x", "y", "z"]].rename(columns={"ROIName": "Organ",
                                                                                     "x": "Barx",
                                                                                     "y": "Bary",
                                                                                     "z": "Barz"})

    return df_barycenter


def is_vertebrae_fully_within_contours(df_contours: pd.DataFrame) -> pd.DataFrame:

    """
    Create a DataFrame indicating if each vertebra is fully within the contours.

    The function determines for each vertebra within the contours dataframe, whether it is fully
    within the contours or not, based on its z-coordinates.

    The DataFrame has two columns :
        - ROIName : Name of the vertebra
        - Full : Boolean indicating if the vertebra is fully within the contours

    Parameters
    ----------
    df_contours : pd.DataFrame
        The DataFrame containing the contours of the patient, each row must contain the following columns :
        ['ROIName', 'z']

    Returns
    -------
    pd.DataFrame
        The Full Vertebrae DataFrame, with columns : ['ROIName', 'Full']
    """

    # Check that there are no missing values in the DataFrame :
    if df_contours[["x", "y", "z"]].isnull().values.any():
        raise ValueError("The contours DataFrame shouldn't contain missing values in the columns 'x', 'y', 'z' !")

    list_vertebrae = df_contours.loc[df_contours['ROIName'].str.startswith('vertebrae'), 'ROIName'].unique().tolist()
    z_min, z_max = df_contours["z"].min(), df_contours["z"].max()

    # Compute the vertebrae_min_z and vertebrae_max_z for all vertebrae :
    vertebrae_z_min_max = df_contours.loc[df_contours['ROIName'].isin(list_vertebrae)] \
        .groupby('ROIName')['z'].agg(['min', 'max'])

    # Create a full vertebrae DataFrame :
    dict_full_vertebrae = [{"ROIName": vertebrae, "Full": (row["min"] > z_min) and (row["max"] < z_max)}
                           for vertebrae, row in vertebrae_z_min_max.iterrows()]

    df_full_vertebrae = pd.DataFrame(dict_full_vertebrae, columns=["ROIName", "Full"])

    return df_full_vertebrae


# -----------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------


# Phantom library :
dir_phantom_lib = os.path.normpath('/media/maichi/T7/PhantomLib')
list_phantoms = [name for name in os.listdir(dir_phantom_lib) if name.endswith('.txt')]
df_phantom_lib = pd.DataFrame({"Phantom": list_phantoms})
df_phantom_lib['Position'] = df_phantom_lib.apply(lambda x: x.Phantom.split('_')[1], axis=1)
df_phantom_lib['Sex'] = df_phantom_lib.apply(lambda x: x.Phantom.split('_')[2], axis=1)
list_all_vertebrae = ['vertebrae C1', 'vertebrae C2', 'vertebrae C3', 'vertebrae C4', 'vertebrae C5',
                      'vertebrae C6', 'vertebrae C7',
                      'vertebrae T1', 'vertebrae T2', 'vertebrae T3', 'vertebrae T4', 'vertebrae T5',
                      'vertebrae T6', 'vertebrae T7', 'vertebrae T8', 'vertebrae T9', 'vertebrae T10',
                      'vertebrae T11', 'vertebrae T12',
                      'vertebrae L1', 'vertebrae L2', 'vertebrae L3', 'vertebrae L4', 'vertebrae L5',
                      'vertebrae S1']

# --------------------------------------------------------------------------------------------------------------------


dir_project = "/media/maichi/T7/workspace"
_DFS_ = "/media/maichi/T7/_DFS_"

df_patients_characteristics = pd.read_pickle(os.path.join(_DFS_, 'PatientsCharacteristicsDf.pkl'))
list_patients = pd.unique(df_patients_characteristics[df_patients_characteristics['Type'] == 'CT_TO_TOTALSEGMENTATOR']['PatientID']).tolist()


for patient in list_patients:
    print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print('Patient: ', patient)
    print('-----------------------------------------------------------')
    if os.path.isfile(os.path.join(dir_project, patient, 'XYZ', 'Patient.txt')):
        # ------------------------------------------------------
        # Phantoms of the same sex and same position as the patient
        _df_patient_characteristics = df_patients_characteristics[df_patients_characteristics['PatientID'] == patient].reset_index(drop=True)

        patient_sex = _df_patient_characteristics[_df_patient_characteristics['Type'] == 'CT_TO_TOTALSEGMENTATOR'].iloc[0]['PatientSex']

        patient_position = _df_patient_characteristics[_df_patient_characteristics['Type'] == 'CT_TO_TOTALSEGMENTATOR'].iloc[0]['PatientPosition']

        df_contours = get_df_contours()

        list_patient_contours = pd.unique(df_contours['ROIName']).tolist()

        patient_bottom_z = df_contours['z'].min()

        patient_top_z = df_contours['z'].max()

        list_patient_vertebrae = [x for x in pd.unique(df_contours['ROIName']).tolist() if x.split(' ')[0] == 'vertebrae']

        df_full_vertebrae = pd.DataFrame()

        for v in list_patient_vertebrae:
            vertebrae_bottom_z = df_contours[df_contours['ROIName'] == v]['z'].min()
            vertebrae_top_z = df_contours[df_contours['ROIName'] == v]['z'].max()
            df0 = pd.DataFrame(data={'ROIName': [v],
                                     'Full': [(vertebrae_bottom_z > patient_bottom_z) and (vertebrae_top_z < patient_top_z)]})
            df_full_vertebrae = pd.concat([df_full_vertebrae, df0], ignore_index=True)

        list_patient_full_vertebrae = pd.unique(df_full_vertebrae[df_full_vertebrae['Full']]['ROIName']).tolist()
        Patient_Full_Vertebrae_Size = df_contours[df_contours['ROIName'].isin(list_patient_full_vertebrae)]['z'].max() - \
                                      df_contours[df_contours['ROIName'].isin(list_patient_full_vertebrae)]['z'].min()

        Barydf_Patient = pd.DataFrame()
        for org in list_patient_full_vertebrae:
            Barx = df_contours[df_contours['ROIName'] == org]['x'].mean()
            Bary = df_contours[df_contours['ROIName'] == org]['y'].mean()
            Barz = df_contours[df_contours['ROIName'] == org]['z'].mean()
            df0 = pd.DataFrame(data={'Organ': [org], 'Rts': ['Patient_Contours'], 'Barx': [Barx], 'Bary': [Bary], 'Barz': [Barz]})
            Barydf_Patient = pd.concat([Barydf_Patient, df0], ignore_index=True)

        Baryz = sorted(Barydf_Patient['Barz'].unique().tolist())
        Barydz = [t - s for s, t in zip(Baryz, Baryz[1:])]
        dzMean = sum(Barydz)/len(Barydz)

        # -------------------------------------------------------------------------------------------------------------------------
        #Junction Top vertabrae
        if 'skull' in list_patient_contours:
            skull_Topz = df_contours[df_contours['ROIName'] == 'skull']['z'].max()
            SkzullZmin = df_contours[df_contours['ROIName'] == 'skull']['z'].min()
            Barz_TopVertabrae_Patient = Barydf_Patient[Barydf_Patient['Barz'] < (SkzullZmin - 3*dzMean)]['Barz'].max()
            JunctionTop = (skull_Topz == Patient_Topz)
            print('JunctionTop =', JunctionTop)
        else:
            JunctionTop = True
            print('JunctionTop =', JunctionTop)
            Barz_TopVertabrae_Patient = Barydf_Patient['Barz'].max()
        Barx_TopVertabrae_Patient = Barydf_Patient.loc[Barydf_Patient['Barz'] == Barz_TopVertabrae_Patient, 'Barx'].values[0]
        Bary_TopVertabrae_Patient = Barydf_Patient.loc[Barydf_Patient['Barz'] == Barz_TopVertabrae_Patient, 'Bary'].values[0]
        JunctionTopVertabrae = Barydf_Patient[Barydf_Patient['Barz'] == Barz_TopVertabrae_Patient].iloc[0]['Organ']
        if JunctionTop == True:       
            JunctionPatientTop = df_contours[df_contours['ROIName'] == 'body trunc']
            JunctionPatientTop['Ecart'] = abs(JunctionPatientTop['z'] - Barz_TopVertabrae_Patient)
            EcartMin = JunctionPatientTop['Ecart'].min()
            JunctionPatientTop = JunctionPatientTop[JunctionPatientTop['Ecart'] == EcartMin]
            df_contours = df_contours[df_contours['z'] <= JunctionPatientTop.iloc[0]['z']]
            AreaJunctionPatientTop = calculate_contour_area(JunctionPatientTop)
            AreaJunctionPatientTop['Centrality'] = abs(AreaJunctionPatientTop['Centrex'])
            CentreMin = AreaJunctionPatientTop['Centrality'].min()
            ContourNum = AreaJunctionPatientTop.loc[AreaJunctionPatientTop['Centrality']== CentreMin, 'ROIContourNumber'].values[0]
            JunctionPatientTop = JunctionPatientTop[JunctionPatientTop['ROIContourNumber'] == ContourNum]
            CtrPatient = JunctionPatientTop[['x', 'y']].to_numpy()
            CtrintPatient = np.array([CtrPatient]).astype(np.int32)
            XULPatient, YULPatient, WRPatient, HRPatient = cv2.boundingRect(CtrintPatient)
            RectanglePatientTop = np.array([[XULPatient, YULPatient] ,[XULPatient, YULPatient + HRPatient], [XULPatient + WRPatient,YULPatient + HRPatient] , [XULPatient + WRPatient,YULPatient]])
            JunctionPatientTop['Polar'] = JunctionPatientTop.apply(lambda row: cartesian_to_polar_coordinates(row['x'], row['y'],
                                                                               AreaJunctionPatientTop.iloc[0]['Centrex'],
                                                                               AreaJunctionPatientTop.iloc[0]['Centrey']) , axis=1)
            JunctionPatientTop['rpat'] = JunctionPatientTop.apply(lambda row: row['Polar'][0], axis=1)
            JunctionPatientTop['tpat'] = JunctionPatientTop.apply(lambda row: row['Polar'][1], axis=1)
            JunctionPatientTop = JunctionPatientTop.drop_duplicates(subset=['tpat'], keep='last')
            X = JunctionPatientTop['tpat'].to_numpy()
            y = JunctionPatientTop['rpat'].to_numpy()
            InterpJunctionPatientTop = interp1d(X, y, fill_value="extrapolate", kind='slinear')
        # -------------------------------------------------------------------------------------------------------------------------
        #Junction Bottom vertabrae
        JunctionBottom = ((set(['femur left', 'femur right']).issubset(pd.unique(df_contours['ROIName']).tolist())) == False)
        print('JunctionBottom =', JunctionBottom)
        if JunctionBottom == True:

            Barz_BottomVertabrae_Patient = Barydf_Patient['Barz'].min()
            Barx_BottomVertabrae_Patient = Barydf_Patient.loc[Barydf_Patient['Barz'] == Barz_BottomVertabrae_Patient, 'Barx'].values[0]
            Bary_BottomVertabrae_Patient = Barydf_Patient.loc[Barydf_Patient['Barz'] == Barz_BottomVertabrae_Patient, 'Bary'].values[0]
            JunctionBottomVertabrae = Barydf_Patient[Barydf_Patient['Barz'] == Barz_BottomVertabrae_Patient].iloc[0]['Organ']


            JunctionPatientBottom = df_contours[df_contours['ROIName'] == 'body trunc']

            JunctionPatientBottom['Ecart'] = abs(JunctionPatientBottom['z'] - Barz_BottomVertabrae_Patient)

            EcartMin = JunctionPatientBottom['Ecart'].min()

            JunctionPatientBottom = JunctionPatientBottom[JunctionPatientBottom['Ecart'] == EcartMin]
            df_contours = df_contours[df_contours['z'] >= JunctionPatientBottom.iloc[0]['z']]
            AreaJunctionPatientBottom = calculate_contour_area(JunctionPatientBottom)
            AreaJunctionPatientBottom['Centrality'] = abs(AreaJunctionPatientBottom['Centrex'])
            CentreMin = AreaJunctionPatientBottom['Centrality'].min()
            ContourNum = AreaJunctionPatientBottom.loc[AreaJunctionPatientBottom['Centrality']== CentreMin, 'ROIContourNumber'].values[0]
            JunctionPatientBottom = JunctionPatientBottom[JunctionPatientBottom['ROIContourNumber'] == ContourNum]
            CtrPatient = JunctionPatientBottom[['x','y']].to_numpy()
            CtrintPatient = np.array([CtrPatient]).astype(np.int32)
            XULPatient, YULPatient, WRPatient, HRPatient = cv2.boundingRect(CtrintPatient)
            RectanglePatientBottom = np.array([[XULPatient, YULPatient] ,[XULPatient, YULPatient + HRPatient], [XULPatient + WRPatient,YULPatient + HRPatient] , [XULPatient + WRPatient,YULPatient]])
            JunctionPatientBottom['Polar'] = JunctionPatientBottom.apply(lambda row: cartesian_to_polar_coordinates(row['x'], row['y'],
                                                                                     AreaJunctionPatientBottom.iloc[0]['Centrex'],
                                                                                     AreaJunctionPatientBottom.iloc[0]['Centrey']) , axis=1)
            JunctionPatientBottom['rpat'] = JunctionPatientBottom.apply(lambda row: row['Polar'][0], axis=1)
            JunctionPatientBottom['tpat'] = JunctionPatientBottom.apply(lambda row: row['Polar'][1], axis=1)
            JunctionPatientBottom = JunctionPatientBottom.drop_duplicates(subset=['tpat'], keep='last')
            X = JunctionPatientBottom['tpat'].to_numpy()
            y = JunctionPatientBottom['rpat'].to_numpy()
            InterpJunctionPatientBottom = interp1d(X, y, fill_value="extrapolate", kind='slinear')

        # -----------------------------------------------------------------------------------------------------------------------------------------------------
        # -----------------------------------------------------------------------------------------------------------------------------------------------------
        # -----------------------------------------------------------------------------------------------------------------------------------------------------
        #Il fait une premier filtre sur le sexe et la position du patient
        #Phantom Selection
        #Sex and Position
        Phantoms_df = All_Phantoms_df[(All_Phantoms_df['Sex'] == patient_sex) &
                                      (All_Phantoms_df['Position'] == patient_position)].reset_index(drop=True)
        Phantoms_df['SizeRatio'] = -1
        # -----------------------------------------------------------------------------------------------------------------------------------------------------
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
        # ------------------------------------------------------
        #Filtre sur le poids : estimé à partir des boites eglobantes au niveau de la junction inf
        #Comparing Phantoms to Patient according to body weigth
        Patient_Body_At_Last_Full_Vertebra = df_contours[(df_contours['ROIName'] == 'body trunc') &
                                                              (df_contours['z'] == \
                                                               df_contours[df_contours['ROIName'].isin(Patient_Full_Vertebrae_List)]['z'].min())]
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
        """
        Donne le possibilité de sécetionner un de ces Phantômes
        """
        Selected_Phantoms_List= ['_HFS_M_ 201709084NS_.txt']
        print('Selected_Phantoms_List: ', len(Selected_Phantoms_List))
        #Fusionne le patient sélectionné et le Fantôme sélectionné
        for sf in Selected_Phantoms_List:
            print('Selected Phantom: ', sf)
            # ---------------------------------------------------------------------------------------------------------------------------------
            start_time = time.time()
            # -----------------------------------------------------------------------------------------------------------------------------------------------------
            df_Phantom_Top = pd.DataFrame()
            df_Phantom_Bottom = pd.DataFrame()
            Phantom_Contours = pd.read_csv(os.path.join(PhantomLib, sf), encoding = "ISO-8859-1", sep='\t',header=0)
            Phantom_Contours = Phantom_Contours[~Phantom_Contours['ROIName'].isin(['body', 'skin'])]
            Phantom_Contours['Origine'] = 'Phantom'
            # -----------------------------------------------------------------------------------------------------------------------------------------------------
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
                AreaJunctionPhantom = calculate_contour_area(JunctionPhantom)
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
                # -----------------------------------------------------------------------------------------------------------------------------------------------------
                #Phantom                       
                Lsmooth = 20
                Phantom_BodyTrunc = Phantom_Contours_Top[Phantom_Contours_Top['ROIName'] == 'body trunc']
                Phantom_BodyTrunc['dz'] = abs(Phantom_BodyTrunc['z'] - JunctionPatientTop.iloc[0]['z'] - Lsmooth)
                dzmin = Phantom_BodyTrunc['dz'].min()
                SmoothJunctionPhantom = Phantom_BodyTrunc[Phantom_BodyTrunc['dz'] == dzmin]
                SmoothJunctionPhantom['Polar']  = SmoothJunctionPhantom.apply(lambda row: cartesian_to_polar_coordinates(row['x'], row['y'],
                                                                                          AreaJunctionPatientTop.iloc[0]['Centrex'],
                                                                                          AreaJunctionPatientTop.iloc[0]['Centrey']) , axis=1)
                SmoothJunctionPhantom['rpat'] = SmoothJunctionPhantom.apply(lambda row: row['Polar'][0], axis=1)
                SmoothJunctionPhantom['tpat'] = SmoothJunctionPhantom.apply(lambda row: row['Polar'][1], axis=1)
                SmoothJunctionPhantom = SmoothJunctionPhantom.drop_duplicates(subset=['tpat'], keep='last')
                X = SmoothJunctionPhantom['tpat'].to_numpy()
                y = SmoothJunctionPhantom['rpat'].to_numpy()
                InterpPhantom = interp1d(X, y, fill_value="extrapolate", kind='slinear')
                # -----------------------------------------------------------------------------------------------------------------------------------------------------
                #Apply interpolations to phantom body
                To_Smooth = Phantom_BodyTrunc[Phantom_BodyTrunc['z'] <= SmoothJunctionPhantom.iloc[0]['z']]
                To_Smooth['Polar'] = To_Smooth.apply(lambda row: cartesian_to_polar_coordinates(row['x'], row['y'],
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
                # -----------------------------------------------------------------------------------------------------------------------------------------------------
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
            # -----------------------------------------------------------------------------------------------------------------------------------------------------
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
                AreaJunctionPhantom = calculate_contour_area(JunctionPhantom)
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
                SmoothJunctionPhantom['Polar']  = SmoothJunctionPhantom.apply(lambda row: cartesian_to_polar_coordinates(row['x'], row['y'],
                                                                                          AreaJunctionPatientBottom.iloc[0]['Centrex'],
                                                                                          AreaJunctionPatientBottom.iloc[0]['Centrey']) , axis=1)
                SmoothJunctionPhantom['rpat'] = SmoothJunctionPhantom.apply(lambda row: row['Polar'][0], axis=1)
                SmoothJunctionPhantom['tpat'] = SmoothJunctionPhantom.apply(lambda row: row['Polar'][1], axis=1)
                SmoothJunctionPhantom = SmoothJunctionPhantom.drop_duplicates(subset=['tpat'], keep='last')
                X = SmoothJunctionPhantom['tpat'].to_numpy()
                y = SmoothJunctionPhantom['rpat'].to_numpy()
                InterpPhantom = interp1d(X, y, fill_value="extrapolate", kind='slinear')
                # -----------------------------------------------------------------------------------------------------------------------------------------------------
                #Apply interpolations to phantom body
                To_Smooth = Phantom_BodyTrunc[Phantom_BodyTrunc['z'] >= SmoothJunctionPhantom.iloc[0]['z']]
                To_Smooth['Polar'] = To_Smooth.apply(lambda row: cartesian_to_polar_coordinates(row['x'], row['y'],
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
                # -----------------------------------------------------------------------------------------------------------------------------------------------------
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
            # -----------------------------------------------------------------------------------------------------------------------------------------------------
            df_Patient_Pantom = pd.concat([df_contours,
                                           df_Phantom_Top,
                                           df_Phantom_Bottom], ignore_index=True)
            df_Patient_Pantom = df_Patient_Pantom[['Origine', 'Section', 'ROIName', 'ROINumber', 'ROIContourNumber', 'ROIContourPointNumber', 'x', 'y', 'z']]
            df_Patient_Pantom = df_Patient_Pantom.dropna()
            df_Patient_Pantom.loc[df_Patient_Pantom['ROIName'].isin(['body trunc', 'body extremities']), 'ROIName'] = 'external'
            # ------------------------------------------------------------------------------------------------------------------------
            ReSampledContours = pd.DataFrame()
            ListSections = sorted(df_Patient_Pantom['Section'].unique().tolist())
            ListROIs = sorted(df_Patient_Pantom['ROIName'].unique().tolist())
            ListPatient_Pantomz = sorted(df_Patient_Pantom['z'].unique().tolist())
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
                            df00 = df0[df0['ROIContourNumber'] == ContourNumb]
                            df00['ROIContourNumber'] = ROIContourNumber
                            df00 = df00.sort_values(by=['ROIContourNumber', 'ROIContourPointNumber', 'x', 'y', 'z'], ascending=([True, True,True,True,True])).reset_index(drop=True)
                            ReSampledContours = pd.concat([ReSampledContours, df00], ignore_index=True)
            # ------------------------------------------------------------------------------------------------------------------------
            Patient_Pantom = 'PP_' + patient + ' ' + sf
            print(os.path.join(dir_project,patient, 'XYZ', Patient_Pantom))
            ReSampledContours.to_csv(os.path.join(dir_project,patient, 'XYZ', Patient_Pantom), sep='\t', encoding='utf-8', index=False)
            print("--- %s seconds ---" % (time.time() - start_time))
            # ---------------------------------------------------------------------------------------------------------------------------------
            # =====================================================================================================================================================



