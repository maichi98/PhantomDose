from phandose.patient import Patient

from pathlib import Path


class Workspace:

    """
    This class is used to represent and manage a Workspace.

    Attributes
    ----------
    _dir_workspace : (Path)
        a Path object that represents the directory of the Workspace

    Methods
    -------
    add_patient(patient: Patient)
        Adds a new patient to the Workspace.

    remove_patient(id_patient: str)
        Removes a patient from the Workspace.

    get_patient(id_patient: str) -> Patient
        Retrieves a patient from the Workspace.
    """

    def __init__(self, dir_workspace: Path, list_patients: list[Patient] = None):

        if list_patients is None:
            list_patients = []

        self._dir_workspace = dir_workspace
        self._dict_patients = {patient.id_patient: patient for patient in list_patients}

    @property
    def list_patients(self) -> list[Patient]:
        """
        Property to get the list of patients in the workspace.

        Returns
        -------
        list[Patient]
            A list of all patients in the workspace.

        """
        return list(self._dict_patients.values())

    def add_patient(self, patient: Patient):
        """
        Adds a new patient to the Workspace.

        Parameters
        ----------
        patient : (Patient)
            the patient object to be added to the workspace.
        """
        self._dict_patients[patient.id_patient] = patient

    def remove_patient(self, id_patient: str):
        """
        Removes a patient from the Workspace

        Parameters
        ----------
        id_patient, (str)
            The id of the patient to be removed from the workspace.

        """
        self._dict_patients.pop(id_patient)

    def get_patient(self, id_patient: str) -> Patient:
        """
        Retrieves a patient from the Workspace

        Parameters
        ----------
        id_patient, (str)
            The id of the patient to be retrieved from the workspace.

        Returns
        -------
        Patient
            The patient object with the given id.
        """

        return self._dict_patients[id_patient]
