from scan_junction_builder import ScanJunctionBuilder


class ScanTopJunctionBuilder(ScanJunctionBuilder):

    def __init__(self,
                 df_contours,
                 df_barycenter,):

        super().__init__(df_contours, df_barycenter)


    def build(self):
        pass
