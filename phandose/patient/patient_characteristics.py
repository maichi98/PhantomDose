from pathlib import Path
import pydicom as dcm
import pandas as pd


def get_patient_characteristics(*list_path_imaging: Path | str) -> pd.DataFrame:
    """
    Extract patient characteristics from imaging data (CT or PETCT) stored in specified paths.

    :param list_path_imaging: *(Union[Path, str]) Variable number of paths to imaging Data. (e.g. CT or PETCT)
    :return: pd.DataFrame, A DataFrame containing the patient characteristics extracted from the specified paths

    """

    cols = ['Folder',
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
            'PatientWeight']

    df_patient_data = pd.DataFrame(columns=cols)

    for path_imaging in list_path_imaging:

        path_imaging = Path(path_imaging)
        # Get patients characteristics from the first slice :
        first_slice = next(path_imaging.glob("*.dcm"))
        # Check that the first slice is a dicom file:
        if dcm.misc.is_dicom(first_slice):
            dcm_slice = dcm.dcmread(first_slice)
            # Extract patients characteristics only if slice modality is CT:
            if dcm_slice.Modality == "CT":
                # ID of the patient :
                patient_id = dcm_slice.get("PatientID", "nan")

                # code meaning of procedure code sequence :
                code_meaning = dcm_slice.get("ProcedureCodeSequence", None)
                code_meaning = code_meaning[0].CodeMeaning if code_meaning else 'nan'

                # length or size of the patient in meters :
                patient_size = dcm_slice.get("PatientSize", "nan")

                # weight of the patient in kilograms :
                patient_weight = dcm_slice.get("PatientWeight", "nan")

                # the date of the acquisition of the data that resulted in the image :
                acquisition_date = dcm_slice.get("AcquisitionDate", "nan")

                # the diameter in mm of the region over which data were collected :
                data_collection_diameter = dcm_slice.get("DataCollectionDiameter", "nan")

                # the diameter in mm of the region from within which data were used
                # in creating the reconstruction of the image :
                reconstruction_diameter = dcm_slice.get("ReconstructionDiameter", "nan")

                # patient position descriptor relative to the equipment :
                patient_position = dcm_slice.get("PatientPosition", "nan")

                # birthdate of the patient :
                patient_birthdate = dcm_slice.get("PatientBirthDate", "nan")

                # sex of the patient :
                patient_sex = dcm_slice.get("PatientSex", "nan")

                patient_data = {
                    "Folder": [str(path_imaging)],
                    "Type": [path_imaging.stem],
                    "PatientID": [patient_id],
                    "CodeMeaning": [code_meaning],
                    "AcquisitionDate": [acquisition_date],
                    "DataCollectionDiameter": [data_collection_diameter],
                    "ReconstructionDiameter": [reconstruction_diameter],
                    "PatientPosition": [patient_position],
                    "PatientBirthDate": [patient_birthdate],
                    "PatientSex": [patient_sex],
                    "PatientSize": [patient_size],
                    "PatientWeight": [patient_weight]
                }

                _df = pd.DataFrame(patient_data)
                df_patient_data = _df if df_patient_data.empty else pd.concat([df_patient_data, _df], ignore_index=True)

    return df_patient_data
