from datetime import datetime
from pathlib import Path
import pydicom as dcm
import pandas as pd
import numpy as np


def get_patient_characteristics(*list_path_imaging: Path | str) -> pd.DataFrame:

    """
    Extract patient characteristics from imaging data (CT or PETCT) stored in specified paths.

    Parameters
    ----------
    list_path_imaging: (Path | str)
         Variable number of paths to imaging Data. (e.g. CT or PETCT)

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the patient characteristics extracted from the specified paths
        The DataFrame contains the following columns:
        'Folder', (str) : The directory path of the imaging data
        'Type', (str) : The type of imaging data (e.g. CT or PETCT)
        'PatientID' (str) : The ID of the patient
        'CodeMeaning', (str) : code meaning of procedure code sequence
        'AcquisitionDate' (datetime64[ns]) : the date of the acquisition of the data that resulted in the image
        'DataCollectionDiameter' (float) : the diameter in mm of the region over which data were collected
        'ReconstructionDiameter' (float) : the diameter (mm) of the region from within which
                                           data were used for reconstruction
        'PatientPosition' (str) : patient position descriptor relative to the equipment
        'PatientBirthDate' (datetime64[ns]) : birthdate of the patient
        'PatientSex' (str) : sex of the patient
        'PatientSize' (float) : length or size of the patient in meters
        'PatientWeight' (float) : weight of the patient in kilograms

    Raises
    ------
    FileNotFoundError
        If the path to the imaging data does not exist

    ValueError
        If the first slice is not a DICOM file, or its slice is not CT.

    """

    # dictionary of the patient_characteristics DataFrame columns with their respective data types :
    dict_columns = {
        'Folder': str,
        'Type': str,
        'PatientID': str,
        'CodeMeaning': str,
        'AcquisitionDate': 'datetime64[ns]',
        'DataCollectionDiameter': float,
        'ReconstructionDiameter': float,
        'PatientPosition': str,
        'PatientBirthDate': 'datetime64[ns]',
        'PatientSex': str,
        'PatientSize': float,
        'PatientWeight': float
    }
    list_columns = list(dict_columns.keys())

    # List of attributes to extract from the DICOM file :
    list_attributes = ['PatientID',
                       'ProcedureCodeSequence',
                       'AcquisitionDate',
                       'DataCollectionDiameter',
                       'ReconstructionDiameter',
                       'PatientPosition',
                       'PatientBirthDate',
                       'PatientSex',
                       'PatientSize',
                       "PatientWeight"]

    df_patient_data = pd.DataFrame(columns=list_columns).astype(dict_columns)
    for path_imaging in list_path_imaging:

        path_imaging = Path(path_imaging)

        if not path_imaging.exists():
            raise FileNotFoundError(f"The path {path_imaging} does not exist !")

        # Get patients characteristics from the first slice :
        first_slice = next(path_imaging.glob("*.dcm"))

        # Check that the first slice is a dicom file:
        if not dcm.misc.is_dicom(first_slice):
            raise ValueError(f"The slice {first_slice} is not a DICOM file !")

        dcm_slice = dcm.dcmread(first_slice)

        # Extract patients characteristics only if slice modality is CT:
        if dcm_slice.Modality != "CT":
            raise ValueError(f"The modality of the slice {first_slice} is not CT !")

        dict_patient_data = {"Folder": str(path_imaging), "Type": path_imaging.stem}

        # Loop over the list of attributes to extract from the DICOM file :
        for attr in list_attributes:

            value = dcm_slice.get(attr, np.nan)

            if attr == 'ProcedureCodeSequence':
                value = value[0].CodeMeaning if not pd.isna(value) else np.nan
                dict_patient_data['CodeMeaning'] = value

            elif attr in ['AcquisitionDate', 'PatientBirthDate']:
                value = datetime.strptime(value, "%Y%m%d") if not pd.isna(value) else np.nan
                dict_patient_data[attr] = value

            else:
                dict_patient_data[attr] = value

        # append the patient data to the DataFrame :
        df_patient_data.loc[len(df_patient_data)] = dict_patient_data

    return df_patient_data.astype(dict_columns)
