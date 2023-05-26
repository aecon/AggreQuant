import os
import sys
import numpy as np
import argparse
import skimage.io
import skimage.filters
import skimage.morphology
from skimage import restoration
import matplotlib.pyplot as plt

from filenames import Filenames
from diagnostics import Diagnostics


# not needed ..
# parser = argparse.ArgumentParser()
# parser.add_argument('-i', type=str, required=True, nargs='+', help="2D tif images")
# parser.add_argument('-o', type=str, required=True, help="output directory name")
# args = parser.parse_args()


def segment_cellpose():
    nuclei_paths = ""
    for f in images_nuclei:
        nuclei_paths+=" '%s'" % f
    os.system( "conda run -n cellpose python cells_cp.py -o %s -i %s" % (Names.OUTDIR, nuclei_paths) ) ### CHECK THE PATHS !!!!



def segment_distance_map():
    print("TODO")


def segment_intensity_map():
    print("TODO")


def segment_propagation():
    print("TODO")


def cellbody_segmentation(cellbody_images, Names)

    opath = "%s/%s" % ( Names.OUTDIR_PATH, Names.OUTDIR)
    if not os.path.exists(opath):
        print("Path %s does NOT exist. Creating now. " % opath)
        os.makedirs(opath)
    else:
        print("Path %s exists." % opath)

    for ifile, image_file in enumerate(cellbody_images):
        bpath = os.path.basename(image_file)
    
        # Loop over cell body images
        # apply one of the segmentation methods to each image


