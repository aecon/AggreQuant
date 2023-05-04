import os
import sys
import numpy as np
import argparse
import skimage.io
from stardist.models import StarDist2D


parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, required=True, nargs='+', help="tif 2D image")
args = parser.parse_args()


for image_file in args.i:

    # load input nuclei image
    img = skimage.io.imread(image_file, plugin='tifffile')


    # create a pretrained model
    model = StarDist2D.from_pretrained('2D_versatile_fluo')


    # predict objects
    from csbdeep.utils import normalize
    labels, _ = model.predict_instances(normalize(img))


    # threshold on object properties
    min_vol = 100
    remove_small=True
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

        if color_by_volume==True:
            idx = (labels==unique_labels[i])
            labels1[idx] = Vol

    if remove_small==True:
        print("After removal of small objects, Nlabels=", np.shape(np.unique(labels))[0])
    if color_by_volume==True:
        labels[:,:] = labels1[:,:]


    # save 
    opath = "%s/out_labels" % os.path.dirname(image_file)
    bpath = os.path.basename(image_file)
    if not os.path.exists(opath):
        os.makedirs(opath)
    skimage.io.imsave("%s/%s_labels_nuclei_Vol%d.tif" % (opath, bpath, min_vol), labels, plugin='tifffile')

