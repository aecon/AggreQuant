import os
import sys
import numpy as np
import argparse
import skimage.io
import skimage.filters
import skimage.morphology
from skimage import restoration
from stardist.models import StarDist2D
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, required=True, nargs='+', help="2D tif images")
parser.add_argument('-o', type=str, required=True, help="output directory name")
args = parser.parse_args()


for image_file in args.i:

    print(">> Processing image: %s" % os.path.basename(image_file))

    # load input nuclei image
    img0 = skimage.io.imread(image_file, plugin='tifffile')

    # background subtraction
    background = restoration.rolling_ball(img0, radius=50)
    img1 = img0 - background

    img2 = skimage.exposure.equalize_adapthist(img1, kernel_size=150)
    print(img2.dtype, np.min(img2), np.max(img2))
    rescale_range = np.max(img2) - np.min(img2)
    Max_uint16 = 65535
    img2_ = (img2-np.min(img2)) / (np.max(img2) - np.min(img2))
    img2_ = img2_*Max_uint16
    img2 = np.asarray(img2_, dtype=np.dtype(np.uint16))

    # smoothing
    img = skimage.filters.gaussian(img2, sigma=3)

    # create a pretrained model
    model = StarDist2D.from_pretrained('2D_versatile_fluo')

    # predict objects
    from csbdeep.utils import normalize
    labels, _ = model.predict_instances(normalize(img))

    # threshold on object properties
    min_vol = 300
    max_vol = 15000
    remove_small=True
    remove_large=True
    color_by_volume=False

    unique_labels, unique_counts = np.unique(labels, return_counts=True)
    Nlabels = np.shape(unique_labels)[0]
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

    if remove_small==True or remove_large==True:
        print("After removal of small/large objects, Nlabels=", np.shape(np.unique(labels))[0])
    if color_by_volume==True:
        labels[:,:] = labels1[:,:]

    # save segmented nuclei
    opath = "%s/%s/nuclei" % ( os.path.dirname(image_file), args.o )
    bpath = os.path.basename(image_file)
    if not os.path.exists(opath):
        os.makedirs(opath)
    skimage.io.imsave("%s/%s_labels_StarDist.tif" % (opath, bpath), labels, plugin='tifffile')

    # find edges
    edges0 = skimage.filters.sobel(labels)
    edges = np.zeros(np.shape(edges0), dtype=np.dtype(np.uint8))
    edges[edges0>0] = 1
    fat_edges = skimage.morphology.binary_dilation(edges)

    # create boarders between labeled objects
    objects = np.zeros(np.shape(edges0), dtype=np.dtype(np.uint16))
    objects[:,:] = labels[:,:]
    objects[fat_edges==1] = 0

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
    skimage.io.imsave("%s/%s_seeds_nuclei.tif" % (opath, bpath), mask, plugin='tifffile')

    # reconstruct edges from nuclei seeds
    edges0 = skimage.filters.sobel(mask)
    edges = np.zeros(np.shape(edges0), dtype=np.dtype(np.uint8))
    edges[edges0>0] = 1

    # overlay edges and original image
    composite = np.zeros( (2, np.shape(objects)[1], np.shape(objects)[0]), dtype=np.dtype(np.uint16))
    composite[0,:,:] = img2[:,:]
    composite[1,:,:] = edges[:,:]
    skimage.io.imsave("%s/%s_composite_edges.tif" % (opath, bpath), composite, plugin='tifffile')

