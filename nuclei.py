import os
import sys
import numpy as np
import argparse
import skimage.io
from stardist.models import StarDist2D
import matplotlib.pyplot as plt


parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, required=True, help="tif 2D image")
parser.add_argument('-o', type=str, required=True, help="output tif path (labeled objects)")
args = parser.parse_args()


# load input nuclei image
img = skimage.io.imread(args.i, plugin='tifffile').T

# create a pretrained model
model = StarDist2D.from_pretrained('2D_versatile_fluo')

# predict objects
from csbdeep.utils import normalize
labels, _ = model.predict_instances(normalize(img))

# plot image and object predictions
if 0:
    from stardist.plot import render_label
    # original nuclei image
    plt.subplot(1,2,1)
    plt.imshow(img, cmap="gray")
    plt.axis("off")
    plt.title("input image")
    # labeled objects image
    plt.subplot(1,2,2)
    plt.imshow(render_label(labels, img=img))
    plt.axis("off")
    plt.title("prediction + input overlay")
    plt.show()

# save 
skimage.io.imsave(args.o, labels, plugin='tifffile')

