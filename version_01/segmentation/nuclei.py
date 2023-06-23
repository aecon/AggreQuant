import os
import sys
import time
import numpy as np
import skimage.io
import skimage.filters
import skimage.morphology
from skimage import restoration

import cupy as cp
from cupyx.scipy.ndimage import gaussian_filter

import matplotlib.pyplot as plt


class Nuclei:

    def __init__(self, fileInfo):
        self.Nimages = 0

        self.nuclei_seeds = fileInfo.NUCLEI_SEEDS
        self.nuclei_all_labels = fileInfo.NUCLEI_ALL_LABELS

        self.input_directory = fileInfo.INPUT_DIR
        self.output_directory = "%s/nuclei" % fileInfo.OUTPUT_DIR


    def preprocess_gpu_1(self, img0):
        mean = np.median(img0)
        print(np.mean(img0), np.median(img0))
        tmp = np.zeros(np.shape(img0))
        tmp[:,:] = img0[:,:]
        tmp[img0>mean] = mean

        g_ = cp.asarray(tmp, dtype=float)
        g1 = gaussian_filter(g_, sigma=20, mode='nearest')
        g0 = cp.asarray(img0, dtype=float)
        g2 = cp.subtract(g0, g1)
        g3 = gaussian_filter(g2, sigma=2)
        img = cp.asnumpy(g3)
        return img


    def preprocess_cpu_1(self, img0):
        # Takes ~ 1.2 sec
        img1 = skimage.filters.gaussian(img0, sigma=2)
        back = skimage.filters.gaussian(img1, sigma=50, mode='nearest', preserve_range=True)
        img2 = img1 / back
        return img2


    def preprocess_cpu_0(self, img0):
        # CLAHE takes ~20 sec
        # background subtraction
        background = restoration.rolling_ball(img0, radius=50)
        img1 = img0 - background

        img2 = skimage.exposure.equalize_adapthist(img1, kernel_size=150)
        rescale_range = np.max(img2) - np.min(img2)
        Max_uint16 = 65535
        img2_ = (img2-np.min(img2)) / (np.max(img2) - np.min(img2))
        img2_ = img2_*Max_uint16
        img2 = np.asarray(img2_, dtype=np.dtype(np.uint16))

        # smoothing
        img = skimage.filters.gaussian(img2, sigma=3)

        return img


    def segment_nuclei(self, image_list, verbose=False):

        import tensorflow as tf
        tf.autograph.set_verbosity(2)
        from stardist.models import StarDist2D
        from csbdeep.utils import normalize

        # limit GPU usage
        gpus = tf.config.experimental.list_physical_devices('GPU')
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)

        # import pretrained model
        model = StarDist2D.from_pretrained('2D_versatile_fluo')

        opath = self.output_directory
        if not os.path.exists(opath):
            os.makedirs(opath)

        # loop over images
        for im,image_file in enumerate(image_list):

            bpath = os.path.basename(image_file)

            if verbose:
                print(">> Processing image: %s" % os.path.basename(image_file))

            img0 = skimage.io.imread(image_file, plugin='tifffile')

            t1 = time.time()
            img = self.preprocess_cpu_1(img0)
            t2 = time.time()
            print("time before segmentation:", t2-t1)
            skimage.io.imsave("%s/%s_img_gpu.tif" % (opath, bpath), img, plugin='tifffile', check_contrast=False)

            # segmentation
            labels, _ = model.predict_instances( normalize(img), predict_kwargs=dict(verbose=False) )

            t3 = time.time()
            print("time for segmentation:", t3-t2)


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

            # find edges
            edges0 = skimage.filters.sobel(labels)
            edges = np.zeros(np.shape(edges0), dtype=np.dtype(np.uint8))
            edges[edges0>0] = 1
            fat_edges = skimage.morphology.binary_dilation(edges)

            # create boarders between labeled objects
            objects = np.zeros(np.shape(edges0), dtype=np.dtype(np.uint16))
            objects[:,:] = labels[:,:]
            objects[fat_edges==1] = 0

            skimage.io.imsave("%s/%s_%s.tif" % (opath, bpath, self.nuclei_all_labels), objects, plugin='tifffile', check_contrast=False)

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
            skimage.io.imsave("%s/%s_%s.tif" % (opath, bpath, self.nuclei_seeds), mask, plugin='tifffile', check_contrast=False)

            t4 = time.time()
            print("time after segmentation:", t4-t3)

            assert(0)

#            # reconstruct edges from nuclei seeds
#            edges0 = skimage.filters.sobel(mask)
#            edges = np.zeros(np.shape(edges0), dtype=np.dtype(np.uint8))
#            edges[edges0>0] = 1
#
#            # overlay edges and original image
#            composite = np.zeros( (2, np.shape(objects)[1], np.shape(objects)[0]), dtype=np.dtype(np.uint16))
#            composite[0,:,:] = img2[:,:]
#            composite[1,:,:] = edges[:,:]
#            skimage.io.imsave("%s/%s_composite_edges.tif" % (opath, bpath), composite, plugin='tifffile', check_contrast=False)

