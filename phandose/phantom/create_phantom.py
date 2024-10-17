from phandose.patient.patient_contours import get_contours_barycenters
from phandose.phantom.phantom_utils import calculate_contour_area, cartesian_to_polar_coordinates

from scipy.interpolate import interp1d
from pathlib import Path
import pandas as pd
import numpy as np
import cv2


class TopExtensionBuilder:
    pass


class BottomExtensionBuilder:

    def __init__(self,
                 df_contours: pd.DataFrame,
                 df_barycenter: pd.DataFrame):

        self._df_contours = df_contours
        self._df_barycenter = df_barycenter

        self._bottom_vertebra = None
        self._df_bottom_extension = None
        self._df_bottom_extension_area = None
        self._interp_bottom_extension = None
        self._bottom_rectangle = None

    def build_bottom_vertebra(self):

        bottom_vertebra_z = self._df_barycenter["Barz"].min()

        bottom_vertebra_x = self._df_barycenter.loc[self._df_barycenter["Barz"] == bottom_vertebra_z, "Barx"].values[0]
        bottom_vertebra_y = self._df_barycenter.loc[self._df_barycenter["Barz"] == bottom_vertebra_z, "Bary"].values[0]

        self._bottom_vertebra = {"Barx": bottom_vertebra_x,
                                 "Bary": bottom_vertebra_y,
                                 "Barz": bottom_vertebra_z}

    def build_bottom_extension(self):

        df_bottom_extension = self._df_contours.loc[self._df_contours["ROIName"] == "body trunc"].copy()
        df_bottom_extension["Ecart"] = abs(df_bottom_extension["z"] - self._bottom_vertebra["Barz"])

        ecart_min = df_bottom_extension["Ecart"].min()
        self._df_bottom_extension = df_bottom_extension.loc[df_bottom_extension["Ecart"] == ecart_min]

        self._df_bottom_extension_area = calculate_contour_area(self._df_bottom_extension)
        self._df_bottom_extension_area["Centrality"] = abs(df_bottom_extension["Centrex"])

        center_min = self._df_bottom_extension_area["Centrality"].min()
        contour_num = self._df_bottom_extension_area.loc[self._df_bottom_extension_area["Centrality"] == center_min,
                                                         "ROIContourNumber"].values[0]

        self._df_bottom_extension = df_bottom_extension.loc[df_bottom_extension["ROIContourNumber"] == contour_num]

        get_polar = lambda row: cartesian_to_polar_coordinates(row["x"],
                                                               row["y"],
                                                               self._df_bottom_extension_area.iloc[0]["Centrex"],
                                                               self._df_bottom_extension_area.iloc[0]["Centrey"])

        self._df_bottom_extension["Polar"] = self._df_bottom_extension.apply(get_polar, axis=1)

        self._df_bottom_extension["rpat"] = self._df_bottom_extension.apply(lambda row: row['Polar'][0], axis=1)
        self._df_bottom_extension["tpat"] = self._df_bottom_extension.apply(lambda row: row['Polar'][0], axis=1)

    def build_bottom_rectangle(self):

        center = self._df_bottom_extension[["x", "y"]].to_numpy()
        center = np.array([center]).astype(np.int32)

        xul, yul, wr, hr = cv2.boundingRect(center)

        self._bottom_rectangle = np.array([[xul, yul],
                                           [xul, yul + hr],
                                           [xul + wr, yul + hr],
                                           [xul + wr, yul]])

    def build_interp_bottom_extension(self):

        x, y = self._df_bottom_extension["x"].to_numpy(), self._df_bottom_extension["y"].to_numpy()
        self._interp_bottom_extension = interp1d(x, y, fill_value='extrapolate', kind='slinear')

    def extend(self):

        self.build_bottom_vertebra()
        self.build_bottom_extension()
        self.build_bottom_rectangle()
        self.build_interp_bottom_extension()


class PhantomExtensionDirector:

    def __init__(self,
                 path_phantom: Path,
                 df_contours: pd.DataFrame,
                 df_barycenter: pd.DataFrame = None):

        self._path_phantom = path_phantom
        self._df_phantom = None

        self._df_contours = df_contours
        self._df_barycenter = df_barycenter

    @property
    def df_phantom(self):
        if self._df_phantom is None:
            self._df_phantom = pd.read_csv(self._path_phantom, sep="\t", encoding="ISO-8859-1")

        return self._df_phantom

    @property
    def df_contours(self):
        return self._df_contours

    @property
    def df_barycenter(self):
        if self._df_barycenter is None:
            self._df_barycenter = get_contours_barycenters(self._df_contours)

        return self._df_barycenter

    def is_top_extension_warranted(self):

        raise NotImplementedError("This method must be implemented in the subclass.")

    def is_bottom_extension_warranted(self):

        return not {'femur left', 'femur right'}.issubset(self.df_contours["ROIName"].unique())

    def extend_top_only(self):
        pass

    def extend_bottom_only(self):
        pass

    def extend_top_and_bottom(self):
        pass
