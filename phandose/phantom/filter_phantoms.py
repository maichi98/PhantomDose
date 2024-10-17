from phandose.patient.patient_contours import is_vertebrae_fully_within_contours
from phandose.phantom.phantom_library import PhantomLibrary
from phandose import constants

import pandas as pd
import numpy as np
import swifter
import cv2


class PhantomFilter:
    """
    Class to filter the phantom library based on the patient's characteristics and the contours.
    It filters the phantom library based on the patient's sex, position, size and weight.

    ...

    Attributes
    ----------
    _df_contours : (pd.DataFrame)
        The DataFrame containing the contours of the patient.

    _df_patient_characteristics : (pd.DataFrame)
        The DataFrame containing the patient's characteristics.

    _phantom_lib : (pd.DataFrame)
        The PhantomLibrary object containing the phantom library.

    _df_phantom_lib : (pd.DataFrame)
        The DataFrame representation of the phantom library.

    _df_full_vertebrae : (pd.DataFrame)
        The DataFrame indicating if each vertebra is fully within the contours.

    _list_full_vertebrae : (list)
        List of contour names of vertebrae that are fully within the contours.

    Methods
    -------
    filter():
        Filters the phantom library based on the patient's characteristics and the contours.
    filter_by_sex_and_position():
        Filters the phantom library based on the patient
    filter_by_size():
        Filters the phantom library based on the patient's size.
    filter_by_weight():
        Filters the phantom library based on the patient's weight.

    """

    def __init__(self,
                 df_contours: pd.DataFrame,
                 df_patient_characteristics: pd.DataFrame):
        """
        Constructor of the PhantomFilter class.

        Parameters
        ----------
            df_contours: pd.DataFrame
                The DataFrame containing the contours of the patient.
                Each row must contain the following columns: ['ROIName', 'z']

            df_patient_characteristics: pd.DataFrame
                The DataFrame containing the patient's characteristics.
                It must contain the following columns : ['PatientSex', 'PatientPosition']

        """

        self._df_contours = df_contours.copy()
        self._df_patient_characteristics = df_patient_characteristics.copy()

        # Create the phantom library :
        self._phantom_lib = PhantomLibrary(constants.DIR_PHANTOM_LIBRARY)
        self._df_phantom_lib = self._phantom_lib.get_phantom_dataframe()

        # Create the full vertebrae dataframe :
        self._df_full_vertebrae = is_vertebrae_fully_within_contours(self._df_contours)
        # list of contour names of vertebrae that are fully within the contours :
        self._list_full_vertebrae = self._df_full_vertebrae.loc[self._df_full_vertebrae["Full"], "ROIName"].tolist()

    def filter(self):
        """
        Filters the phantom library based on the patient's characteristics and the contours.

        Returns
        -------
        list[str]
            The list of the names of the phantoms that passed the filters.

        """

        self.filter_by_sex_and_position()
        self.filter_by_size()
        self.filter_by_weight()

        list_selected_phantoms = self._df_phantom_lib["Phantom"].unique().tolist()
        return list_selected_phantoms

    def filter_by_sex_and_position(self):
        """
        Filters the phantom library based on the patient's sex and position
        """
        try:
            patient_info = self._df_patient_characteristics.loc[
                self._df_patient_characteristics["Type"] == "CT_TO_TOTALSEGMENTATOR"
                ].iloc[0]

            sex, position = patient_info['PatientSex'], patient_info['PatientPosition']

            self._df_phantom_lib = self._df_phantom_lib.loc[
                (self._df_phantom_lib["Sex"] == sex) &
                (self._df_phantom_lib["Position"] == position)
                ]
        except IndexError:
            self._df_phantom_lib = pd.DataFrame(columns=self._df_phantom_lib.columns)

    def filter_by_size(self):
        """
        Filters the phantom library based on the patient's size.
        """

        self._df_phantom_lib["SizeRatio"] = -1

        patient_z_max = self._df_contours.loc[self._df_contours["ROIName"].isin(self._list_full_vertebrae), "z"].max()
        patient_z_min = self._df_contours.loc[self._df_contours["ROIName"].isin(self._list_full_vertebrae), "z"].min()
        patient_size = patient_z_max - patient_z_min

        if patient_size == 0:
            # If the patient size is 0, we can't filter the phantom library based on size :
            self._df_phantom_lib = pd.DataFrame(columns=self._df_phantom_lib.columns)

        else:
            # filter the phantom library based on size :
            list_phantoms = self._df_phantom_lib["Phantom"].unique().tolist()

            list_vertebrae = {
                'vertebrae C1', 'vertebrae C2', 'vertebrae C3', 'vertebrae C4',
                'vertebrae C5', 'vertebrae C6', 'vertebrae C7',
                'vertebrae T1', 'vertebrae T2', 'vertebrae T3', 'vertebrae T4',
                'vertebrae T5', 'vertebrae T6', 'vertebrae T7', 'vertebrae T8',
                'vertebrae T9', 'vertebrae T10', 'vertebrae T11', 'vertebrae T12',
                'vertebrae L1', 'vertebrae L2', 'vertebrae L3', 'vertebrae L4', 'vertebrae L5',
                'vertebrae S1'
            }

            for phantom_name in list_phantoms:

                df_phantom = self._phantom_lib.get_phantom(phantom_name)

                if list_vertebrae.issubset(df_phantom["ROIName"].unique().tolist()):
                    phantom_z_max = df_phantom.loc[df_phantom["ROIName"].isin(self._list_full_vertebrae), "z"].max()
                    phantom_z_min = df_phantom.loc[df_phantom["ROIName"].isin(self._list_full_vertebrae), "z"].min()
                    phantom_size = phantom_z_max - phantom_z_min

                    self._df_phantom_lib.loc[self._df_phantom_lib["Phantom"] == phantom_name, "SizeRatio"] = round(
                        100 * abs(1 - phantom_size / patient_size))

            self._df_phantom_lib = self._df_phantom_lib.loc[
                (self._df_phantom_lib["SizeRatio"] != -1) &
                (self._df_phantom_lib["SizeRatio"] <= 10)
                ]

    def filter_by_weight(self):
        """
        Filters the phantom library based on the patient's weight.
        """

        # Filter the phantom library based on the patient's weight :
        min_full_vertebrae_z = self._df_contours.loc[
            self._df_contours["ROIName"].isin(self._list_full_vertebrae),
            "z"
        ].min()

        df_last_full_vertebrae = self._df_contours.loc[
            (self._df_contours['ROIName'] == 'body trunc') &
            (self._df_contours["z"] == min_full_vertebrae_z)
            ]

        patient_center = df_last_full_vertebrae[["x", "y"]].to_numpy().astype(np.int32)
        patient_xul, patient_yul, patient_wr, patient_hr = cv2.boundingRect(patient_center)

        def is_phantom_not_too_big(phantom_name):

            df_phantom = self._phantom_lib.get_phantom(phantom_name)

            df_phantom_last_full_vertebrae = df_phantom.loc[
                (df_phantom['ROIName'] == 'body trunc') &
                (df_phantom['z'] == df_phantom.loc[df_phantom['ROIName'].isin(self._list_full_vertebrae)]['z'].min())
                ]

            phantom_center = df_phantom_last_full_vertebrae[['x', 'y']].to_numpy().astype(np.int32)
            phantom_xul, phantom_yul, phantom_wr, phantom_hr = cv2.boundingRect(phantom_center)

            return patient_wr >= (phantom_wr - 25) and patient_hr >= (phantom_hr - 25)

        self._df_phantom_lib[
            "Thinner"] = self._df_phantom_lib["Phantom"].swifter.progress_bar(False).apply(is_phantom_not_too_big)

        self._df_phantom_lib = self._df_phantom_lib.loc[self._df_phantom_lib["Thinner"]]

    @property
    def df_phantom_lib(self):
        return self._df_phantom_lib
