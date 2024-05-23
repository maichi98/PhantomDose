import pandas as pd
import numpy as np
import cv2


def round_to_nearest_multiple(x, a) -> float:
    """
    Round a number to the nearest multiple of another number.

    Parameters
    ----------
    x : (float)
        The number to round.
    a : (float)
        The number to which x will be rounded.

    Returns
    -------
    float
        The rounded number.
    """

    return round(round(x / a) * a, 2)


def cartesian_to_polar_coordinates(x, y, x_c, y_c) -> tuple[float, float]:
    """
    Convert Cartesian coordinates to polar coordinates.

    Parameters
    ----------
    x : (float)
        The x-coordinate of the point.
    y : (float)
        The y-coordinate of the point.
    x_c : (float)
        The x-coordinate of the center point.
    y_c : (float)
        The y-coordinate of the center point.

    Returns
    -------
    tuple[float, float]
        The radius and the angle of the polar coordinates.

    """
    complex_format = x - x_c + 1j * (y - y_c)
    return np.abs(complex_format), np.angle(complex_format, deg=False)


def calculate_contour_area(df_contours: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the area of a contour.

    Parameters
    ----------
    df_contours : (pd.DataFrame)
        A DataFrame containing the contour points.
        The DataFrame must have the following columns:
            - x: x-coordinate of the contour point
            - y: y-coordinate of the contour point

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the area of the contour.
        The DataFrame has the following columns:
            - Centrex: the x-coordinate of the center of the contour
            - Centrey: the y-coordinate of the center of the contour
            - z
            - ROIName
            - ROINumber
            - ROIContourNumber
            - area: the area of the contour
    """

    def calculate_area(contour):
        rounded_contour = contour.round({'x': 0, 'y': 0}).drop_duplicates(subset=['x', 'y'], keep='last')
        center = np.array(rounded_contour[['x', 'y']].to_numpy()).astype(np.int32)
        xul, yul, wr, hr = cv2.boundingRect(center)
        center_x = xul + wr / 2
        center_y = yul + hr / 2
        area = cv2.contourArea(center)
        return pd.Series({'Centrex': center_x, 'Centrey': center_y, 'area': area})

    cols = ['z', 'ROINumber', 'ROIContourNumber']
    df_area = df_contours.groupby(cols).apply(calculate_area).reset_index()
    df_area['ROIName'] = df_contours['ROIName'].groupby(cols).first().reset_index(drop=True)
    return df_area[['Centrex', 'Centrey', 'z', 'ROIName', 'ROINumber', 'ROIContourNumber', 'area']]
