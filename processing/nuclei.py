import os
import sys
import time
import numpy as np
import skimage.io
import skimage.filters
import skimage.morphology

from csbdeep.utils import normalize
from processing import image_functions as IF

verbose = False
debug = False


# list of parameters
# - pre process
sigma_denoise = 2
sigma_background = 50


def _pre_process(img0):
    """
    Input:
        The original image (I)
    Output:
        The normalized image (In), where:
        * In = G(s=2) / G(s=50), and
        * G(s=a) is the result of the convolution of the original image
          with a Gaussian filter with standard deviation, sigma=a. 
    """
    # takes ~1.2 sec
    img1 = skimage.filters.gaussian(img0, sigma=sigma_denoise)
    back = skimage.filters.gaussian(
        img1, sigma=sigma_background, mode='nearest', preserve_range=True)
    img = img1 / back
    return img


def _segment_stardist(img, model):
    """
    Segment nuclei using the pre-trained DNN model StarDist
    Input:
        Pre-processed image
    Output:
        Instance segmentation, with a unique label-ID per nucleus
    """
    labels, _ = model.predict_instances(
        normalize(img), predict_kwargs=dict(verbose=False) )
    return labels


def _post_process_size_exclusion(labels, min_area, max_area):
    # thresholds on object properties
    remove_small=True
    remove_large=True
#    color_by_volume=False

    # get number of detected objects
    unique_labels, unique_counts = np.unique(labels, return_counts=True)
    Nlabels = np.shape(unique_labels)[0]
    if verbose:
        print("Detected %d labels" % Nlabels)

#    if color_by_volume==True:
#        labels1 = np.zeros(np.shape(labels))

    # exclude non-cells based on thresholds
    for i in range(1,Nlabels):
        Vol = unique_counts[i]
        if remove_small==True:
            if Vol<min_area:
                idx = (labels==unique_labels[i])
                labels[idx] = 0
        if remove_large==True:
            if Vol>max_area:
                idx = (labels==unique_labels[i])
                labels[idx] = 0
#        if color_by_volume==True:
#            idx = (labels==unique_labels[i])
#            labels1[idx] = Vol

    # print number of cells after size exlcusion
    if (remove_small==True or remove_large==True) and verbose:
        print("After removal of small/large objects, Nlabels=", np.shape(
            np.unique(labels))[0])
#    if color_by_volume==True:
#        labels[:,:] = labels1[:,:]

    return labels


def _post_process_increase_cell_borders(labels):
    # find edges
    edges0 = skimage.filters.sobel(labels)
    edges = np.zeros(np.shape(edges0), dtype=np.dtype(np.uint8))
    edges[edges0>0] = 1
    fat_edges = skimage.morphology.binary_dilation(edges)

    # create boarders between labeled objects
    objects = np.zeros(np.shape(edges0), dtype=np.dtype(np.uint16))
    objects[:,:] = labels[:,:]
    objects[fat_edges==1] = 0

    return objects


def _save_labels(objects, output_path):
    skimage.io.imsave(
        output_path, objects, plugin='tifffile',check_contrast=False)


def _border_exclusion(objects):
     # exclude nuclei on the borders
    edge_labels = np.unique(objects[0,:])
    for j in edge_labels:
        objects[objects==j] = 0
    edge_labels = np.unique(objects[-1,:])
    for j in edge_labels:
        objects[objects==j] = 0
    edge_labels = np.unique(objects[:,0])
    for j in edge_labels:
        objects[objects==j] = 0
    edge_labels = np.unique(objects[:,-1])
    for j in edge_labels:
        objects[objects==j] = 0
    return objects


def _save_mask(objects, output_path):
    # store split object mask
    mask = np.zeros(np.shape(objects), dtype=np.dtype(np.uint8))
    mask[objects>0] = 1
    skimage.io.imsave(
        output_path, mask, plugin='tifffile', check_contrast=False)


def segment_method_stardist(model, image_file, output_files, _verbose, _debug, min_area=300, max_area=15000):
    """
    Segmentation of images with nuclei.

    Input:
        - Stardist pre-trained model
        - path to input image
        - paths to outputs

    Output:
        - seed mask
        - all labels
    """

    verbose = _verbose
    debug = _debug

    img0 = IF.load_image(image_file, verbose)

    # pre-processing
    img = _pre_process(img0)

    # segmentation
    labels = _segment_stardist(img, model)

    # post-processing
    labels = _post_process_size_exclusion(labels, min_area, max_area)
    objects = _post_process_increase_cell_borders(labels)

    # save ALL labels
    _save_labels(objects, output_files["alllabels"])
 
    # exclude cells on borders and save mask
    objects = _border_exclusion(objects)
    _save_mask(objects, output_files["seeds"])


# TODO
def segment_method_cellpose(image_file, verbose):
    """
    Use Cellpose for nuclei detection
    """
    print("UNDER DEVELOPMENT")
    assert(0)

