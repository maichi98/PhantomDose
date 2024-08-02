import pandas as pd
import numpy as np


def get_contours_barycenters(df_contours: pd.DataFrame) -> pd.DataFrame:

    """
    This function calculates the barycenter of each contour in the DataFrame.

    Parameters
    ----------
    df_contours : (pd.DataFrame),
        DataFrame with columns: ['ROIName', 'ROINumber', 'ROIContourNumber', 'ROIContourPointNumber', 'x', 'y', 'z']

    Returns
    -------
    pd.DataFrame
    a pandas DataFrame with columns: ['ROIName', 'ROINumber', 'ROIContourNumber', 'x', 'y', 'z']
    """

    # Check that there are no missing values in the DataFrame :
    if df_contours[["x", "y", "z"]].isnull().values.any():
        raise ValueError("The contours DataFrame shouldn't contain missing values in the columns 'x', 'y', 'z' !")

    # Compute the barycenter of each contour :
    df_barycenter = df_contours.groupby("ROIName")[["x", "y", "z"]].mean().reset_index()
    df_barycenter["Rts"] = 'Patient_Contours'

    df_barycenter = df_barycenter[["ROIName", "Rts", "x", "y", "z"]].rename(columns={"ROIName": "Organ",
                                                                                     "x": "Barx",
                                                                                     "y": "Bary",
                                                                                     "z": "Barz"})

    return df_barycenter


def is_vertebrae_fully_within_contours(df_contours: pd.DataFrame) -> pd.DataFrame:

    """
    Create a DataFrame indicating if each vertebra is fully within the contours.

    The function determines for each vertebra within the contours dataframe, whether it is fully
    within the contours or not, based on its z-coordinates.

    The DataFrame has two columns :
        - ROIName : Name of the vertebra
        - Full : Boolean indicating if the vertebra is fully within the contours

    Parameters
    ----------
    df_contours : pd.DataFrame
        The DataFrame containing the contours of the patient, each row must contain the following columns :
        ['ROIName', 'z']

    Returns
    -------
    pd.DataFrame
        The Full Vertebrae DataFrame, with columns : ['ROIName', 'Full']
    """

    # Check that there are no missing values in the DataFrame :
    if df_contours[["x", "y", "z"]].isnull().values.any():
        raise ValueError("The contours DataFrame shouldn't contain missing values in the columns 'x', 'y', 'z' !")

    list_vertebrae = df_contours.loc[df_contours['ROIName'].str.startswith('vertebrae'), 'ROIName'].unique().tolist()
    z_min, z_max = df_contours["z"].min(), df_contours["z"].max()

    # Compute the vertebrae_min_z and vertebrae_max_z for all vertebrae :
    vertebrae_z_min_max = df_contours.loc[df_contours['ROIName'].isin(list_vertebrae)] \
        .groupby('ROIName')['z'].agg(['min', 'max'])

    # Create a full vertebrae DataFrame :
    dict_full_vertebrae = [{"ROIName": vertebrae, "Full": (row["min"] > z_min) and (row["max"] < z_max)}
                           for vertebrae, row in vertebrae_z_min_max.iterrows()]

    df_full_vertebrae = pd.DataFrame(dict_full_vertebrae, columns=["ROIName", "Full"])

    return df_full_vertebrae


def get_mean_organ_spacing_z(df_barycenter: pd.DataFrame) -> float:
    """
    Get the mean spacing between two consecutive organs along the z-axis.

    Returns
    -------
    float
        The average spacing between two consecutive organs along the z-axis.
    """

    # Get along the z-axis the mean distance between two consecutive organs :
    list_organ_z = sorted(df_barycenter["Barz"].unique().tolist())
    list_spacing_z = np.diff(list_organ_z)

    return list_spacing_z.mean()


def needed_top_part(df_contours: pd.DataFrame) -> bool:
    """
    Check if the junction is the top junction of the phantom.

    Returns
    -------
    bool
        True if the junction is the top junction of the phantom, False otherwise.
    """

    # If the skull is present in the contours, the junction is the top junction if the skull is the highest organ :
    if "skull" in df_contours["ROIName"].unique():

        skull_z_max = df_contours.loc[df_contours["ROIName"] == "skull", "z"].max()
        return skull_z_max == df_contours["z"].max()

    return True


def needed_bottom_part(df_contours: pd.DataFrame) -> bool:
    """
    Check if the junction is the bottom junction of the phantom.

    Returns
    -------
    bool
        True if the junction is the bottom junction of the phantom, False otherwise.
    """

    return not {'femur left', 'femur right'}.issubset(df_contours["ROIName"].unique())
