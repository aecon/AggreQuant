import os
import sys
import numpy as np
import argparse
import skimage.io
import skimage.filters
import scipy.ndimage


parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, required=True, nargs='+', help="tif 2D image")
args = parser.parse_args()


for image_file in args.i:
    # load input image
    img = skimage.io.imread(image_file, plugin='tifffile')

    # background subtraction
    back = scipy.ndimage.gaussian_filter(img, sigma=100, mode='reflect')

    # normalized
    norm = img / back
    assert(np.min(norm)>=0)

    # segmented (binary mask)
    threshold = skimage.filters.threshold_li(norm) 
    segmented_ = np.zeros(np.shape(img), dtype=np.uint8)
    segmented_[norm>threshold] = 1

    # median
    segmented = scipy.ndimage.median_filter(segmented_, size=2)

    # connected components
    labels = skimage.morphology.label(segmented, connectivity=2)
    print("Connected cmoponents (original):", np.max(labels))

    # remove small holes
    noholes = skimage.morphology.remove_small_holes(segmented, area_threshold=5*5, connectivity=2)
    labels = skimage.morphology.label(noholes, connectivity=2)
    print("Removed small holes:", np.max(labels))

    # remove small objects
    nosmall = skimage.morphology.remove_small_objects(labels, min_size=20*20, connectivity=2)
    labels = skimage.morphology.label(nosmall, connectivity=2)
    print("Removed small objects:", np.max(labels))
    obj = np.max(labels)

    # save 
    opath = "%s/out_labels" % os.path.dirname(image_file)
    bpath = os.path.basename(image_file)
    if not os.path.exists(opath):
        os.makedirs(opath)
    labels = np.asarray(labels, dtype=np.uint32)
    assert(np.max(labels) == obj)
    skimage.io.imsave("%s/%s_labels_cells.tif" % (opath, bpath), labels, plugin='tifffile')

