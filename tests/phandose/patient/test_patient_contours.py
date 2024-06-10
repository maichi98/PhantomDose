from phandose.patient import is_vertebrae_fully_within_contours
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

    def setUp(self):

        cols = ["ROIName", "ROINumber", "ROIContourNumber", "ROIContourPointNumber", "x", "y", "z"]

        # initialize the list of organ contours dataframes :
        list_df_contours = []

        # Create a Dummy head contours dataframe :
        df_head_contours = pd.DataFrame(columns=cols)

        # Dummy head will be a sphere with radius 1 and centered at (0, 0, 5), with 1000 points :
        num_points, radius_head = 1000, 1
        # Generate 1000 points on the surface of a sphere by using spherical coordinates :
        theta = 2 * np.pi * np.random.randint(0, 101, num_points) / 100
        phi = np.arccos(2 * np.random.randint(0, 101, num_points) / 100 - 1)

        df_head_contours["x"] = radius_head * np.sin(phi) * np.cos(theta)
        df_head_contours["y"] = radius_head * np.sin(phi) * np.sin(theta)
        df_head_contours["z"] = (radius_head * np.cos(phi)) + 5

        # Sort the contours by z, then x, then y :
        df_head_contours = df_head_contours.sort_values(by=['z', 'x', 'y']).reset_index(drop=True)
        # Add additional information about the ROI :
        df_head_contours['ROIName'] = 'Head'
        df_head_contours['ROINumber'] = 1
        df_head_contours['ROIContourNumber'] = df_head_contours.groupby('z').ngroup() + 1
        df_head_contours['ROIContourPointNumber'] = df_head_contours.groupby('z').cumcount() + 1

        # Add the head contours to the list of organ contours dataframes :
        list_df_contours.append(df_head_contours)

        # Create 2 dummy vertebrae contours dataframes :
        dict_vertebrae = {"vertebrae1": (0, 0, 3), "vertebrae2": (0, 0, 2)}

        for vertebrae, center in dict_vertebrae.items():

            df_vertebrae_contours = pd.DataFrame(columns=cols)

            # Dummy vertebrae will be a ring with radius 5, of thickness 0.1 and centered at (0, 0, 3) and (0, 0, 2) :
            num_points, radius_vertebrae, thickness_vertebrae = 1000, 5, 0.1
            # Generate 1000 points on the surface of a ring by using cylindrical coordinates :
            theta = 2 * np.pi * np.random.rand(num_points)
            z = ((np.random.randint(-10, 11, num_points) / 20) * thickness_vertebrae) + center[2]

            df_vertebrae_contours["x"] = radius_vertebrae * np.cos(theta)
            df_vertebrae_contours["y"] = radius_vertebrae * np.sin(theta)
            df_vertebrae_contours["z"] = z

            # Sort the contours by z, then x, then y :
            df_vertebrae_contours = df_vertebrae_contours.sort_values(by=['z', 'x', 'y']).reset_index(drop=True)
            # Add additional information about the ROI :
            df_vertebrae_contours['ROIName'] = vertebrae
            df_vertebrae_contours['ROINumber'] = 1
            df_vertebrae_contours['ROIContourNumber'] = df_vertebrae_contours.groupby('z').ngroup() + 1
            df_vertebrae_contours['ROIContourPointNumber'] = df_vertebrae_contours.groupby('z').cumcount() + 1
            # Add the vertebrae contours to the list of organ contours dataframes :
            list_df_contours.append(df_vertebrae_contours)

        # Concatenate all the organ contours dataframes :
        self.df_valid_contours = pd.concat(list_df_contours, ignore_index=True)
        # drop any duplicate rows :
        self.df_valid_contours = self.df_valid_contours.drop_duplicates().reset_index(drop=True)

        self.df_empty_contours = pd.DataFrame(columns=self.df_valid_contours.columns)

    def test_is_vertebrae_fully_within_contours_with_valid_contours(self):

        df_result_full_vertebrae = is_vertebrae_fully_within_contours(self.df_valid_contours)

        self.assertEqual(df_result_full_vertebrae.shape, (2, 2))
        self.assertEqual(df_result_full_vertebrae.columns.tolist(), ['ROIName', 'Full'])
        self.assertEqual(df_result_full_vertebrae['ROIName'].tolist(), ['vertebrae1', 'vertebrae2'])
        self.assertEqual(df_result_full_vertebrae['Full'].tolist(), [True, False])

    def test_is_vertebrae_fully_within_contours_with_empty_contours(self):

        df_result_full_vertebrae = is_vertebrae_fully_within_contours(self.df_empty_contours)
        print(df_result_full_vertebrae)
        self.assertEqual(df_result_full_vertebrae.shape, (0, 2))
        self.assertEqual(df_result_full_vertebrae.columns.tolist(), ['ROIName', 'Full'])
        self.assertTrue(df_result_full_vertebrae.empty)

    def test_is_vertebrae_fully_within_contours_with_invalid_contours(self):

        df_invalid_contours = self.df_valid_contours.copy()
        df_invalid_contours.loc[0, 'z'] = np.nan

        with self.assertRaises(ValueError):
            df_result_full_vertebrae = is_vertebrae_fully_within_contours(df_invalid_contours)


if __name__ == '__main__':
    unittest.main()
