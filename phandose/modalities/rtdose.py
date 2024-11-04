from .modality import Modality

from pathlib import Path
import pydicom as dcm


class RtdoseModality(Modality):

    def __init__(self,
                 series_instance_uid: str,
                 path_rtdose: Path,
                 series_description: str = None):

        super().__init__(series_instance_uid, series_description)
        self._path_rtdose = path_rtdose

    def dicom(self):
        return dcm.dcmread(str(self._path_rtdose))

    def nifti(self):
        pass
