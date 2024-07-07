from .modality import Modality

from pathlib import Path
import pydicom as dcm


class RtdoseModality(Modality):

    def __init__(self, id_modality: str, path_rtdose: Path):
        super().__init__(id_modality)
        self._path_rtdose = path_rtdose

    def dicom(self):
        return dcm.dcmread(str(self._path_rtdose))

    def nifti(self):
        pass
