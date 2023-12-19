import os
import sys
import numpy as np
import skimage.io
import skimage.filters
import scipy.ndimage
import tifffile



def segment_aggregates(image_file, output_files_aggregates, verbose, debug):

    # load image
    img = skimage.io.imread(image_file, plugin='tifffile')
    if debug:
        print(np.median(img), np.min(img), np.max(img))

    # cap values
    threshold = 3500 #based on visual inspection of many images #np.percentile(img, 98)
    if debug:
        print("threshold:", threshold)
    capped = np.zeros(np.shape(img))
    capped[:,:] = img[:,:]
    capped[img>threshold] = threshold

    # background division
    back = scipy.ndimage.gaussian_filter(capped, sigma=20, mode='reflect')
    if debug:
        print(np.median(back), np.min(back), np.max(back))

    # normalized
    norm = img / back
    assert(np.min(norm)>=0)

    # noise reduction: same as Cellprofiler pipeline
    tmp_ = scipy.ndimage.gaussian_filter(norm, sigma=1, mode='reflect') 
    norm[:,:] = tmp_[:,:]

    # segment
    threshold = 1.60 #based on visual inspection #max(np.percentile(norm, 98), 1.08)
    segmented_ = np.zeros(np.shape(img), dtype=np.uint8)
    segmented_[norm>threshold] = 1
    if debug:
        print("seg. threshold:", threshold)

    # median
    segmented = scipy.ndimage.median_filter(segmented_, size=4)

    # connected components
    labels = skimage.morphology.label(segmented, connectivity=2)
    if debug:
        print("Connected cmoponents (original):", np.max(labels))

    # remove small holes
    Amin_hole = 6000
    noholes = skimage.morphology.remove_small_holes(segmented.astype(bool, copy=True), area_threshold=Amin_hole, connectivity=2)
    labels = skimage.morphology.label(noholes, connectivity=2)
    if debug:
        print("Removed small holes:", np.max(labels))

    # remove small objects
    nosmall = skimage.morphology.remove_small_objects(labels, min_size=9, connectivity=2)
    labels = skimage.morphology.label(nosmall, connectivity=2)
    if debug:
        print("Removed small objects:", np.max(labels))
    obj = np.max(labels)

    # save connected components
    labels = np.asarray(labels, dtype=np.uint32)
    assert(np.max(labels) == obj)
    skimage.io.imsave(output_files_aggregates["alllabels"], labels, plugin='tifffile', check_contrast=False)


