import pandas as pd
import numpy as np
import cv2


def round_nearest(x, a):
    return round(round(x / a) * a, 2)


def cart_to_pol(x, y, x_c, y_c):
    complex_format = x - x_c + 1j * (y - y_c)
    return np.abs(complex_format), np.angle(complex_format, deg=False)


def Get_Area(SelectedContours):
    """
    Contour Area : Calcule la surface d'un coutour
    """

    ZList = sorted(SelectedContours.z.unique().tolist())
    AreaDf = pd.DataFrame()
    for z in ZList:
        Coupe = SelectedContours[SelectedContours['z'] == z]
        ROINumberList = sorted(Coupe.ROINumber.unique().tolist())
        for r in ROINumberList:
            ROI = Coupe[Coupe['ROINumber'] == r]
            ROIContourNumberList = sorted(ROI.ROIContourNumber.unique().tolist())
            for c in ROIContourNumberList:
                Contour = ROI[ROI['ROIContourNumber'] == c]
                Contour = Contour.round({'x': 0, 'y': 0})
                Contour = Contour.drop_duplicates(subset=['x', 'y'], keep='last')
                ctr = Contour[['x', 'y']].to_numpy()
                ctrint = np.array([ctr]).astype(np.int32)
                XUL, YUL, WR, HR = cv2.boundingRect(ctrint)
                Centrex = XUL + WR / 2
                Centrey = YUL + HR / 2
                area = cv2.contourArea(ctrint)
                data = {'Centrex': [Centrex], 'Centrey': [Centrey], 'z': [z],
                        'ROIName': [Contour.iloc[0]['ROIName']],
                        'ROINumber': [r],
                        'ROIContourNumber': [c],
                        'Area': [area]}
                df0 = pd.DataFrame(data, columns=['Centrex', 'Centrey', 'z', 'ROIName', 'ROINumber', 'ROIContourNumber',
                                                  'Area'])
                AreaDf = pd.concat([AreaDf, df0], ignore_index=True)
    return AreaDf
