from phandose.phantom import PhantomLibrary
from phandose import constants

from unittest.mock import patch
import pandas as pd
import unittest


class TestPhantomLibrary(unittest.TestCase):

    def setUp(self):
        self.phantom_library = PhantomLibrary(constants.DIR_PHANTOM_LIBRARY)
        self.existing_phantom_name = "_FFDL_M_ 201919998LF_.txt"

    @patch("pandas.read_csv")
    def test_get_phantom_when_phantom_exists(self, mock_read_csv):
        mock_read_csv.return_value = pd.DataFrame()
        result = self.phantom_library.get_phantom(self.existing_phantom_name)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(mock_read_csv.called)

    def test_get_phantom_when_phantom_does_not_exist(self):
        with self.assertRaises(FileNotFoundError):
            self.phantom_library.get_phantom("non_existing_phantom")

    @patch("pandas.DataFrame.to_csv")
    def test_add_phantom_when_phantom_does_not_exist(self, mock_to_csv):
        df_phantom = pd.DataFrame()
        self.phantom_library.add_phantom(df_phantom, "new_phantom")
        mock_to_csv.assert_called_once()

    def test_add_phantom_when_phantom_already_exists(self):
        df_phantom = pd.DataFrame()
        with self.assertRaises(FileExistsError):
            self.phantom_library.add_phantom(df_phantom, self.existing_phantom_name)

    def test_get_phantom_dataframe(self):
        result = self.phantom_library.get_phantom_dataframe()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(result.columns.tolist(), ['Phantom', 'Position', 'Sex'])


if __name__ == "__main__":
    unittest.main()
