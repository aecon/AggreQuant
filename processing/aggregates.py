import os
import sys
import numpy as np
import skimage.io
import skimage.filters
import scipy.ndimage
import tifffile


# Image segmentation parameters

median_filter_size = 4      # applied after segmentation to regularize shape
sigma_noise_reduction = 1   # applied on normalized data to reduce digitization noise
sigma_background = 20       # used to generate a model of background illumination
intensity_cap=3500          # used to cap intensity for background estimation
normalized_intensity_threshold=1.60 # threshold on normalized intensity to generate segmentation
small_hole_area_threshold=6000 # fill holes in segmented data that are smaller than this threshold
min_aggreagte_area=9        # ignore segmented objects smaller than this threshold


def segment_aggregates(image_file, output_files_aggregates, verbose, debug):

    # load image
    img = skimage.io.imread(image_file, plugin='tifffile')
    if debug:
        print(np.median(img), np.min(img), np.max(img))

    # cap intensity values only for background intensity estimation
    threshold = intensity_cap  #np.percentile(img, 98)
    if debug:
        print("threshold:", threshold)
    capped = np.zeros(np.shape(img))
    capped[:,:] = img[:,:]
    capped[img>threshold] = threshold

    # background estimation
    back = scipy.ndimage.gaussian_filter(capped, sigma=sigma_background, mode='reflect')
    if debug:
        print(np.median(back), np.min(back), np.max(back))

    # normalized image
    norm = img / back
    assert(np.min(norm)>=0)

    # noise reduction of normalized image
    tmp_ = scipy.ndimage.gaussian_filter(norm, sigma=sigma_noise_reduction, mode='reflect') 
    norm[:,:] = tmp_[:,:]

    # segment
    threshold = normalized_intensity_threshold #max(np.percentile(norm, 98), 1.08)
    segmented_ = np.zeros(np.shape(img), dtype=np.uint8)
    segmented_[norm>threshold] = 1
    if debug:
        print("seg. threshold:", threshold)

    # median
    segmented = scipy.ndimage.median_filter(segmented_, size=median_filter_size)

    # connected components
    labels = skimage.morphology.label(segmented, connectivity=2)
    if debug:
        print("Connected cmoponents (original):", np.max(labels))

    # remove small holes
    Amin_hole = small_hole_area_threshold
    noholes = skimage.morphology.remove_small_holes(segmented.astype(bool, copy=True), area_threshold=Amin_hole, connectivity=2)
    labels = skimage.morphology.label(noholes, connectivity=2)
    if debug:
        print("Removed small holes:", np.max(labels))

    # remove small objects
    nosmall = skimage.morphology.remove_small_objects(labels, min_size=min_aggreagte_area, connectivity=2)
    labels = skimage.morphology.label(nosmall, connectivity=2)
    if debug:
        print("Removed small objects:", np.max(labels))
    obj = np.max(labels)

    # save connected components
    labels = np.asarray(labels, dtype=np.uint32)
    assert(np.max(labels) == obj)
    skimage.io.imsave(output_files_aggregates["alllabels"], labels, plugin='tifffile', check_contrast=False)


