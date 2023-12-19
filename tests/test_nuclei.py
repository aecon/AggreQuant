import sys
import os
# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add the parent directory (processing) to the Python path
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)

import unittest
import numpy as np
from processing import nuclei
from stardist.models import StarDist2D


class TestNuclei(unittest.TestCase):

    def test_load(self):
        f = "data/Plate_HA13rep1_K - 13(fld 3 wv 390 - Blue).tif"
        d = nuclei._load_image(f)
        r = np.sum(d)
        self.assertEqual(r,738293912)

    def test_preprocess(self):
        f = "data/Plate_HA13rep1_K - 13(fld 3 wv 390 - Blue).tif"
        d = nuclei._load_image(f)
        p = nuclei._pre_process(d)
        r = int(np.max(p)*1000)
        self.assertEqual(r,7055)

#    def test_segmentStarDist(self):
#        f = "data/Plate_HA13rep1_K - 13(fld 3 wv 390 - Blue).tif"
#        d = nuclei._load_image(f)
#        model = StarDist2D.from_pretrained('2D_versatile_fluo')
#        labels = nuclei._segment_stardist(d, model)
#        N = np.unique(labels)
#        self.assertEqual(r,100)

#    def test_size_exclusion(self):
#        f = "data/Plate_HA13rep1_K - 13(fld 3 wv 390 - Blue).tif"
#        d = nuclei._load_image(f)
#        m = np.median(d)
#        d[d<m]=0
#        d[d>=m]=1
    

if __name__ == '__main__':
    unittest.main()

