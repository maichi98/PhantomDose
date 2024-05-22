from phandose.phantom.phantom_utils import (round_nearest,
                                            cart_to_pol,
                                            Get_Area)

from scipy.interpolate import interp1d
from pathlib import Path
import pandas as pd
import numpy as np
import cv2


def _get_phantom_lib_dataframe(path_phantom_lib: Path) -> pd.DataFrame:
    """
    Create the Phantom Library DataFrame from the Phantom text files located at the given path.

    The DataFrame has three columns :
        - Phantom : Name of the Phantom text file
        - Position : Position of the Phantom (e.g. 'HFS', 'FFS')
        - Sex : Sex of the Phantom (e.g. 'M', 'F')

    :param path_phantom_lib: Path to the directory containing the phantom library text files.
    :return: pd.DataFrame, The Phantom Library DataFrame, with columns : ['Phantom', 'Position', 'Sex']
    """

    df_phantom_lib = pd.DataFrame({"Phantom": [filename.name for filename in path_phantom_lib.glob("*.txt")]})

    df_phantom_lib["Position"], df_phantom_lib["Sex"] = zip(*df_phantom_lib["Phantom"].map(lambda x: x.split("_")[1:3]))

    return df_phantom_lib


def filter_phantoms(dir_phantom_lib: Path | str,
                    df_contours: pd.DataFrame,
                    df_patient_characteristics: pd.DataFrame) -> list[str]:
    """
    Filters the phantom library based on the patient's characteristics and the contours.

    This function takes as input the directory of the phantom library, the DataFrame of the patient's contours,
    and the DataFrame of the patient's characteristics. It filters the phantom library based on the patient's
    sex, position, size, and weight. The function returns a list of the names of the phantoms that passed the filters.

    :param dir_phantom_lib: (Path | str), The directory containing the phantom library text files.
    :param df_contours: pd.DataFrame, The DataFrame containing the contours of the patient. Each row must contain
                                      the following columns : ['ROIName', 'z']
    :param df_patient_characteristics: pd.DataFrame, The DataFrame containing the patient's characteristics. It must
                                      contain the following columns : ['PatientSex', 'PatientPosition']

    :return: list[str], The list of the names of the phantoms that passed the filters.
    """
    # Make sure path_phantom_lib is a Path object :
    dir_phantom_lib = Path(dir_phantom_lib)

    # Load the phantom library :
    df_phantom_lib = _get_phantom_lib_dataframe(dir_phantom_lib)

    # ----- Filter the phantoms based on the patient's sex and position : ----------------------------------------------
    patient_info = df_patient_characteristics.loc[df_patient_characteristics["Type"] == "CT_TO_TOTALSEGMENTATOR"].iloc[
        0]
    sex, position = patient_info['PatientSex'], patient_info['PatientPosition']

    df_phantom_lib = df_phantom_lib.loc[(df_phantom_lib["Sex"] == sex) & (df_phantom_lib["Position"] == position)]
    df_phantom_lib["SizeRatio"] = -1
    # ------------------------------------------------------------------------------------------------------------------

    # ----- Create the full vertebrae dataframe : ----------------------------------------------------------------------
    df_full_vertebrae = _get_full_vertebrae_dataframe(df_contours)
    list_full_vertebrae = df_full_vertebrae.loc[df_full_vertebrae["Full"], "ROIName"].tolist()

    patient_z_max = df_contours.loc[df_contours["ROIName"].isin(list_full_vertebrae), "z"].max()
    patient_z_min = df_contours.loc[df_contours["ROIName"].isin(list_full_vertebrae), "z"].min()
    patient_size = patient_z_max - patient_z_min
    # ------------------------------------------------------------------------------------------------------------------

    # ----- filter the phantom library based on size : -----------------------------------------------------------------
    list_phantoms = df_phantom_lib["Phantom"].tolist().unique()

    list_vertebrae = {
        'vertebrae T1', 'vertebrae T2', 'vertebrae T3', 'vertebrae T4', 'vertebrae T5', 'vertebrae T6', 'vertebrae T7',
        'vertebrae T8', 'vertebrae T9', 'vertebrae T10', 'vertebrae T11', 'vertebrae T12',
        'vertebrae C1', 'vertebrae C2', 'vertebrae C3', 'vertebrae C4', 'vertebrae C5', 'vertebrae C6', 'vertebrae C7',
        'vertebrae L1', 'vertebrae L2', 'vertebrae L3', 'vertebrae L4', 'vertebrae L5',
        'vertebrae S1'
    }

    for phantom in list_phantoms:

        df_phantom = pd.read_csv(dir_phantom_lib / phantom, encoding="ISO-8859-1", sep="\t", header=0)

        if list_vertebrae.issubset(df_phantom["ROIName"].str.startswith("vertebrae").unique()):
            phantom_z_max = df_phantom.loc[df_phantom["ROIName"].isin(list_full_vertebrae), "z"].max()
            phantom_z_min = df_phantom.loc[df_phantom["ROIName"].isin(list_full_vertebrae), "z"].min()
            phantom_size = phantom_z_max - phantom_z_min

            df_phantom_lib.loc[df_phantom_lib["Phantom"] == phantom, "SizeRatio"] = round(
                100 * abs(1 - phantom_size / patient_size))

    df_phantom_lib = df_phantom_lib.loc[(df_phantom_lib["SizeRatio"] != -1) & (df_phantom_lib["SizeRatio"] <= 10)]
    # -------------------------------------------------------------- ---------------------------------------------------

    # ----- Filter the phantom library based on the patient's weight : -------------------------------------------------
    df_last_full_vertebrae = df_contours.loc[
        (df_contours['ROIName'] == 'body trunc') &
        (df_contours["z"] == df_contours["ROIName"].isin(list_full_vertebrae)["z"].min())
        ]
    patient_center = df_last_full_vertebrae[["x", "y"]].to_numpy().astype(np.int32)
    patient_xul, patient_yul, patient_wr, patient_hr = cv2.boundingRect(patient_center)
    list_phantoms = df_phantom_lib["Phantom"].tolist().unique()

    for phantom in list_phantoms:
        df_phantom = pd.read_csv(dir_phantom_lib / phantom, encoding="ISO-8859-1", sep="\t", header=0)

        df_phantom_last_full_vertebrae = df_phantom.loc[
            (df_phantom['ROIName'] == 'body trunc') &
            (df_phantom['z'] == df_phantom['ROIName'].isin(list_full_vertebrae)['z'].min())
            ]

        phantom_center = df_phantom_last_full_vertebrae[['x', 'y']].to_numpy().astype(np.int32)
        phantom_xul, phantom_yul, phantom_wr, phantom_hr = cv2.boundingRect(phantom_center)

        df_phantom_lib.loc[df_phantom_lib["Phantom"] == phantom, "Thinner"] = (patient_wr >= (phantom_wr - 25) and
                                                                               patient_hr >= (phantom_hr - 25))

    df_phantom_lib = df_phantom_lib.loc[df_phantom_lib["Thinner"]]
    # ------------------------------------------------------------------------------------------------------------------

    list_selected_phantoms = df_phantom_lib["Phantom"].unique().tolist()

    return list_selected_phantoms


