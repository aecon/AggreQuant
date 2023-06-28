import os
import sys
import numpy as np
import argparse
import skimage.io
import skimage.filters
import skimage.morphology
from skimage import restoration
import matplotlib.pyplot as plt
from scipy import ndimage
from skimage.segmentation import watershed


class CellSegmentation:

    def __init__(self, input_file, output_files_nuclei, output_files_cells, verbose=False, debug=False, algorithm="propagation"):
        self.input_file             = input_file
        self.output_files_nuclei    = output_files_nuclei # struct defined in Dataset
        self.output_files_cells     = output_files_cells  # struct defined in Dataset
        self.algorithm              = algorithm
        self.verbose                = verbose
        self.debug                  = debug
        if verbose:
            print("Segmenting cells with algorithm %s" % self.algorithm)


    def _scale_values_01_float(self, img):
        """
        Return image with values scaled between 0 and 1
        """
        IMIN = np.min(img)
        IMAX = np.max(img)

        img1 = (img-IMIN)/(IMAX-IMIN)
        img2 = np.asarray(img1, dtype=float)

        scale = np.asarray([IMIN, IMAX])

        return img2, scale


    def _exclude_cells_without_nucleus(self, labels, seeds):
        AllLabels = np.unique(labels[labels>0])
        for l in AllLabels:
            idx = labels==l
            is_seed = np.sum(seeds[idx])
            if is_seed < 100:
                labels[idx] = 0
                if self.verbose:
                    print("No seed for label", l)
        return labels


    def _segment_distance_map(self):

        image_file = self.input_file

        bpath = os.path.basename(image_file)

        # load image and convert to float
        img0 = skimage.io.imread(image_file, plugin='tifffile')
        img0 = np.asfarray(img0, float)

        # 1. GENERATE MASK OF CELLBODY AREA
        # background division
        smt = skimage.filters.gaussian(img0, sigma=2)
        #print("Smooth s=2:", np.min(smt), np.max(smt))
        img_cap = np.zeros(np.shape(img0))
        img_cap[:,:] = img0[:,:]
        img_cap[img0>1000] = 1000
        bkg = skimage.filters.gaussian(img_cap, sigma=50)
        #print("Smooth s=50, capped:", np.min(bkg), np.max(bkg))
        img1 = smt / bkg

        #print("After BEQ:", np.min(img1), np.max(img1))
        img11, scale = self._scale_values_01_float(img1)
        #print("After scaling 0/1 (float):", np.min(img11), np.max(img11))
        img2 = skimage.exposure.equalize_adapthist(img11, kernel_size=150)
        #print("After CLAHE:", np.min(img2), np.max(img2))

        IMIN = scale[0]
        IMAX = scale[1]
        cells_area = img2*(IMAX-IMIN)+IMIN

        cell_mask_ = np.zeros(np.shape(cells_area), dtype=np.dtype(np.uint8))
        cell_mask_[cells_area>1.5] = 1
        #plt.imshow(cell_mask_)
        #plt.show()

        # remove small holes
        cell_mask = skimage.morphology.remove_small_holes(cell_mask_.astype(bool, copy=True), area_threshold=400)
        #plt.imshow(cell_mask)
        #plt.show()

        # 2. SPLIT CELL MASK BASED on NUCLEI SEEDS

        # load image and convert to float
        allnuclei = skimage.io.imread(self.output_files_nuclei["alllabels"], plugin='tifffile')
        allnuclei_mask = np.zeros(np.shape(allnuclei), dtype=np.dtype(np.uint8))
        allnuclei_mask[allnuclei>0] = 1

        # load image and convert to float
        seeds = skimage.io.imread(self.output_files_nuclei["seeds"], plugin='tifffile')  # uint8

        # compute distances to all nuclei
        distances = ndimage.distance_transform_edt(1-allnuclei_mask)  # float64
        #plt.imshow(distances)
        #plt.show()

        # watershed of distance map
        labels_ = watershed(distances, mask=cell_mask, watershed_line=True)
        labels = np.zeros(np.shape(allnuclei_mask), dtype=np.dtype(np.uint16))
        labels[labels_>0] = labels_[labels_>0]
        #plt.imshow(labels)
        #plt.show()

        # Remove cellbodies that do not contain nucleus
        labels2 = self._exclude_cells_without_nucleus(labels, seeds)
        skimage.io.imsave(self.output_files_cells["labels"], labels2, plugin='tifffile', check_contrast=False)



