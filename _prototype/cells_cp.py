"""
https://github.com/MouseLand/cellpose/blob/main/notebooks/Cellpose_cell_segmentation_2D_prediction_only.ipynb
"""
import os
import sys
import argparse
import skimage.io
import numpy as np
import matplotlib.pyplot as plt

from cellpose import core
from cellpose import plot
from cellpose import models
from cellpose.io import imread


parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, required=True, nargs='+', help="tif 2D image")
args = parser.parse_args()

for image_file in args.i:
    # load input image
    img = skimage.io.imread(image_file, plugin='tifffile')

    # GPU activated?
    use_GPU = core.use_gpu()
    print('>>> GPU activated? %d'%use_GPU)

    # call logger_setup to have output of cellpose written
    from cellpose.io import logger_setup
    logger_setup();

    # DEFINE CELLPOSE MODEL
    Model_Choice = "cyto2" # ["cyto", "nuclei", "cyto2", "tissuenet", "livecell"]
    model = models.Cellpose(gpu=use_GPU, model_type=Model_Choice)

    # define CHANNELS to run segementation on
    # grayscale=0, R=1, G=2, B=3
    # channels = [cytoplasm, nucleus]
    # if NUCLEUS channel does not exist, set the second channel to 0
    # channels = [0,0]
    # IF ALL YOUR IMAGES ARE THE SAME TYPE, you can give a list with 2 elements
    # channels = [0,0] # IF YOU HAVE GRAYSCALE
    # channels = [2,3] # IF YOU HAVE G=cytoplasm and B=nucleus
    # channels = [2,1] # IF YOU HAVE G=cytoplasm and R=nucleus
    # or if you have different types of channels in each image
    cytoplasm_channel = int(1)
    nuclear_channel = int(2)
    channels = [cytoplasm_channel, nuclear_channel]

    # if diameter is set to None, the size of the cells is estimated on a per image basis
    # you can set the average cell `diameter` in pixels yourself (recommended) 
    # diameter can be a list or a single number for all images

    masks, flows, styles, diams = model.eval(img, diameter=None, flow_threshold=0.6, cellprob_threshold=0, channels=channels)



# all options: masks, flows, styles, diams = model.eval(img1, diameter=diameter, flow_threshold=flow_threshold,cellprob_threshold=cellprob_threshold, channels=channels)



    # DISPLAY RESULTS
    maski = masks
    flowi = flows[0]
    
    fig = plt.figure(figsize=(12,5))
    plot.show_segmentation(fig, img, maski, flowi, channels=channels)
    plt.tight_layout()
    plt.show()


#    # save 
#    opath = "%s/out_labels" % os.path.dirname(image_file)
#    bpath = os.path.basename(image_file)
#    if not os.path.exists(opath):
#        os.makedirs(opath)
#    labels = np.asarray(masks, dtype=np.uint32)
#    skimage.io.imsave("%s/%s_labels_cells_CP.tif" % (opath, bpath), labels, plugin='tifffile')
#
