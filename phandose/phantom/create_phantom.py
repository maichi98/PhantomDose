from phandose.patient.patient_contours import is_top_extension_warranted, is_bottom_extension_warranted
from phandose.patient.patient_contours import get_contours_barycenters

import pandas as pd


class PhantomExtensionBuilderV1:

    def __init__(self,
                 path_phantom: str,
                 df_contours: pd.DataFrame,
                 df_patient_characteristics: pd.DataFrame,
                 **kwargs):

        self._path_phantom = path_phantom
        self._df_phantom = None

        self._df_contours = df_contours
        self._df_barycenter = kwargs.get("df_barycenter", None)

        self._is_top_extension_warranted = None
        self._is_bottom_extension_warranted = None

        self._df_top_extension = None
        self._df_bottom_extension = None

        self._df_top_extension_area = None
        self._df_bottom_extension_area = None

        self._top_extension_vertebra = None
        self._bottom_extension_vertebra = None

        self._top_vertebra = None
        self._bottom_vertebra = None

        self._top_extension_rectangle = None
        self._bottom_extension_rectangle = None

        self._interp_top_extension = None
        self._interp_bottom_extension = None

    @property
    def df_barycenter(self):
        if self._df_barycenter is None:
            self._df_barycenter = get_contours_barycenters(self._df_contours)

        return self._df_barycenter

    @property
    def df_phantom(self):

        if self._df_phantom is None:

            self._df_phantom = pd.read_csv(self._path_phantom, encoding="ISO-8859-1", sep="\t", header=0)
            self._df_phantom = self._df_phantom[~self._df_phantom["ROIName"].isin(["skin", "body"])]
            self._df_phantom["Origine"] = "Phantom"

        return self._df_phantom

    def is_top_extension_warranted(self):
        if self._is_top_extension_warranted is None:
            self._is_top_extension_warranted = is_top_extension_warranted(self._df_contours)

        return self._is_top_extension_warranted

    def is_bottom_extension_warranted(self):
        if self._is_bottom_extension_warranted is None:
            self._is_bottom_extension_warranted = is_bottom_extension_warranted(self._df_contours)

        return self._is_bottom_extension_warranted

    def build_top_extension(self):

        list_organ_z = sorted()



class PhantomExtensionBuilderV2:

    def __init__(self,
                 path_phantom: str,
                 df_contours: pd.DataFrame,
                 df_patient_characteristics: pd.DataFrame,
                 **kwargs):

        self._path_phantom = path_phantom
        self._df_phantom = None

        self._df_contours = df_contours
        self._df_barycenter = kwargs.get("df_barycenter", None)

        self._is_top_extension_warranted = None
        self._is_bottom_extension_warranted = None

        self._df_top_extension = None
        self._df_bottom_extension = None

        self._df_top_extension_area = None
        self._df_bottom_extension_area = None

        self._top_extension_vertebra = None
        self._bottom_extension_vertebra = None

        self._top_vertebra = None
        self._bottom_vertebra = None

        self._top_extension_rectangle = None
        self._bottom_extension_rectangle = None

        self._interp_top_extension = None
        self._interp_bottom_extension = None

    @property
    def df_barycenter(self):
        if self._df_barycenter is None:
            self._df_barycenter = get_contours_barycenters(self._df_contours)

        return self._df_barycenter

    @property
    def df_phantom(self):

        if self._df_phantom is None:

            self._df_phantom = pd.read_csv(self._path_phantom, encoding="ISO-8859-1", sep="\t", header=0)
            self._df_phantom = self._df_phantom[~self._df_phantom["ROIName"].isin(["skin", "body"])]
            self._df_phantom["Origine"] = "Phantom"

        return self._df_phantom

    def is_top_extension_warranted(self):
        if self._is_top_extension_warranted is None:
            self._is_top_extension_warranted = is_top_extension_warranted(self._df_contours)

        return self._is_top_extension_warranted

    def is_bottom_extension_warranted(self):
        if self._is_bottom_extension_warranted is None:
            self._is_bottom_extension_warranted = is_bottom_extension_warranted(self._df_contours)

        return self._is_bottom_extension_warranted

    def build_top_extension(self):

        list_organ_z = sorted()




class PhantomExtensionDirector:

    def __init__(self, builder):

        self._builder = builder

    def extend_top_only(self):
        pass

    def extend_bottom_only(self):
        pass

    def extend_top_and_bottom(self):
        pass
