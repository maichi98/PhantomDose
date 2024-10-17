from phandose.modalities import Modality


class Study:
    """"
    Class that represents a study.

    Attributes:
    -----------
    study_instance_uid : (str)
        Study Instance UID.

    study_description : (str), optional
        Study Description.

    dict_modalities : (dict[str: Modality])
        Dictionary containing the modalities of the study.

    Methods:
    --------
    add_modality(modality)
        Add a modality to the study.

    remove_modality(series_instance_uid)
        Remove a modality from the study.

    get_modality(series_instance_uid)
        Get a modality from the study.
    """

    def __init__(self,
                 study_instance_uid: str,
                 list_modalities: list = None,
                 study_description: str = None):
        """
        Constructor of the class Study.

        Parameters:
        -----------
        study_instance_uid : (str)
            Study Instance UID.

        list_modalities : (list[Modality]), optional
            List of modalities of the study.

        study_description : (str), optional
            Study Description.
        """

        self._study_instance_uid = study_instance_uid
        self._study_description = study_description
        self._dict_modalities = {modality.series_instance_uid: modality
                                 for modality in list_modalities} if list_modalities is not None else {}

    @property
    def study_instance_uid(self):
        """
        Getter method for the Study Instance UID.
        """

        return self._study_instance_uid

    @property
    def study_description(self):
        """
        Getter method for the Study Description.
        """

        return self._study_description

    @property
    def dict_modalities(self):
        """
        Getter method for the Dictionary containing the modalities of the study.
        """

        return self._dict_modalities

    def add_modality(self, modality: Modality):
        """
        Add a modality to the study.

        Parameters:
        -----------
        modality : (Modality)
            Modality to add to the study.
        """
        self._dict_modalities[modality.series_instance_uid] = modality

    def remove_modality(self, series_instance_uid: str):
        """"
        Remove a modality from the study.

        Parameters:
        -----------
        series_instance_uid : (str)
            Series Instance UID of the modality to remove.

        """
        self._dict_modalities.pop(series_instance_uid)

    def get_modality(self, series_instance_uid: str):
        """"
        Get a modality from the study.

        Parameters:
        -----------
        series_instance_uid : (str)
            Series Instance UID of the modality to get.

        Returns:
        --------
        Modality
            The modality corresponding to the Series Instance UID.
        """
        return self._dict_modalities.get(series_instance_uid)
