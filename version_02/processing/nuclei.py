import os
import sys
import time
import numpy as np
import skimage.io
import skimage.filters
import skimage.morphology
from skimage import restoration

from stardist.models import StarDist2D
from csbdeep.utils import normalize

import matplotlib.pyplot as plt


class NucleiSegmentation:

    def __init__(self, name_nuclei_seeds, name_nuclei_alllabels, verbose, debug):
        self.verbose = verbose
        self.debug = debug
        self.name_nuclei_seeds = name_nuclei_seeds
        self.name_nuclei_alllabels = name_nuclei_alllabels
        if verbose:
            print("Segmenting nuclei")


    def _preprocess(self, img0):
        # Takes ~ 1.2 sec
        img1 = skimage.filters.gaussian(img0, sigma=2)
        back = skimage.filters.gaussian(img1, sigma=50, mode='nearest', preserve_range=True)
        img2 = img1 / back
        return img2


    def segment_nuclei(self, image_file, opath):

        if not os.path.exists(opath):
            print("Output directory does NOT exist! %s" % opath)
            sys.exit()

        bpath = os.path.basename(image_file)
        if self.verbose:
            print(">> Processing image: %s" % bpath)

        # load image
        img0 = skimage.io.imread(image_file, plugin='tifffile')

        # pre-processing
        t1 = time.time()
        img = self._preprocess(img0)
        t2 = time.time()
        if self.debug:
            print("time for preprocessing:", t2-t1)

        # segment with pretrained model
        model = StarDist2D.from_pretrained('2D_versatile_fluo')
        labels, _ = model.predict_instances( normalize(img), predict_kwargs=dict(verbose=False) )
        t3 = time.time()
        if self.debug:
            print("time for segmentation:", t3-t2)

        # thresholds on object properties
        min_vol = 300
        max_vol = 15000
        remove_small=True
        remove_large=True
        color_by_volume=False

        unique_labels, unique_counts = np.unique(labels, return_counts=True)
        Nlabels = np.shape(unique_labels)[0]
        if self.verbose:
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

        if (remove_small==True or remove_large==True) and self.verbose:
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

        filename_all_nuclei = "%s/%s_%s.tif" % (opath, bpath, self.name_nuclei_alllabels)
        skimage.io.imsave(filename_all_nuclei, objects, plugin='tifffile', check_contrast=False)

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
        filename_seeds = "%s/%s_%s.tif" % (opath, bpath, self.name_nuclei_seeds)
        skimage.io.imsave(filename_seeds, mask, plugin='tifffile', check_contrast=False)

        t4 = time.time()
        if self.debug:
            print("time after segmentation:", t4-t3)

        return filename_seeds, filename_all_nuclei



#        # reconstruct edges from nuclei seeds
#        edges0 = skimage.filters.sobel(mask)
#        edges = np.zeros(np.shape(edges0), dtype=np.dtype(np.uint8))
#        edges[edges0>0] = 1
#
#        # overlay edges and original image
#        composite = np.zeros( (2, np.shape(objects)[1], np.shape(objects)[0]), dtype=np.dtype(np.uint16))
#        composite[0,:,:] = img2[:,:]
#        composite[1,:,:] = edges[:,:]
#        skimage.io.imsave("%s/%s_composite_edges.tif" % (opath, bpath), composite, plugin='tifffile', check_contrast=False)

