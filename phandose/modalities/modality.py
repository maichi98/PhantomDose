from abc import ABC, abstractmethod


class Modality(ABC):

    def __init__(self, id_modality: str):
        self._id_modality = id_modality

    @property
    def id_modality(self):
        return self._id_modality

    @abstractmethod
    def dicom(self):
        pass

    @abstractmethod
    def nifti(self):
        pass
