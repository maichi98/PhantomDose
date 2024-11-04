from abc import abstractmethod


class ScanJunctionBuilder:

    def __init__(self,
                 df_contours,
                 df_barycenter):

        self._df_contours = df_contours
        self._df_barycenter = df_barycenter

    @property
    def df_contours(self):
        return self._df_contours

    @property
    def df_barycenter(self):
        return self._df_barycenter

    @abstractmethod
    def build(self):
        pass
