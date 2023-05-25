import os
import sys
import numpy as np
import argparse
import skimage.io
import skimage.filters
import skimage.morphology
from skimage import restoration
from stardist.models import StarDist2D

parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, required=True, nargs='+', help="2D tif images")
args = parser.parse_args()


for image_file in args.i:

    print(">> Processing image: %s" % os.path.basename(image_file))

    # load input nuclei image
    img0 = skimage.io.imread(image_file, plugin='tifffile')

    # background subtraction
    background = restoration.rolling_ball(img0, radius=50)
    img1 = img0 - background

    # CLAHE: skimage.exposure.equalize_adapthist(..)

    # smoothing
    img = skimage.filters.gaussian(img1, sigma=3)

    # create a pretrained model
    model = StarDist2D.from_pretrained('2D_versatile_fluo')

    # predict objects
    from csbdeep.utils import normalize
    labels, _ = model.predict_instances(normalize(img))

    # threshold on object properties
    min_vol = 300
    max_vol = 5000
    remove_small=True
    remove_large=False
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
    opath = "%s/output_V0.0" % os.path.dirname(image_file)
    bpath = os.path.basename(image_file)
    if not os.path.exists(opath):
        os.makedirs(opath)
    skimage.io.imsave("%s/%s_labels_nuclei.tif" % (opath, bpath), labels, plugin='tifffile')


    # Find edges
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

    # store split objects
    skimage.io.imsave("%s/%s_seeds nuclei.tif" % (opath, bpath), objects, plugin='tifffile')

    # overlay edges and original image
    composite = np.zeros(np.shape(objects), dtype=np.dtype(np.uint16))
    composite[:,:] = img1[:,:]
    composite[fat_edges==1] = 65535
    skimage.io.imsave("%s/%s_overlay_edges.tif" % (opath, bpath), composite, plugin='tifffile')

    sys.exit()

