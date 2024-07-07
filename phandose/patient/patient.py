from phandose.modalities import Modality


class Patient:

    def __init__(self, id_patient: str, list_modalities: list[Modality] = None):

        if list_modalities is None:
            list_modalities = []

        self._id_patient = id_patient
        self._dict_modalities = {modality.id_modality: modality for modality in list_modalities}

    @property
    def id_patient(self):
        return self._id_patient

    @property
    def dict_modalities(self):
        return self._dict_modalities

    def add_modality(self, modality: Modality):
        self._dict_modalities[modality.id_modality] = modality

    def remove_modality(self, id_modality: str):
        del self._dict_modalities[id_modality]

    def get_modality(self, id_modality: str):
        return self._dict_modalities[id_modality]
