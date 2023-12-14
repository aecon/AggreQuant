import sys
import os
# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add the parent directory (processing) to the Python path
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)


import unittest
import numpy as np
from processing.nuclei import NucleiSegmentation
from processing.dataset import Dataset


class TestNucleiSegmentation(unittest.TestCase):

    def test_segmentation(self):
        data_n = "data/Plate_HA13rep1_K - 13(fld 3 wv 390 - Blue).tif"
        data_a = "data/Plate_HA13rep1_K - 13(fld 3 wv 473 - Green2).tif"
        data_c = "data/Plate_HA13rep1_K - 13(fld 3 wv 631 - FarRed).tif"

        dataset = Dataset(data_n, data_c, data_a, fileParser.input_directory, self.overwrite_output_folder)
        output_files_nuclei = dataset.get_output_file_names(self.data.n, "nuclei")

        NucleiModel = 
        verbose = False
        debug = False
        nuclei = NucleiSegmentation(data_n, output_files_nuclei, NucleiModel, verbose, debug)
        Number_of_nuclei = nuclei.segment_nuclei()

        self.assertEqual(Number_of_nuclei, 500)


if __name__ == '__main__':
    unittest.main()

