import sys
sys.path.append("B:/02-Developpement/13-gustaveroussy/02-mohammed_axel/PhantomDose/")
from phandose.patient import get_patient_characteristics
from phandose.patient import convert_nifti_segmentations_to_xyz
from phandose.phantom import filter_phantoms

import pandas as pd
from pathlib import Path
import platform


def main():
    if platform.system() == "Windows":
        dir_project = Path(fr"B:/02-Developpement/13-gustaveroussy/02-mohammed_axel/")
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
    df_contours = convert_nifti_segmentations_to_xyz(dir_nifti_segmentations)
    df_contours.to_csv(dir_save / "contours.csv", sep=";", index=False)

    print("Filter phantoms...")
    print("Create phantom library...")
    df_phantom_lib = filter_phantoms(dir_phantom_lib,  df_contours, df_patient_characteristics)
    df_phantom_lib.to_csv(dir_save / "phantom_lib.csv", sep=";", index=False)


if __name__ == '__main__':
    main()