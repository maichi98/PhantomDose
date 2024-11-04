from phandose.patient.patient_contours import get_contours_barycenters

import pandas as pd


class ScanExtensionDirector:

    def __init__(self,
                 path_phantom,
                 df_contours,
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
