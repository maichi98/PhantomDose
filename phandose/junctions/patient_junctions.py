import pandas as pd
import numpy as np


class JunctionHandler:

    def __init__(self, df_contours: pd.DataFrame, df_barycenter: pd.DataFrame):

        """
        Constructor of the class JunctionTemplate.

        Parameters:
        -----------
        df_contours : (pd.DataFrame)
            DataFrame containing the contours of the junction.

        df_barycenter : (pd.DataFrame)
            DataFrame containing the barycenter of the junction.
        """

        self._df_contours = df_contours
        self._df_barycenter = df_barycenter

    def get_mean_organ_spacing_z(self):
        """
        Get the mean spacing between two consecutive organs along the z-axis.

        Returns
        -------
        float
            The average spacing between two consecutive organs along the z-axis.
        """

        # Get along the z-axis the mean distance between two consecutive organs :
        list_organ_z = sorted(self._df_barycenter["Barz"].unique().tolist())
        list_spacing_z = np.diff(list_organ_z)

        return list_spacing_z.mean()

    def is_top_junction(self):
        """
        Check if the junction is the top junction of the phantom.

        Returns
        -------
        bool
            True if the junction is the top junction of the phantom, False otherwise.
        """

        # If the skull is present in the contours, the junction is the top junction if the skull is the highest organ :
        if "skull" in self._df_contours["ROIName"].unique():

            skull_z_max = self._df_contours.loc[self._df_contours["ROIName"] == "skull", "z"].max()
            return skull_z_max == self._df_contours["z"].max()

        return True

    def is_bottom_junction(self):
        """
        Check if the junction is the bottom junction of the phantom.

        Returns
        -------
        bool
            True if the junction is the bottom junction of the phantom, False otherwise.
        """

        return not {'femur left', 'femur right'}.issubset(self._df_contours["ROIName"].unique())

    def get_top_vertebra(self):
        """
        Get the top vertebra of the phantom.

        Returns
        -------
        tuple
            The coordinates of the top vertebra of the phantom.
        """

        if "skull" in self._df_contours["ROIName"].unique():
            skull_z_min = self._df_contours.loc[self._df_contours["ROIName"] == "skull", "z"].min()

            threshold_vertebra_z = skull_z_min - 3 * self.get_mean_organ_spacing_z()
            top_vertebra_z = self._df_barycenter.loc[self._df_barycenter["Barz"] < threshold_vertebra_z, "Barz"].max()
        else:
            top_vertebra_z = self._df_barycenter["Barz"].max()

        top_vertebra_x = self._df_barycenter.loc[self._df_barycenter["Barz"] == top_vertebra_z, "Barx"].values[0]
        top_vertebra_y = self._df_barycenter.loc[self._df_barycenter["Barz"] == top_vertebra_z, "Bary"].values[0]

        return top_vertebra_x, top_vertebra_y, top_vertebra_z

    def get_bottom_vertebra(self):
        """
        Get the bottom vertebra of the phantom.

        Returns
        -------
        str
            The name of the bottom vertebra of the phantom.
        """

        bottom_vertebra_z = self._df_barycenter["Barz"].min()
        bottom_vertebra_x = self._df_barycenter.loc[self._df_barycenter["Barz"] == bottom_vertebra_z, "Barx"].values[0]
        bottom_vertebra_y = self._df_barycenter.loc[self._df_barycenter["Barz"] == bottom_vertebra_z, "Bary"].values[0]

        return bottom_vertebra_x, bottom_vertebra_y, bottom_vertebra_z

    def get_top_junction_dataframe(self):
        pass

    def get_bottom_junction_dataframe(self):
        pass

    def get_top_rectangle(self):
        pass

    def get_bottom_rectangle(self):
        pass

    def get_area_top_junction(self):
        pass

    def get_area_bottom_junction(self):
        pass

    def get_interp_top_junction(self):
        pass

    def get_interp_bottom_junction(self):
        pass
