from abc import ABC, abstractmethod


class Modality(ABC):
    """
    Abstract class that represents a modality.

    Attributes:
    -----------
    series_instance_uid : (str)
        Series Instance UID.

    series_description : (str), optional
        Series Description.

    Methods:
    --------
    dicom()
        Abstract method that returns the modality in DICOM format.

    nifti()
        Abstract method that returns the modalities in NIfTI format.
    """

    def __init__(self,
                 series_instance_uid: str,
                 series_description: str = None):
        """
        Constructor of the class Modality.

        Parameters:
        -----------
        series_instance_uid : (str)
            Series Instance UID.

        series_description : (str), optional
            Series Description.
        """

        self._series_instance_uid = series_instance_uid
        self._series_description = series_description

    @property
    def series_instance_uid(self):
        """
        Getter method for the Series Instance UID.
        """

        return self._series_instance_uid

    @property
    def series_description(self):
        """
        Getter method for the Series Description.
        """

        return self._series_description

    @abstractmethod
    def dicom(self):
        """
        Abstract method that returns the modality in DICOM format.
        """

        pass

    @abstractmethod
    def nifti(self):
        """
        Abstract method that returns the modality in NIfTI format.
        """

        pass
