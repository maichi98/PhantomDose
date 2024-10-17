from phandose.patient import get_patient_characteristics

from unittest.mock import patch, MagicMock
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
import unittest


class TestGetPatientCharacteristics(unittest.TestCase):

    def setUp(self):
        # Define the path to the imaging data :
        self.dir_sample_patient_data = Path(__file__).parent.parent.parent / 'sample_data' / "AGORL_P33"
        self.dir_ct = self.dir_sample_patient_data / "CT_TO_TOTALSEGMENTATOR"
        self.dir_petct = self.dir_sample_patient_data / "PET_TO_TOTALSEGMENTATOR"

    def test_get_patient_characteristics_for_patient_agorl_p33(self):

        # Call the function get_patient_characteristics :
        df_patient_data = get_patient_characteristics(self.dir_ct, self.dir_petct)

        # Expected DataFrame :
        df_expected = pd.DataFrame({
            'Folder': [str(self.dir_ct), str(self.dir_petct)],
            'Type': ['CT_TO_TOTALSEGMENTATOR', 'PET_TO_TOTALSEGMENTATOR'],
            'PatientID': ['AGORL_P33', 'AGORL_P33'],
            'CodeMeaning': ['TDM RT ORL', 'TIM PET'],
            'AcquisitionDate': [datetime(2020, 3, 6), datetime(2020, 2, 17)],
            'DataCollectionDiameter': [500.0, 500.0],
            'ReconstructionDiameter': [500.0, 500.0],
            'PatientPosition': ['HFS', 'HFS'],
            'PatientBirthDate': [datetime(2023, 1, 1), datetime(2023, 1, 1)],
            'PatientSex': ['M', 'M'],
            'PatientSize': [np.nan, 1.8],
            'PatientWeight': [np.nan, np.nan]
            })

        # Check that the returned DataFrame is correct :
        pd.testing.assert_frame_equal(df_patient_data, df_expected)

    def test_get_patient_characteristics_with_invalid_path(self):
        with self.assertRaises(FileNotFoundError):
            get_patient_characteristics(Path('invalid_path'))

    @patch('phandose.patient.patient_characteristics.dcm.misc.is_dicom')
    def test_get_patient_characteristics_with_non_dicom_files(self, mock_is_dicom):
        mock_is_dicom.return_value = False
        with self.assertRaises(ValueError):
            get_patient_characteristics(self.dir_ct)

    @patch('phandose.patient.patient_characteristics.dcm.dcmread')
    def test_get_patient_characteristics_with_non_ct_modality(self, mock_dcmread):
        mock_dcmread.return_value = MagicMock(Modality='MR')
        with self.assertRaises(ValueError):
            get_patient_characteristics(self.dir_ct)


if __name__ == '__main__':
    unittest.main()