def _get_top_junction_dataframe(df_contours: pd.DataFrame,
                                df_barycenter: pd.DataFrame) -> dict:
    """
    Create a DataFrame that indicates the top junction of the patient's contours.

    :param df_contours: pd.DataFrame,
    :param df_barycenter:
    :return:
    """

    list_organ_z = sorted(df_barycenter["Barz"].unique().tolist())
    list_delta_z = [t - s for s, t in zip(list_organ_z, list_organ_z[1:])]
    delta_z_mean = sum(list_delta_z) / len(list_delta_z)

    is_top_junction = True
    top_vertebra_z = df_barycenter["Barz"].max()

    if "skull" in df_contours["ROIName"].unique():
        skull_z_max = df_contours.loc[df_contours["ROIName"] == "skull", "z"].max()
        skull_z_min = df_contours.loc[df_contours["ROIName"] == "skull", "z"].min()

        top_vertebra_z = df_barycenter.loc[df_barycenter["Barz"] < (skull_z_min - 3 * delta_z_mean), "Barz"].max()
        is_top_junction = (skull_z_max == df_contours["z"].max())

    top_vertebra_x = df_barycenter.loc[df_barycenter["Barz"] == top_vertebra_z, "Barx"].values[0]
    top_vertebra_y = df_barycenter.loc[df_barycenter["Barz"] == top_vertebra_z, "Bary"].values[0]

    top_junction_vertebra = df_barycenter.loc[df_barycenter["Barz"] == top_vertebra_z, "Organ"].values[0]

    df_top_junction = pd.DataFrame()
    df_area_top_junction = pd.DataFrame()
    top_rectangle = np.array([])
    interp_top_junction = None

    if is_top_junction:
        df_top_junction = df_contours.loc[df_contours["ROIName"] == 'body trunc'].copy()
        df_top_junction["Ecart"] = abs(df_top_junction["z"] - top_vertebra_z)
        ecart_min = df_top_junction["Ecart"].min()
        df_top_junction = df_top_junction.loc[df_top_junction["Ecart"] == ecart_min]
        df_area_top_junction = Get_Area(df_top_junction)
        df_area_top_junction["Centrality"] = abs(df_area_top_junction["Centrex"])
        center_min = df_area_top_junction["Centrality"].min()
        contour_num = \
            df_area_top_junction.loc[df_area_top_junction["Centrality"] == center_min, "ROIContourNumber"].values[0]
        df_top_junction = df_top_junction.loc[df_top_junction["ROIContourNumber"] == contour_num]

        center = df_top_junction[["x", "y"]].to_numpy()
        center = np.array([center]).astype(np.int32)
        xul, yul, wr, hr = cv2.boundingRect(center)
        top_rectangle = np.array([
            [xul, yul],
            [xul, yul + hr],
            [xul + wr, yul + hr],
            [xul + wr, yul]
        ])

        x_c, y_c = df_area_top_junction.iloc[0]['Centrex'], df_area_top_junction.iloc[0]['Centrey']
        df_top_junction['Polar'] = df_top_junction.apply(lambda row: cart_to_pol(row['x'], row['y'], x_c, y_c), axis=1)
        df_top_junction['rpat'] = df_top_junction.apply(lambda row: row['Polar'][0], axis=1)
        df_top_junction['tpat'] = df_top_junction.apply(lambda row: row['Polar'][1], axis=1)
        df_top_junction = df_top_junction.drop_duplicates(subset=['tpat'], keep='last')

        x, y = df_top_junction['x'].to_numpy(), df_top_junction['y'].to_numpy()
        interp_top_junction = interp1d(x, y, fill_value='extrapolate', kind='slinear')

    d_top_junction = {
        "is_top_junction": is_top_junction,
        "df_top_junction": df_top_junction,
        "df_area_top_junction": df_area_top_junction,
        "top_junction_vertebra": top_junction_vertebra,
        "top_vertebra_z": top_vertebra_z,
        "top_vertebra_x": top_vertebra_x,
        "top_vertebra_y": top_vertebra_y,
        "top_rectangle": top_rectangle,
        "interp_top_junction": interp_top_junction
    }

    return d_top_junction


