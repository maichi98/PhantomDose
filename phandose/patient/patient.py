from .study import Study


class Patient:
    """
    Class representing a patient.

    Attributes:
    -----------
    patient_id : (str)
        Patient ID.

    dict_studies : (dict[str: Study])
        Dictionary containing the studies of the patient.

    Methods:
    --------
    add_study(study)
        Add a study to the patient.

    remove_study(study_instance_uid)
        Remove a study from the patient.

    get_study(study_instance_uid)
        Get a study from the patient.

    """

    def __init__(self,
                 patient_id: str,
                 list_studies: list[Study] = None):

        """
        Constructor of the class Patient.

        Parameters:
        -----------
        patient_id : (str)
            Patient ID.

        list_studies : (list[Study]), optional
            List of studies of the patient

        """

        self._patient_id = patient_id
        self._dict_studies = {study.study_instance_uid: study
                              for study in list_studies} if list_studies is not None else {}

    @property
    def patient_id(self):
        """
        Getter method for the Patient ID.
        """

        return self._patient_id

    @property
    def dict_studies(self):
        """
        Getter method for the dictionary of studies.
        """

        return self._dict_studies

    def add_study(self, study: Study):
        """
        Add a study to the patient.

        Parameters:
        -----------
        study : (Study)
            Study to be added.
        """

        self._dict_studies[study.study_instance_uid] = study

    def remove_study(self, study_instance_uid: str):
        """
        Remove a study from the patient.

        Parameters:
        -----------
        study_instance_uid : (str)
            Study Instance UID of the study to be removed
        """

        self._dict_studies.pop(study_instance_uid)

    def get_study(self, study_instance_uid: str):
        """
        Get a study from the patient.

        Parameters:
        -----------
        study_instance_uid : (str)
            Study Instance UID of the study to be retrieved.
        """

        return self._dict_studies.get(study_instance_uid)
