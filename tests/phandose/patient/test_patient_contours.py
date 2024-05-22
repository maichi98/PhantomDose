from phandose.patient import get_contours_barycenters

import pandas as pd
import numpy as np
import unittest


class TestPatientContours(unittest.TestCase):

    def setUp(self):

        self.df_valid_contours = pd.DataFrame({'ROIName': ['ROI1', 'ROI1', 'ROI2', 'ROI2'],
                                               'ROINumber': [1, 1, 2, 2],
                                               'ROIContourNumber': [1, 1, 1, 1],
                                               'ROIContourPointNumber': [1, 2, 1, 2],
                                               'x': [1, 2, 3, 4],
                                               'y': [4, 5, 3, 4],
                                               'z': [0, 2, 5, 4]})

        self.df_empty_contours = pd.DataFrame(columns=self.df_valid_contours.columns)

        self.df_invalid_contours = self.df_valid_contours.copy()
        self.df_invalid_contours.loc[0, 'x'] = np.nan

    def test_get_contours_barycenters_with_valid_contours_dataframe(self):

        df_result_barycenters = get_contours_barycenters(self.df_valid_contours)

        self.assertEqual(df_result_barycenters.shape, (2, 5))
        self.assertEqual(df_result_barycenters.columns.tolist(), ['Organ', 'Rts', 'Barx', 'Bary', 'Barz'])
        self.assertEqual(df_result_barycenters['Organ'].tolist(), ['ROI1', 'ROI2'])
        self.assertEqual(df_result_barycenters['Rts'].tolist(), ['Patient_Contours', 'Patient_Contours'])
        self.assertEqual(df_result_barycenters['Barx'].tolist(), [1.5, 3.5])
        self.assertEqual(df_result_barycenters['Bary'].tolist(), [4.5, 3.5])
        self.assertEqual(df_result_barycenters['Barz'].tolist(), [1, 4.5])

    def test_get_contours_barycenters_with_empty_contours_dataframe(self):

        df_result_barycenters = get_contours_barycenters(self.df_empty_contours)

        self.assertEqual(df_result_barycenters.shape, (0, 5))
        self.assertEqual(df_result_barycenters.columns.tolist(), ['Organ', 'Rts', 'Barx', 'Bary', 'Barz'])
        self.assertTrue(df_result_barycenters.empty)

    def test_get_contours_barycenters_with_invalid_contours_dataframe(self):

        with self.assertRaises(ValueError):
            df_result_barycenters = get_contours_barycenters(self.df_invalid_contours)


class TestIsVertebraeFullyWithinContours(unittest.TestCase):

    pass


if __name__ == '__main__':
    unittest.main()
