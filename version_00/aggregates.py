import os
import sys
import numpy as np
import skimage.io
import skimage.filters
import scipy.ndimage
import matplotlib.pyplot as plt

from filenames import Filenames
from diagnostics import Diagnostics


def segment_intensity_map(image_file, cells_file, opath, Names):

    # load input image
    img = skimage.io.imread(image_file, plugin='tifffile')
    print(np.median(img), np.min(img), np.max(img))

    # cap values
    threshold = np.percentile(img, 98)
    print("threshold:", threshold)
    capped = np.zeros(np.shape(img))
    capped[:,:] = img[:,:]
    capped[img>threshold] = threshold
    #plt.imshow(capped)
    #plt.show()

    # background division
    back = scipy.ndimage.gaussian_filter(capped, sigma=100, mode='reflect')
    print(np.median(back), np.min(back), np.max(back))
    #plt.imshow(back)
    #plt.show()

    # normalized
    norm = img / back
    assert(np.min(norm)>=0)
    #plt.imshow(norm)
    #plt.show()

    # segment
    threshold = np.percentile(norm, 98)
    segmented_ = np.zeros(np.shape(img), dtype=np.uint8)
    segmented_[norm>threshold] = 1
    print("seg. threshold:", threshold)
    #plt.imshow(segmented_)
    #plt.show()

    # median
    segmented = scipy.ndimage.median_filter(segmented_, size=2)

    # connected components
    labels = skimage.morphology.label(segmented, connectivity=2)
    print("Connected cmoponents (original):", np.max(labels))
    #plt.imshow(labels)
    #plt.show()

    # remove small holes
    noholes = skimage.morphology.remove_small_holes(segmented, area_threshold=400, connectivity=2)
    #plt.imshow(noholes)
    #plt.show()
    labels = skimage.morphology.label(noholes, connectivity=2)
    print("Removed small holes:", np.max(labels))
    #plt.imshow(labels)
    #plt.show()

    # remove small objects
    nosmall = skimage.morphology.remove_small_objects(labels, min_size=9, connectivity=2)
    labels = skimage.morphology.label(nosmall, connectivity=2)
    print("Removed small objects:", np.max(labels))
    obj = np.max(labels)
    #plt.imshow(labels)
    #plt.show()

    # save 
    bpath = os.path.basename(image_file)
    labels = np.asarray(labels, dtype=np.uint32)
    assert(np.max(labels) == obj)
    skimage.io.imsave("%s/%s_labels_aggregates.tif" % (opath, bpath), labels, plugin='tifffile')



def segment_ilastik():
    print("TODO.")
    assert(0)



def aggregate_segmentation(aggregate_images, Names):

    segmentation_algorithm = Names.AGGREGATE_SEGMENTATION_TYPE
    print("Segmenting aggregates with algorithm:", segmentation_algorithm)

    for ifile, image_file in enumerate(aggregate_images):

        bpath = os.path.basename(image_file)
        print(">> Processing image: %s" % bpath)

        # find corresponding cellbodies
        cells_file = "%s/%s/%s/%s%s).tif_cellbodies_labels.tif" % ( Names.OUTDIR_PATH, Names.OUTDIR, Names.CELLBODY_ODIR_NAME, bpath.split(Names.COLOR_AGGREGATES,1)[0], Names.COLOR_CELLS)
        if not os.path.isfile(cells_file):
            print("Cellbody labels for file %s do NOT exist!", bpath)
            sys.exit()

        # Output folder for aggregate segmentation
        opath = "%s/%s/%s" % ( Names.OUTDIR_PATH, Names.OUTDIR, Names.AGGREGATE_ODIR_NAME)
        if not os.path.exists(opath):
            print("Path %s does NOT exist. Creating now. " % opath)
            os.makedirs(opath)
        else:
            print("Path %s exists." % opath)

        # Choose segmentation algorithm for aggregates
        if segmentation_algorithm == "intensity":
            segment_intensity_map(image_file, cells_file, opath, Names)

        elif segmentation_algorithm == "ilastik":
            segment_ilastik()

        else:
            print("Segmentation algorithm %s not defined." % segmentation_algorithm)
            sys.exit()

