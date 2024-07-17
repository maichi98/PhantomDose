from .modality import Modality

from pathlib import Path
import pydicom as dcm


class PETScanModality(Modality):
    """
    Class that represents a PET Scan modality.

    Attributes:
    -----------
    series_instance_uid : (str)
        Series Instance UID.

    list_path_slices : (list[Path])
        List of paths to the slices of the PET Scan.

    series_description : (str), optional
        Series Description.

    Methods:
    --------
    dicom()
        Returns the PET modality in DICOM format.

    nifti()
        Returns the PET modality in NIfTI format.
    """

    def __init__(self,
                 series_instance_uid: str,
                 list_path_slices: list[Path],
                 series_description: str = None):

        """
        Constructor of the class PETScanModality.

        Parameters:
        -----------
        series_instance_uid : (str)
            Series Instance UID.

        list_path_slices : (list[Path])
            List of paths to the slices of the PET Scan.

        series_description : (str), optional
            Series Description.
        """

        super().__init__(series_instance_uid, series_description)
        self._list_path_slices = list_path_slices

    @property
    def list_path_slices(self):
        """
        Getter method for the list of paths to the slices of the PET Scan.
        """

        return self._list_path_slices

    def dicom(self):
        """
        Returns the PET modality in DICOM format.
        """

        return [dcm.dcmread(str(path_slice)) for path_slice in self._list_path_slices]

    def nifti(self):
        """
        Returns the PET modality in NIfTI format.
        """

        pass
