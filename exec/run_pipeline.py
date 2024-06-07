import sys
sys.path.append("C:/Users/axelb/Documents/01-developpement/04-phandose-version/Phandose_back/PhantomDose")
from phandose.patient.patient_characteristics import get_patient_characteristics
from phandose.patient.segmentations_to_coordinates import convert_nifti_segmentation_directory_to_contours_dataframe as convert_nivti
from phandose.phantom.filter_phantoms import PhantomFilter
from phandose.phantom.phantom import create_phantom

import pandas as pd
from pathlib import Path
import platform


def main():
    """
    Launches the Phandose project with backend adjustments.

    This function initializes and configures the backend for the Phandose project,
    performing the necessary adjustments. It ensures that all dependencies are loaded,
    configurations are correct, and the backend server is ready to run.

    Steps performed by this function:
    
    1. Create patient characteristics...
    2. Convert NIFTI segmentations to XYZ...
    3. Filter phantoms...
    4. Create phantom library..
    5. Create full vertebrae...
 

    Example:
        >>> main()
        Create patient characteristics of AGORL_33...
        Convert NIFTI segmentations to XYZ...
        Filter phantoms who have same AGORL_33 charachterists ...
        Create phantom library..
        Create full vertebrae...

    Note:
        Make sure all required dependencies are installed before running this function.
        Use a virtual environment to avoid dependency conflicts.

    """
    if platform.system() == "Windows":
        dir_project = Path("C:/Users/axelb/Documents/01-developpement/04-phandose-version/Phandose_back")
    else:
        dir_project = Path("/home/maichi/work/My Projects/PhanDose")

    dir_patient = dir_project / "sample_data" / "AGORL_P33"
    dir_save = dir_project / "test"
    dir_phantom_lib = dir_project / "PhantomLib"

    # print(dir_patient)
    assert dir_patient.exists(), "The patient directory does not exist."
    if not dir_save.exists():
        dir_save.mkdir()

    dir_ct = dir_patient / "CT_TO_TOTALSEGMENTATOR"
    dir_petct = dir_patient / "PET_TO_TOTALSEGMENTATOR"

    print("Create patient characteristics...")
    df_patient_characteristics = get_patient_characteristics(dir_ct, dir_petct)
    df_patient_characteristics.to_csv(dir_save / "patient_characteristics.csv", sep=";", index=False)

    print("Convert NIFTI segmentations to XYZ...")
    dir_nifti_segmentations = dir_patient / "NIFTI_FROM_CT"
    df_contours = convert_nivti(dir_nifti_segmentations)
    df_contours.to_csv(dir_save / "contours.csv", sep=";", index=False)

    # print("Filter phantoms...")
    # df_phantom_lib = PhantomFilter(df_contours, df_patient_characteristics)
    # print(df_phantom_lib.filter())
    # df_phantom_lib.to_csv(dir_save / "phantom_lib.csv", sep=";", index=False)

    print("Create phantom library...")
    phantom_selected = "C:/Users/axelb/Documents/01-developpement/04-phandose-version/Phandose_back/PhantomDose/PhantomLib/_HFS_M_ 201709084NS_.txt"
    create_phantom(phantom_selected, df_contours, df_patient_characteristics)


if __name__ == '__main__':
    main()