def _get_bottom_junction_dataframe(df_contours: pd.DataFrame,
                                   df_barycenter: pd.DataFrame) -> dict:
    """
    Create a DataFrame that indicates the bottom junction of the patient's contours.

    :param df_contours: pd.DataFrame,
    :return:
    """

    is_bottom_junction = ({'femur left', 'femur right'}.issubset(df_contours["ROIName"].unique()) == False)
    bottom_vertebra_z = df_barycenter["Barz"].min()

    bottom_vertebra_x = df_barycenter.loc[df_barycenter["Barz"] == bottom_vertebra_z, "Barx"].values[0]
    bottom_vertebra_y = df_barycenter.loc[df_barycenter["Barz"] == bottom_vertebra_z, "Bary"].values[0]

    df_bottom_junction = pd.DataFrame()
    df_area_bottom_junction = pd.DataFrame()
    bottom_rectangle = np.array([])
    interp_bottom_junction = None
    if is_bottom_junction:

        df_bottom_junction = df_contours.loc[df_contours["ROIName"] == 'body trunc'].copy()
        df_bottom_junction["Ecart"] = abs(df_bottom_junction["z"] - bottom_vertebra_z)

        ecart_min = df_bottom_junction["Ecart"].min()
        df_bottom_junction = df_bottom_junction.loc[df_bottom_junction["Ecart"] == ecart_min]

        df_area_bottom_junction = Get_Area(df_bottom_junction)

        df_area_bottom_junction["Centrality"] = abs(df_area_bottom_junction["Centrex"])
        center_min = df_area_bottom_junction["Centrality"].min()
        contour_num = \
            df_area_bottom_junction.loc[df_area_bottom_junction["Centrality"] == center_min, "ROIContourNumber"].values[
                0]
        df_bottom_junction = df_bottom_junction.loc[df_bottom_junction["ROIContourNumber"] == contour_num]

        center = df_bottom_junction[["x", "y"]].to_numpy()
        center = np.array([center]).astype(np.int32)
        xul, yul, wr, hr = cv2.boundingRect(center)
        bottom_rectangle = np.array([
            [xul, yul],
            [xul, yul + hr],
            [xul + wr, yul + hr],
            [xul + wr, yul]
        ])

        get_polar = lambda row: cart_to_pol((row['x'],
                                             row['y'],
                                             df_area_bottom_junction.iloc[0]['Centrex'],
                                             df_area_bottom_junction.iloc[0]['Centrey']))

        df_bottom_junction['Polar'] = df_bottom_junction.apply(get_polar, axis=1)

        df_bottom_junction['rpat'] = df_bottom_junction.apply(lambda row: row['Polar'][0], axis=1)
        df_bottom_junction['tpat'] = df_bottom_junction.apply(lambda row: row['Polar'][1], axis=1)
        x, y = df_bottom_junction['x'].to_numpy(), df_bottom_junction['y'].to_numpy()
        interp_bottom_junction = interp1d(x, y, fill_value='extrapolate', kind='slinear')

    d_bottom_junction = {
        "is_bottom_junction": is_bottom_junction,
        "df_bottom_junction": df_bottom_junction,
        "df_area_bottom_junction": df_area_bottom_junction,
        "bottom_vertebra_z": bottom_vertebra_z,
        "bottom_vertebra_x": bottom_vertebra_x,
        "bottom_vertebra_y": bottom_vertebra_y,
        "bottom_rectangle": bottom_rectangle,
        "interp_bottom_junction": interp_bottom_junction}

    return d_bottom_junction