#        # Assign a cell area to each nucleus
#        nuclei_labels = np.zeros(np.shape(labels), dtype=np.dtype(np.uint16))
#        nuclei_labels[labels>0] = labels[labels>0]
#        nuclei_labels[seeds==0] = 0
#        #plt.imshow(nuclei_labels)
#        #plt.show()
#        skimage.io.imsave("%s/%s_corresponding_nuclei.tif" % (opath, bpath), nuclei_labels, plugin='tifffile', check_contrast=False)
#    
#        # find edges
#        nuclei_labels[nuclei_labels>0] = 1
#        edges0 = skimage.filters.sobel(nuclei_labels)
#        edges = np.zeros(np.shape(edges0), dtype=np.dtype(np.uint8))
#        edges[edges0>0] = 1
#        fat_edges = edges #skimage.morphology.binary_dilation(edges)
#    
#        # overlay cells and nuclei edges
#        composite = np.zeros( np.shape(labels), dtype=np.dtype(np.uint16) )
#        composite[:,:] = labels[:,:]
#        composite[fat_edges==1] = 0
#        skimage.io.imsave("%s/%s_%s.tif" % (opath, bpath, Names.COMPOSITE_CELLS_AND_NUCLEI ), composite, plugin='tifffile', check_contrast=False)


    def _segment_intensity_map(self):

        image_file = self.input_file

        # TODO:
        # > compute average intensity of image. Proceed based on average intensity ..

        bpath = os.path.basename(image_file)

        # load image and convert to float
        img0 = skimage.io.imread(image_file, plugin='tifffile')
        img0 = np.asfarray(img0, float)

        # 1. GENERATE MASK OF CELLBODY AREA
        # background division
        smt = skimage.filters.gaussian(img0, sigma=2)
        #print("Smooth s=2:", np.min(smt), np.max(smt))
        img_cap = np.zeros(np.shape(img0))
        img_cap[:,:] = img0[:,:]
        img_cap[img0>1000] = 1000
        bkg = skimage.filters.gaussian(img_cap, sigma=50)
        #print("Smooth s=50, capped:", np.min(bkg), np.max(bkg))
        img1 = smt / bkg

        #print("After BEQ:", np.min(img1), np.max(img1))
        img11, scale = self._scale_values_01_float(img1)
        #print("After scaling 0/1 (float):", np.min(img11), np.max(img11))
        img2 = skimage.exposure.equalize_adapthist(img11, kernel_size=150)
        #print("After CLAHE:", np.min(img2), np.max(img2))

        IMIN = scale[0]
        IMAX = scale[1]
        cells_area = img2*(IMAX-IMIN)+IMIN

        cell_mask_ = np.zeros(np.shape(cells_area), dtype=np.dtype(np.uint8))
        cell_mask_[cells_area>1.5] = 1
        #plt.imshow(cell_mask_)
        #plt.show()

        # remove small holes
        cell_mask = skimage.morphology.remove_small_holes(cell_mask_.astype(bool, copy=True), area_threshold=400)
        #plt.imshow(cell_mask)
        #plt.show()

        # 2. SPLIT CELL MASK BASED on NUCLEI SEEDS

        # load image and convert to float
        allnuclei = skimage.io.imread(self.output_files_nuclei["alllabels"], plugin='tifffile')
        allnuclei_mask = np.zeros(np.shape(allnuclei), dtype=np.dtype(np.uint8))
        allnuclei_mask[allnuclei>0] = 1

        # load image and convert to float
        seeds = skimage.io.imread(self.output_files_nuclei["seeds"], plugin='tifffile')  # uint8

        # field to use for watershed
        intensity_field_ = skimage.filters.gaussian(img2, sigma=6)
        intensity_field, _ = self._scale_values_01_float(intensity_field_)
        field = 1.0 - intensity_field
        field[allnuclei_mask==1] = 0
        #print(np.min(field), np.max(field))
        #plt.imshow(field)
        #plt.show()

        # compute distances to all nuclei
        #distances = ndimage.distance_transform_edt(1-allnuclei_mask)  # float64
        #plt.imshow(distances)
        #plt.show()

        # watershed of distance map
        labels_ = watershed(field, mask=cell_mask, watershed_line=True)
        labels = np.zeros(np.shape(allnuclei_mask), dtype=np.dtype(np.uint16))
        labels[labels_>0] = labels_[labels_>0]
        #plt.imshow(labels)
        #plt.show()

        # Remove cellbodies that do not contain nucleus
        labels2 = self._exclude_cells_without_nucleus(labels, seeds)
        skimage.io.imsave(self.output_files_cells["labels"], labels2, plugin='tifffile', check_contrast=False)



    def _segment_propagation(self):

        image_file = self.input_file

        bpath = os.path.basename(image_file)

        # load image and convert to float
        img0 = skimage.io.imread(image_file, plugin='tifffile')
        img0 = np.asfarray(img0, float)
        min_Cell_Intensity = 800

        # 1. GENERATE MASK OF CELLBODY AREA
        # background division
        smt = skimage.filters.gaussian(img0, sigma=2)
        #print("Smooth s=2:", np.min(smt), np.max(smt))
        img_cap = np.zeros(np.shape(img0))
        img_cap[:,:] = img0[:,:]
        img_cap[img0>1000] = 1000
        bkg = skimage.filters.gaussian(img_cap, sigma=50)
        #print("Smooth s=50, capped:", np.min(bkg), np.max(bkg))
        img1 = smt / bkg

        #print("After BEQ:", np.min(img1), np.max(img1))
        img11, scale = self._scale_values_01_float(img1)
        #print("After scaling 0/1 (float):", np.min(img11), np.max(img11))
        img2 = skimage.exposure.equalize_adapthist(img11, kernel_size=150)
        #print("After CLAHE:", np.min(img2), np.max(img2))
        img2[img0<min_Cell_Intensity] = 0

        IMIN = scale[0]
        IMAX = scale[1]
        cells_area = img2*(IMAX-IMIN)+IMIN

        cell_mask_ = np.zeros(np.shape(cells_area), dtype=np.dtype(np.uint8))
        cell_mask_[cells_area>1.5] = 1
        #plt.imshow(cell_mask_)
        #plt.show()

        # remove small holes
        cell_mask = skimage.morphology.remove_small_holes(cell_mask_.astype(bool, copy=True), area_threshold=400)
        #plt.imshow(cell_mask)
        #plt.show()

        # 2. SPLIT CELL MASK BASED on NUCLEI SEEDS

        # load image and convert to float
        allnuclei = skimage.io.imread(self.output_files_nuclei["alllabels"], plugin='tifffile')
        allnuclei_mask = np.zeros(np.shape(allnuclei), dtype=np.dtype(np.uint8))
        allnuclei_mask[allnuclei>0] = 1

        # load image and convert to float
        seeds = skimage.io.imread(self.output_files_nuclei["seeds"], plugin='tifffile')  # uint8

        # compute distances to all nuclei
        distances = ndimage.distance_transform_edt(1-allnuclei_mask)  # float64
        #plt.imshow(distances)
        #plt.show()
        max_distance = 150  # in pixels
        #print(np.min(distances), np.max(distances))
        distances[distances>=max_distance] = 0
        distances_, _ = self._scale_values_01_float(distances)
        distances = np.power((1 - distances_), 2)
        #plt.imshow(distances)
        #plt.show()

        # field to use for watershed
        intensity_field_ = skimage.filters.gaussian(img2, sigma=6)
        field_ = intensity_field_ * (distances)

        field0, _ = self._scale_values_01_float(field_)
        field = 1.0 - field0
        #plt.imshow(field)
        #plt.show()

        field[allnuclei_mask==1] = 0
        #plt.imshow(field)
        #plt.show()
        #print(np.min(field), np.max(field))

        # weighted average of distance and intensity fields
        field_ = np.zeros(np.shape(field))
        field_[:,:] = field[:,:]*distances 

        # watershed of distance map
        labels_ = watershed(field, mask=cell_mask, watershed_line=True)
        labels = np.zeros(np.shape(allnuclei_mask), dtype=np.dtype(np.uint16))
        labels[labels_>0] = labels_[labels_>0]
        #plt.imshow(labels)
        #plt.show()

        # Remove cellbodies that do not contain nucleus
        labels2 = self._exclude_cells_without_nucleus(labels, seeds)
        skimage.io.imsave(self.output_files_cells["labels"], labels2, plugin='tifffile', check_contrast=False)



    def segment_cells(self):

        # Choose segmentation algorithm for cells
        if self.algorithm == "distance":
            self._segment_distance_map()

        elif self.algorithm == "intensity":
            self._segment_intensity_map()

        elif self.algorithm == "propagation":
            self._segment_propagation()

#        elif self.algorithm == "cellpose":
#            self._segment_cellpose()

        else:
            print("Segmentation algorithm %s not defined." % self.algorithm)
            sys.exit()


