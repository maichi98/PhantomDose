import pandas as pd


class ScanJunction:

    def __init__(self,
                 vertebra: dict = None,
                 df_junction: pd.DataFrame = None,
                 df_junction_area: pd.DataFrame = None,
                 interp_junction=None,
                 rectangle=None):

        self._vertebra = vertebra
        self._df_junction = df_junction
        self._df_junction_area = df_junction_area
        self._interp_junction = interp_junction
        self._rectangle = rectangle

    @property
    def vertebra(self):
        return self._vertebra

    def set_vertebra(self, organ, bar_x, bar_y, bar_z):
        self._vertebra = {"Organ": organ, "Barx": bar_x, "Bary": bar_y, "Barz": bar_z}

    @property
    def df_junction(self):
        return self._df_junction

    @df_junction.setter
    def df_junction(self, df_junction):
        self._df_junction = df_junction

    @property
    def df_junction_area(self):
        return self._df_junction_area

    @df_junction_area.setter
    def df_junction_area(self, df_junction_area):
        self._df_junction_area = df_junction_area

    @property
    def interp_junction(self):
        return self._interp_junction

    @property
    def rectangle(self):
        return self._rectangle
