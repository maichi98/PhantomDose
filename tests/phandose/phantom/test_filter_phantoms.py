from phandose.phantom.filter_phantoms import PhantomFilter

from pathlib import Path
import pandas as pd
import numpy as np
import unittest


class TestPhantomFilter(unittest.TestCase):
    def setUp(self):
        self.dir_sample_patient_data = Path(__file__).parent.parent.parent / 'sample_data' / "AGORL_P33"

    def test_filter_by_sex_and_position(self):
        pass
