from phandose.patient import convert_nifti_segmentation_directory_to_contours_dataframe, get_patient_characteristics
from phandose.phantom.filter_phantoms import PhantomFilter

from pandas.testing import assert_frame_equal
from unittest.mock import patch
from pathlib import Path
import pandas as pd
import numpy as np
import unittest


class TestFilterBySexAndPosition(unittest.TestCase):

    @patch('phandose.phantom.filter_phantoms.PhantomLibrary')
    def setUp(self, mock_phantom_library):

        mock_df_phantom_lib = pd.DataFrame({
            "Phantom": ["phantom1", "phantom2", "phantom3", "phantom4", "phantom5"],
            "Sex": ["M", "M", "F", "F", "M"],
            "Position": ["HFS", "FFS", "HFS", "FFS", "HFS"]})

        mock_phantom_library.return_value.get_phantom_dataframe.return_value = mock_df_phantom_lib

        # directory to test patient AGORL_P33 (PatientSex = M, PatientPosition = HFS) :
        dir_patient = Path(__file__).resolve().parents[3] / 'sample_data' / 'AGORL_P33'

        dir_ct, dir_petct = dir_patient / 'CT_TO_TOTALSEGMENTATOR', dir_patient / 'PET_TO_TOTALSEGMENTATOR'
        self.df_patient_characteristics = get_patient_characteristics(dir_ct, dir_petct)

        dir_segmentations = dir_patient / "NIFTI_FROM_CT"
        self.df_contours = convert_nifti_segmentation_directory_to_contours_dataframe(dir_segmentations)

        self.phantom_filter = PhantomFilter(self.df_contours, self.df_patient_characteristics)

    def test_filter_by_sex_and_position_for_patient_agorl_p33(self):

        self.phantom_filter.filter_by_sex_and_position()

        df_expected = pd.DataFrame({
            "Phantom": ["phantom1", "phantom5"],
            "Sex": ["M", "M"],
            "Position": ["HFS", "HFS"]}, index=[0, 4])

        assert_frame_equal(self.phantom_filter.df_phantom_lib, df_expected)

    def test_filter_by_sex_and_position_for_patient_with_no_matching_sex(self):

        df_patient_characteristics = self.df_patient_characteristics.copy()
        df_patient_characteristics["PatientSex"] = "X"

        phantom_filter = PhantomFilter(self.df_contours, df_patient_characteristics)
        phantom_filter.filter_by_sex_and_position()

        assert_frame_equal(phantom_filter.df_phantom_lib, pd.DataFrame(columns=["Phantom", "Position", "Sex"]))

    def test_filter_by_sex_and_position_for_patient_with_no_matching_position(self):

        df_patient_characteristics = self.df_patient_characteristics.copy()
        df_patient_characteristics["PatientPosition"] = "HFDS"

        phantom_filter = PhantomFilter(self.df_contours, df_patient_characteristics)
        phantom_filter.filter_by_sex_and_position()

        assert_frame_equal(phantom_filter.df_phantom_lib, pd.DataFrame(columns=["Phantom", "Position", "Sex"]))

    def test_filter_by_sex_and_position_for_patient_with_no_sex_information(self):

        df_patient_characteristics = self.df_patient_characteristics.copy()
        df_patient_characteristics["PatientSex"] = np.nan

        phantom_filter = PhantomFilter(self.df_contours, df_patient_characteristics)
        phantom_filter.filter_by_sex_and_position()

        assert_frame_equal(phantom_filter.df_phantom_lib, pd.DataFrame(columns=["Phantom", "Position", "Sex"]))

    def test_filter_by_sex_and_position_for_patient_with_no_position_information(self):

        df_patient_characteristics = self.df_patient_characteristics.copy()
        df_patient_characteristics["PatientPosition"] = np.nan

        phantom_filter = PhantomFilter(self.df_contours, df_patient_characteristics)
        phantom_filter.filter_by_sex_and_position()

        assert_frame_equal(phantom_filter.df_phantom_lib, pd.DataFrame(columns=["Phantom", "Position", "Sex"]))


if __name__ == '__main__':
    unittest.main()
