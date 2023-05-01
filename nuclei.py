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
    
    # plot image and object predictions
    if 0:
        import matplotlib.pyplot as plt
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
    opath = "%s/out_labels" % os.path.dirname(image_file)
    bpath = os.path.basename(image_file)
    if not os.path.exists(opath):
        os.makedirs(opath)
    skimage.io.imsave("%s/%s_labels.tif" % (opath, bpath), labels, plugin='tifffile')