def create_phantom(path_phantom: str,
                   df_contours: pd.DataFrame,
                   df_patient_characteristics: pd.DataFrame):
    # Load the selected phantom :
    df_phantom = pd.read_csv(path_phantom, encoding="ISO-8859-1", sep="\t", header=0)
    df_phantom = df_phantom.loc[~df_phantom["ROIName"].isin(["skin", "body"])]
    df_phantom["Origine"] = "Phantom"

    # ------ load the patient's junction dataframes : ------------------------------------------------------------------
    # ------ Load the barycenter dataframe :
    df_barycenter = _get_barycenter_dataframe(df_contours)

    # ------ Load the top junction dictionary :
    d_top_junction = _get_top_junction_dataframe(df_contours, df_barycenter)
    df_top_junction = d_top_junction["df_top_junction"]
    df_area_top_junction = d_top_junction["df_area_top_junction"]
    interp_top_junction = d_top_junction["interp_top_junction"]

    # ------ Load the bottom junction dictionary :
    d_bottom_junction = _get_bottom_junction_dataframe(df_contours, df_barycenter)
    df_bottom_junction = d_bottom_junction["df_bottom_junction"]
    df_area_bottom_junction = d_bottom_junction["df_area_bottom_junction"]
    interp_bottom_junction = d_bottom_junction["interp_bottom_junction"]
    # ------------------------------------------------------------------------------------------------------------------

    if d_top_junction["is_top_junction"]:

        phantom_x = df_phantom.loc[df_phantom["ROIName"] == d_top_junction["top_junction_vertebra"], "x"].mean()
        phantom_y = df_phantom.loc[df_phantom["ROIName"] == d_top_junction["top_junction_vertebra"], "y"].mean()
        phantom_z = df_phantom.loc[df_phantom["ROIName"] == d_top_junction["top_junction_vertebra"], "z"].mean()

        df_phantom_top = df_phantom.loc[df_phantom["z"] >= phantom_z]
        df_phantom_top["x"] += (d_top_junction["top_vertebra_x"] - phantom_x)
        df_phantom_top["y"] += (d_top_junction["top_vertebra_y"] - phantom_y)
        df_phantom_top["z"] += (d_top_junction["top_vertebra_z"] - phantom_z)

        df_junction_phantom = df_phantom_top.loc[
            (df_phantom_top["ROIName"] == "body trunc") &
            (df_phantom_top["z"] == df_phantom_top["z"].min())
            ]

        df_area_junction_phantom = Get_Area(df_junction_phantom)
        df_area_junction_phantom["Central"] = abs(df_area_junction_phantom["Centrex"])

        center_min = df_area_junction_phantom["Central"].min()
        contour_num = \
            df_area_junction_phantom.loc[df_area_junction_phantom["Central"] == center_min, "ROIContourNumber"].values[
                0]

        df_junction_phantom = df_junction_phantom.loc[df_junction_phantom["ROIContourNumber"] == contour_num]
        phantom_center = df_junction_phantom[["x", "y"]].to_numpy()
        phantom_center = np.array([phantom_center]).astype(np.int32)

        phantom_xul, phantom_yul, phantom_wr, phantom_hr = cv2.boundingRect(phantom_center)

        phantom_top_rectangle = np.array([
            [phantom_xul, phantom_yul],
            [phantom_xul, phantom_yul + phantom_hr],
            [phantom_xul + phantom_wr, phantom_yul + phantom_hr],
            [phantom_xul + phantom_wr, phantom_yul]
        ])

        h, status = cv2.findHomography(phantom_top_rectangle, d_top_junction["top_rectangle"])

        def compute_xh(row, h):
            if row["ROIName"] == "body trunc":
                return (h[0, 0] * row["x"] + h[0, 1] * row["y"] + h[0, 2]) / (
                        h[2, 0] * row["x"] + h[2, 1] * row["y"] + h[2, 2])
            else:
                return row["x"]

        df_phantom_top["xh"] = df_phantom_top.apply(lambda row: compute_xh(row, h), axis=1)

        def compute_yh(row, h):
            if row["ROIName"] == "body trunc":
                return (h[1, 0] * row["x"] + h[1, 1] * row["y"] + h[1, 2]) / (
                        h[2, 0] * row["x"] + h[2, 1] * row["y"] + h[2, 2])

        df_phantom_top["yh"] = df_phantom_top.apply(lambda row: compute_yh(row, h), axis=1)

        df_phantom_top["zh"] = df_phantom_top["z"]

        df_phantom_top.drop(columns=["x", "y", "z"], inplace=True)
        df_phantom_top.rename(columns={"xh": "x", "yh": "y", "zh": "z"}, inplace=True)

        l_smooth = 20
        df_phantom_body_trunc = df_phantom_top.loc[df_phantom_top["ROIName"] == "body trunc"]
        df_phantom_body_trunc["dz"] = abs(df_phantom_body_trunc["z"] - df_top_junction.iloc[0]["z"] - l_smooth)
        dz_min = df_phantom_body_trunc["dz"].min()

        df_phantom_smooth_junction = df_phantom_body_trunc.loc[df_phantom_body_trunc["dz"] == dz_min]
        df_phantom_smooth_junction[
            "Polar"] = df_phantom_smooth_junction.apply(lambda row:
                                                        cart_to_pol(row['x'],
                                                                    row['y'],
                                                                    df_area_top_junction.iloc[0]['Centrex'],
                                                                    df_area_top_junction.iloc[0]['Centrey']), axis=1)

        df_phantom_smooth_junction["rpat"] = df_phantom_smooth_junction.apply(lambda row: row["Polar"][0], axis=1)
        df_phantom_smooth_junction["tpat"] = df_phantom_smooth_junction.apply(lambda row: row["Polar"][1], axis=1)

        df_phantom_smooth_junction = df_phantom_smooth_junction.drop_duplicates(subset=["tpat"], keep="last")
        x, y = df_phantom_smooth_junction["x"].to_numpy(), df_phantom_smooth_junction["y"].to_numpy()
        phantom_interp = interp1d(x, y, fill_value="extrapolate", kind="slinear")

        # ----- Apply interpolations to the phantom body :
        df_to_smooth = df_phantom_body_trunc.loc[df_phantom_body_trunc['z'] <= df_phantom_smooth_junction.iloc[0]['z']]
        df_to_smooth['Polar'] = df_to_smooth.apply(lambda row: cart_to_pol(row['x'],
                                                                           row['y'],
                                                                           df_area_junction_phantom.iloc[0]['Centrex'],
                                                                           df_area_junction_phantom.iloc[0]['Centrey']),
                                                   axis=1)

        df_to_smooth['teta'] = df_to_smooth.apply(lambda row: row['Polar'][1], axis=1)
        df_to_smooth['pond'] = df_to_smooth.apply(lambda row: (row['z'] - df_top_junction.iloc[0]['z']) / l_smooth, axis=1)

        df_to_smooth['rPred'] = df_to_smooth.apply(lambda x: x.pond * phantom_interp(x.teta) + (1 - x.pond) * interp_top_junction(x.teta), axis=1)
        df_to_smooth['xPred'] = df_to_smooth.apply(lambda x: x.rPred * np.cos(x.teta) + df_area_top_junction.iloc[0]["Centrex"], axis=1)
        df_to_smooth['yPred'] = df_to_smooth.apply(lambda x: x.rPred * np.sin(x.teta) + df_area_top_junction.iloc[0]["Centrey"], axis=1)

        df_to_smooth = df_to_smooth.drop(columns=["Polar", "teta", "pond", "rPred"], axis=1)
        df_to_smooth.rename(columns={"xPred": "x", "yPred": "y"}, inplace=True)

        # Concat contours :
        df_top_internal_phantom = df_phantom_top.loc[~df_phantom_top["ROIName"].isin(["body trunc", "body extremities"])]
        df_top_extremities_phantom = df_phantom_top.loc[df_phantom_top["ROIName"] == "body extremities"]
        df_top_body_trunc_non_smooth_phantom = df_phantom_top.loc[
            (df_phantom_top["ROIName"] == "body trunc") &
            (df_phantom_top["z"] > df_phantom_smooth_junction.iloc[0]["z"])
        ]
        df_phantom_top = pd.concat([df_top_internal_phantom,
                                    df_top_extremities_phantom,
                                    df_top_body_trunc_non_smooth_phantom,
                                   df_to_smooth])

        df_phantom_top[["Origine", "Section"]] = ['Phantom', 1]

        # --------------------------------------------------------------------------------------------------------------

    if d_bottom_junction["is_bottom_junction"]:

        phantom_x = df_phantom.loc[df_phantom["ROIName"] == d_bottom_junction["bottom_vertebra_z"], "x"].mean()
        phantom_y = df_phantom.loc[df_phantom["ROIName"] == d_bottom_junction["bottom_vertebra_z"], "y"].mean()
        phantom_z = df_phantom.loc[df_phantom["ROIName"] == d_bottom_junction["bottom_vertebra_z"], "z"].mean()

        df_phantom_bottom = df_phantom.loc[df_phantom["z"] <= phantom_z]
        df_phantom_bottom["x"] += (d_bottom_junction["bottom_vertebra_x"] - phantom_x)
        df_phantom_bottom["y"] += (d_bottom_junction["bottom_vertebra_y"] - phantom_y)
        df_phantom_bottom["z"] += (d_bottom_junction["bottom_vertebra_z"] - phantom_z)

        df_junction_phantom = df_phantom_bottom.loc[
            (df_phantom_bottom["ROIName"] == "body trunc") &
            (df_phantom_bottom["z"] == df_phantom_bottom["z"].max())
            ]

        df_area_junction_phantom = Get_Area(df_junction_phantom)
        df_area_junction_phantom["Central"] = abs(df_area_junction_phantom["Centrex"])

        center_min = df_area_junction_phantom["Central"].min()
        contour_num = \
            df_area_junction_phantom.loc[df_area_junction_phantom["Central"] == center_min, "ROIContourNumber"].values[
                0]

        df_junction_phantom = df_junction_phantom.loc[df_junction_phantom["ROIContourNumber"] == contour_num]
        phantom_center = df_junction_phantom[["x", "y"]].to_numpy()
        phantom_center = np.array([phantom_center]).astype(np.int32)

        phantom_xul, phantom_yul, phantom_wr, phantom_hr = cv2.boundingRect(phantom_center)

        phantom_bottom_rectangle = np.array([
            [phantom_xul, phantom_yul],
            [phantom_xul, phantom_yul + phantom_hr],
            [phantom_xul + phantom_wr, phantom_yul + phantom_hr],
            [phantom_xul + phantom_wr, phantom_yul]
        ])

        h, status = cv2.findHomography(phantom_bottom_rectangle, d_bottom_junction["bottom_rectangle"])
