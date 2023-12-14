import os
import sys
import time
import numpy as np
import skimage.io
import skimage.filters
import skimage.morphology

from csbdeep.utils import normalize


def preprocess(img0):
    # Takes ~ 1.2 sec
    img1 = skimage.filters.gaussian(img0, sigma=2)
    back = skimage.filters.gaussian(img1, sigma=50, mode='nearest', preserve_range=True)
    img2 = img1 / back
    return img2


def segment_nuclei(image_file, output_files, verbose, debug, model):

    bpath = os.path.basename(image_file)
    if verbose:
        print(">> Processing image: %s" % bpath)

    # load image
    img0 = skimage.io.imread(image_file, plugin='tifffile')

    # Check image condition: Blurry? Very few cells? Empty? Large artefacts?
    # This sounds like a CNN classification ..

    # pre-processing
    t1 = time.time()
    img = preprocess(img0)
    t2 = time.time()
    if debug:
        print("time for preprocessing:", t2-t1)

    # segment with pretrained model
    labels, _ = model.predict_instances( normalize(img), predict_kwargs=dict(verbose=False) )
    t3 = time.time()
    if debug:
        print("time for segmentation:", t3-t2)

    # thresholds on object properties
    min_vol = 300
    max_vol = 15000
    remove_small=True
    remove_large=True
    color_by_volume=False

    unique_labels, unique_counts = np.unique(labels, return_counts=True)
    Nlabels = np.shape(unique_labels)[0]
    if verbose:
        print("Detected %d labels" % Nlabels)

    if color_by_volume==True:
        labels1 = np.zeros(np.shape(labels))

    for i in range(1,Nlabels):
        Vol = unique_counts[i]

        if remove_small==True:
            if Vol<min_vol:
                idx = (labels==unique_labels[i])
                labels[idx] = 0
        if remove_large==True:
            if Vol>max_vol:
                idx = (labels==unique_labels[i])
                labels[idx] = 0

        if color_by_volume==True:
            idx = (labels==unique_labels[i])
            labels1[idx] = Vol

    if (remove_small==True or remove_large==True) and verbose:
        print("After removal of small/large objects, Nlabels=", np.shape(np.unique(labels))[0])
    if color_by_volume==True:
        labels[:,:] = labels1[:,:]

    # find edges
    edges0 = skimage.filters.sobel(labels)
    edges = np.zeros(np.shape(edges0), dtype=np.dtype(np.uint8))
    edges[edges0>0] = 1
    fat_edges = skimage.morphology.binary_dilation(edges)

    # create boarders between labeled objects
    objects = np.zeros(np.shape(edges0), dtype=np.dtype(np.uint16))
    objects[:,:] = labels[:,:]
    objects[fat_edges==1] = 0

    skimage.io.imsave(output_files["alllabels"], objects, plugin='tifffile', check_contrast=False)

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

    # store split object mask
    mask = np.zeros(np.shape(objects), dtype=np.dtype(np.uint8))
    mask[objects>0] = 1
    skimage.io.imsave(output_files["seeds"], mask, plugin='tifffile', check_contrast=False)

    t4 = time.time()
    if debug:
        print("time after segmentation:", t4-t3)

    Nnuclei = len(np.unique(objects))

    # # reconstruct edges from nuclei seeds
    # edges0 = skimage.filters.sobel(mask)
    # edges = np.zeros(np.shape(edges0), dtype=np.dtype(np.uint8))
    # edges[edges0>0] = 1

    # # overlay edges and original image
    # composite = np.zeros( (2, np.shape(objects)[1], np.shape(objects)[0]), dtype=np.dtype(np.uint16))
    # composite[0,:,:] = img2[:,:]
    # composite[1,:,:] = edges[:,:]
    # skimage.io.imsave("%s/%s_composite_edges.tif" % (opath, bpath), composite, plugin='tifffile', check_contrast=False)



#    # WIP:
#    def segment_nuclei_CellProfiler(image_file, verbose):
#
#        bpath = os.path.basename(image_file)
#        if verbose:
#            print(">> Processing image: %s" % bpath)
#
#        # load image
#        img0 = skimage.io.imread(image_file, plugin='tifffile')
#
#
#        """
#        CellProfiler pipeline:
#        1. Compute thresholds (Global threshold, Minimum Cross Entropy)
#        2. 
#        """





