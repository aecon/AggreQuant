import os
import sys
import numpy as np
import skimage.io
import skimage.filters
import scipy.ndimage
import tifffile



class AggregateSegmentation:

    def __init__(self, input_file, output_files_aggregates, verbose=False, debug=False):
        self.input_file              = input_file
        self.output_files_aggregates = output_files_aggregates # struct defined in Dataset
        self.verbose                = verbose
        self.debug                  = debug
        if verbose:
            print("Segmenting aggregates")


    def segment_aggregates(self):

        image_file = self.input_file

        bpath = os.path.basename(image_file)
        if self.verbose:
            print(">> Processing image: %s" % bpath)

        # load image
        img = skimage.io.imread(image_file, plugin='tifffile')
        if self.debug:
            print(np.median(img), np.min(img), np.max(img))
    
        # cap values
        threshold = np.percentile(img, 98)
        if self.debug:
            print("threshold:", threshold)
        capped = np.zeros(np.shape(img))
        capped[:,:] = img[:,:]
        capped[img>threshold] = threshold
    
        # background division
        back = scipy.ndimage.gaussian_filter(capped, sigma=100, mode='reflect')
        if self.debug:
            print(np.median(back), np.min(back), np.max(back))
    
        # normalized
        norm = img / back
        assert(np.min(norm)>=0)
    
        # segment
        threshold = np.percentile(norm, 98)
        segmented_ = np.zeros(np.shape(img), dtype=np.uint8)
        segmented_[norm>threshold] = 1
        if self.debug:
            print("seg. threshold:", threshold)
    
        # median
        segmented = scipy.ndimage.median_filter(segmented_, size=2)
    
        # connected components
        labels = skimage.morphology.label(segmented, connectivity=2)
        if self.debug:
            print("Connected cmoponents (original):", np.max(labels))
    
        # remove small holes
        noholes = skimage.morphology.remove_small_holes(segmented.astype(bool, copy=True), area_threshold=400, connectivity=2)
        labels = skimage.morphology.label(noholes, connectivity=2)
        if self.debug:
            print("Removed small holes:", np.max(labels))
    
        # remove small objects
        nosmall = skimage.morphology.remove_small_objects(labels, min_size=9, connectivity=2)
        labels = skimage.morphology.label(nosmall, connectivity=2)
        if self.debug:
            print("Removed small objects:", np.max(labels))
        obj = np.max(labels)
    
        # save connected components
        bpath = os.path.basename(image_file)
        labels = np.asarray(labels, dtype=np.uint32)
        assert(np.max(labels) == obj)
        skimage.io.imsave(self.output_files_aggregates["alllabels"], labels, plugin='tifffile', check_contrast=False)


