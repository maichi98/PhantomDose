from .modality import Modality

from pathlib import Path
import pydicom as dcm


class PETScanModality(Modality):

    def __init__(self, id_modality: str, list_path_slices: list[Path]):
        super().__init__(id_modality)
        self._list_path_slices = list_path_slices

    def dicom(self):
        return [dcm.dcmread(str(path_slice)) for path_slice in self._list_path_slices]

    def nifti(self):
        pass
