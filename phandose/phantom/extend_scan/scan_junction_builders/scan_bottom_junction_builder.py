from phandose.phantom.phantom_utils import calculate_contour_area, cartesian_to_polar_coordinates
from phandose.phantom.extend_scan.scan_junction import ScanJunction
from scan_junction_builder import ScanJunctionBuilder

from scipy.interpolate import interp1d
import numpy as np
import cv2


class ScanBottomJunctionBuilder(ScanJunctionBuilder):

    def __init__(self,
                 df_contours,
                 df_barycenter):

        super().__init__(df_contours, df_barycenter)

        self._junction = ScanJunction()

    def find_bottom_vertebra(self):

        z = self.df_barycenter["Barz"].min()

        x = self.df_barycenter.loc[self.df_barycenter["Barz"] == z, "Barx"].values[0]
        y = self.df_barycenter.loc[self.df_barycenter["Barz"] == z, "Bary"].values[0]
        organ = self.df_barycenter.loc[self.df_barycenter["Barz"] == z, "Organ"].values[0]

        self._junction.set_vertebra(organ, x, y, z)

    def build_bottom_junction(self):

        df_junction = self.df_contours.loc[self.df_contours["ROIName"] == "body trunc"].copy()
        df_junction["Ecart"] = abs(df_junction["z"] - self._junction.vertebra["Barz"])

        ecart_min = df_junction["Ecart"].min()
        df_junction = df_junction.loc[df_junction["Ecart"] == ecart_min]











        df_junction = self.df_contours.loc[self.df_contours["ROIName"] == "body trunc"].copy()



        df_bottom_junction = self.df_contours.loc[self.df_contours["ROIName"] == "body trunc"].copy()
        df_bottom_junction["Ecart"] = abs(df_bottom_junction["z"] - self._bottom_junction_vertebra["Barz"])

        ecart_min = df_bottom_junction["Ecart"].min()
        self._df_bottom_junction = df_bottom_junction.loc[df_bottom_junction["Ecart"] == ecart_min]

        self._df_bottom_junction_area = calculate_contour_area(self._df_bottom_junction)
        self._df_bottom_junction_area["Centrality"] = abs(df_bottom_junction["Centrex"])

        center_min = self._df_bottom_junction_area["Centrality"].min()
        contour_num = self._df_bottom_junction_area.loc[self._df_bottom_junction_area["Centrality"] == center_min,
                                                        "ROIContourNumber"].values[0]

        self._df_bottom_junction = df_bottom_junction.loc[df_bottom_junction["ROIContourNumber"] == contour_num]

        get_polar = lambda row: cartesian_to_polar_coordinates(row["x"],
                                                               row["y"],
                                                               self._df_bottom_junction_area.iloc[0]["Centrex"],
                                                               self._df_bottom_junction_area.iloc[0]["Centrey"])

        self._df_bottom_junction["Polar"] = self._df_bottom_junction.apply(get_polar, axis=1)

        self._df_bottom_junction["rpat"] = self._df_bottom_junction.apply(lambda row: row['Polar'][0], axis=1)
        self._df_bottom_junction["tpat"] = self._df_bottom_junction.apply(lambda row: row['Polar'][0], axis=1)

    def build_bottom_rectangle(self):

        center = self._df_bottom_junction[["x", "y"]].to_numpy()
        center = center.mean(axis=0)

        xul, yul, wr, hr = cv2.boundingRect(center)

        self._bottom_rectangle = np.array([[xul, yul],
                                           [xul, yul + hr],
                                           [xul + wr, yul + hr],
                                           [xul + wr, yul]])

    def build_interp_bottom_junction(self):

        x, y = self._df_bottom_junction["x"].to_numpy(), self._df_bottom_junction["y"].to_numpy()
        self._interp_bottom_junction = interp1d(x, y, fill_value='extrapolate', kind='slinear')

    def build(self):

        self.build_bottom_junction_vertebra()
        self.build_bottom_junction()
        self.build_bottom_rectangle()
        self.build_interp_bottom_junction()

        return ScanJunction(junction_vertebra=self._bottom_junction_vertebra,
                            df_junction=self._df_bottom_junction,
                            df_junction_area=self._df_bottom_junction_area,
                            interp_junction=self._interp_bottom_junction,
                            rectangle=self._bottom_rectangle)
