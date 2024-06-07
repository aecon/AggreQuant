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
from cellpose import models

from processing import image_functions as IF


verbose = False
debug = False

def _scale_values_01_float(img):
    """
    Return image with values scaled between 0 and 1
    """
    IMIN = np.min(img)
    IMAX = np.max(img)

    img1 = (img-IMIN)/(IMAX-IMIN)
    img2 = np.asarray(img1, dtype=float)

    scale = np.asarray([IMIN, IMAX])

    return img2, scale


def _exclude_cells_without_nucleus(labels, seeds):
    AllLabels = np.unique(labels[labels>0])
    for l in AllLabels:
        idx = labels==l
        is_seed = np.sum(seeds[idx])
        if is_seed < 100:    #TODO: Make parameter
            labels[idx] = 0
            if verbose:
                print("No seed for label", l)
    return labels


#def _segment_distance_map(image_file, output_files_cells):  # TODO
#
#
#    # load image and convert to float
#    img0 = skimage.io.imread(image_file, plugin='tifffile')
#    img0 = np.asfarray(img0, float)
#
#    # 1. GENERATE MASK OF CELLBODY AREA
#    # background division
#    smt = skimage.filters.gaussian(img0, sigma=2)
#    #print("Smooth s=2:", np.min(smt), np.max(smt))
#    img_cap = np.zeros(np.shape(img0))
#    img_cap[:,:] = img0[:,:]
#    img_cap[img0>1000] = 1000
#    bkg = skimage.filters.gaussian(img_cap, sigma=50)
#    #print("Smooth s=50, capped:", np.min(bkg), np.max(bkg))
#    img1 = smt / bkg
#
#    #print("After BEQ:", np.min(img1), np.max(img1))
#    img11, scale = _scale_values_01_float(img1)
#    #print("After scaling 0/1 (float):", np.min(img11), np.max(img11))
#    img2 = skimage.exposure.equalize_adapthist(img11, kernel_size=150)
#    #print("After CLAHE:", np.min(img2), np.max(img2))
#
#    IMIN = scale[0]
#    IMAX = scale[1]
#    cells_area = img2*(IMAX-IMIN)+IMIN
#
#    cell_mask_ = np.zeros(np.shape(cells_area), dtype=np.dtype(np.uint8))
#    cell_mask_[cells_area>1.5] = 1
#    #plt.imshow(cell_mask_)
#    #plt.show()
#
#    # remove small holes
#    cell_mask = skimage.morphology.remove_small_holes(cell_mask_.astype(bool, copy=True), area_threshold=400)
#    #plt.imshow(cell_mask)
#    #plt.show()
#
#    # 2. SPLIT CELL MASK BASED on NUCLEI SEEDS
#
#    # load image and convert to float
#    allnuclei = skimage.io.imread(output_files_nuclei["alllabels"], plugin='tifffile')
#    allnuclei_mask = np.zeros(np.shape(allnuclei), dtype=np.dtype(np.uint8))
#    allnuclei_mask[allnuclei>0] = 1
#
#    # load image and convert to float
#    seeds = skimage.io.imread(output_files_nuclei["seeds"], plugin='tifffile')  # uint8
#
#    # compute distances to all nuclei
#    distances = ndimage.distance_transform_edt(1-allnuclei_mask)  # float64
#    #plt.imshow(distances)
#    #plt.show()
#
#    # watershed of distance map
#    labels_ = watershed(distances, mask=cell_mask, watershed_line=True)
#    labels = np.zeros(np.shape(allnuclei_mask), dtype=np.dtype(np.uint16))
#    labels[labels_>0] = labels_[labels_>0]
#    #plt.imshow(labels)
#    #plt.show()
#
#    # Remove cellbodies that do not contain nucleus
#    labels2 = _exclude_cells_without_nucleus(labels, seeds)
#    skimage.io.imsave(output_files_cells["labels"], labels2, plugin='tifffile', check_contrast=False)
#
#
#
#     # Assign a cell area to each nucleus
#     nuclei_labels = np.zeros(np.shape(labels), dtype=np.dtype(np.uint16))
#     nuclei_labels[labels>0] = labels[labels>0]
#     nuclei_labels[seeds==0] = 0
#     #plt.imshow(nuclei_labels)
#     #plt.show()
#     skimage.io.imsave("%s/%s_corresponding_nuclei.tif" % (opath, bpath), nuclei_labels, plugin='tifffile', check_contrast=False)
# 
#     # find edges
#     nuclei_labels[nuclei_labels>0] = 1
#     edges0 = skimage.filters.sobel(nuclei_labels)
#     edges = np.zeros(np.shape(edges0), dtype=np.dtype(np.uint8))
#     edges[edges0>0] = 1
#     fat_edges = edges #skimage.morphology.binary_dilation(edges)
# 
#     # overlay cells and nuclei edges
#     composite = np.zeros( np.shape(labels), dtype=np.dtype(np.uint16) )
#     composite[:,:] = labels[:,:]
#     composite[fat_edges==1] = 0
#     skimage.io.imsave("%s/%s_%s.tif" % (opath, bpath, Names.COMPOSITE_CELLS_AND_NUCLEI ), composite, plugin='tifffile', check_contrast=False)


#def _segment_intensity_map(image_file, output_files_cells):  # TODO
#
#    # TODO:
#    # > compute average intensity of image. Proceed based on average intensity ..
#
#    bpath = os.path.basename(image_file)
#
#    # load image and convert to float
#    img0 = skimage.io.imread(image_file, plugin='tifffile')
#    img0 = np.asfarray(img0, float)
#
#    # 1. GENERATE MASK OF CELLBODY AREA
#    # background division
#    smt = skimage.filters.gaussian(img0, sigma=2)
#    #print("Smooth s=2:", np.min(smt), np.max(smt))
#    img_cap = np.zeros(np.shape(img0))
#    img_cap[:,:] = img0[:,:]
#    img_cap[img0>1000] = 1000
#    bkg = skimage.filters.gaussian(img_cap, sigma=50)
#    #print("Smooth s=50, capped:", np.min(bkg), np.max(bkg))
#    img1 = smt / bkg
#
#    #print("After BEQ:", np.min(img1), np.max(img1))
#    img11, scale = _scale_values_01_float(img1)
#    #print("After scaling 0/1 (float):", np.min(img11), np.max(img11))
#    img2 = skimage.exposure.equalize_adapthist(img11, kernel_size=150)
#    #print("After CLAHE:", np.min(img2), np.max(img2))
#
#    IMIN = scale[0]
#    IMAX = scale[1]
#    cells_area = img2*(IMAX-IMIN)+IMIN
#
#    cell_mask_ = np.zeros(np.shape(cells_area), dtype=np.dtype(np.uint8))
#    cell_mask_[cells_area>1.5] = 1
#    #plt.imshow(cell_mask_)
#    #plt.show()
#
#    # remove small holes
#    cell_mask = skimage.morphology.remove_small_holes(cell_mask_.astype(bool, copy=True), area_threshold=400)
#    #plt.imshow(cell_mask)
#    #plt.show()
#
#    # 2. SPLIT CELL MASK BASED on NUCLEI SEEDS
#
#    # load image and convert to float
#    allnuclei = skimage.io.imread(output_files_nuclei["alllabels"], plugin='tifffile')
#    allnuclei_mask = np.zeros(np.shape(allnuclei), dtype=np.dtype(np.uint8))
#    allnuclei_mask[allnuclei>0] = 1
#
#    # load image and convert to float
#    seeds = skimage.io.imread(output_files_nuclei["seeds"], plugin='tifffile')  # uint8
#
#    # field to use for watershed
#    intensity_field_ = skimage.filters.gaussian(img2, sigma=6)
#    intensity_field, _ = _scale_values_01_float(intensity_field_)
#    field = 1.0 - intensity_field
#    field[allnuclei_mask==1] = 0
#    #print(np.min(field), np.max(field))
#    #plt.imshow(field)
#    #plt.show()
#
#    # compute distances to all nuclei
#    #distances = ndimage.distance_transform_edt(1-allnuclei_mask)  # float64
#    #plt.imshow(distances)
#    #plt.show()
#
#    # watershed of distance map
#    labels_ = watershed(field, mask=cell_mask, watershed_line=True)
#    labels = np.zeros(np.shape(allnuclei_mask), dtype=np.dtype(np.uint16))
#    labels[labels_>0] = labels_[labels_>0]
#    #plt.imshow(labels)
#    #plt.show()
#
#    # Remove cellbodies that do not contain nucleus
#    labels2 = _exclude_cells_without_nucleus(labels, seeds)
#    skimage.io.imsave(output_files_cells["labels"], labels2, plugin='tifffile', check_contrast=False)


def _segment_distanceIntensity(image_file, output_files_cells, output_files_nuclei):

    # Segmentation parameters
    THRESHOLD_NORMALIZED = 1.04  # used 1.20 for validation figures
    MIN_CELL_INTENSITY = 200
    FOREGROUND_SIGMA = 2
    BACKGROUND_SIGMA = 50
    MAX_INTENSITY_PERCENTILE = 99.8
    MAX_DISTANCE_FROM_NUCLEI = 100
    CLAHE_FIELD_BLUR_SIGMA = 6

    # Load image
    img0 = IF.load_image(image_file, verbose)
    img0 = np.asfarray(img0, float)  # float is necessary for next steps

    # Calculate thresholds
    # - XX-th percentile: ignore very bright foreground in background estimation
    cap_threshold = np.percentile(img0, MAX_INTENSITY_PERCENTILE)
    if verbose:
        print(" > signal max intensity:", cap_threshold)
        back_threshold = np.percentile(img0, 0.02)
        print(" > background min intensity:", back_threshold)


    # 1. GENERATE MASK OF CELLBODY AREA
    # background division
    denoised = skimage.filters.gaussian(img0, sigma=FOREGROUND_SIGMA)

    # cap foreground
    img_cap = np.zeros(np.shape(img0))
    img_cap[:,:] = img0[:,:]
    img_cap[img0>cap_threshold] = cap_threshold

    # estimate background
    bkg = skimage.filters.gaussian(img_cap, sigma=BACKGROUND_SIGMA)

    # intensity normalization
    normalized = denoised / bkg

    # CLAHE
    scaledNormalized, scale = _scale_values_01_float(normalized)
    scaledClahe = skimage.exposure.equalize_adapthist(scaledNormalized, kernel_size=150)

    # Ignore pixels with small intensities
    # - minimum cross-entropy: split foreground and background distributions
    min_Cell_Intensity = MIN_CELL_INTENSITY #skimage.filters.threshold_li(denoised); print("threshold_li (ignore values below this):", min_Cell_Intensity)
    scaledClahe[denoised<min_Cell_Intensity] = 0
    print(" > Min. cell intensity (Li - unused):", skimage.filters.threshold_li(denoised))

    IMIN = scale[0]
    IMAX = scale[1]
    cells_area = scaledClahe*(IMAX-IMIN)+IMIN

    cell_mask_ = np.zeros(np.shape(cells_area), dtype=np.dtype(np.uint8))
    cell_mask_[cells_area>THRESHOLD_NORMALIZED] = 1

    # remove small holes
    cell_mask = skimage.morphology.remove_small_holes(cell_mask_.astype(bool, copy=True), area_threshold=400)


    # 2. SPLIT CELL MASK BASED on NUCLEI SEEDS

    # load image and convert to float
    allnuclei = skimage.io.imread(output_files_nuclei["alllabels"], plugin='tifffile')
    allnuclei_mask = np.zeros(np.shape(allnuclei), dtype=np.dtype(np.uint8))
    allnuclei_mask[allnuclei>0] = 1

    # load image and convert to float
    seeds = skimage.io.imread(output_files_nuclei["seeds"], plugin='tifffile')  # uint8

    # extend cell mask to include nuclei seeds
    cell_mask[seeds==1] = 1


    # 3. COMBINE INTENSITY AND DISTANCE FIELDS

    # intensity field
    intensity_field = skimage.filters.gaussian(scaledClahe, sigma=CLAHE_FIELD_BLUR_SIGMA)

    # invert intensity field
    tmp, _ = _scale_values_01_float(intensity_field)
    inverted_01_intensity_field = 1.0 - tmp
    inverted_01_intensity_field[allnuclei_mask==1] = 0

    # compute distances to all nuclei
    distances = ndimage.distance_transform_edt(1-allnuclei_mask)  # float64
    distances[distances>=MAX_DISTANCE_FROM_NUCLEI] = 0

    # watershed field: weighted average of distance and intensity
    field = np.zeros(np.shape(distances))
    field[:,:] = inverted_01_intensity_field * distances 

    #fig, (ax0, ax1, ax2) = plt.subplots(nrows=1, ncols=3, figsize=(12, 6))
    #ax0.imshow(inverted_01_intensity_field * distances * distances)
    #ax1.imshow(inverted_01_intensity_field * distances)
    #ax2.imshow(inverted_01_intensity_field)
    #plt.show()
    #assert(0)

    # watershed of distance map
    labels_ = watershed(field, mask=cell_mask, watershed_line=True)
    labels = np.zeros(np.shape(allnuclei_mask), dtype=np.dtype(np.uint16))
    labels[labels_>0] = labels_[labels_>0]

    # Remove cellbodies that do not contain nucleus
    labels2 = _exclude_cells_without_nucleus(labels, seeds)
    skimage.io.imsave(output_files_cells["labels"], labels2, plugin='tifffile', check_contrast=False)



def _segment_cellpose(image_file, output_files_cells, output_files_nuclei, model):
    """
    Use the pre-trained Deep Neural Network cellpose for segmentation of cells. 

    Model:
        cyto2: For best accuracy and runtime performance, resize images so cells are less than 100 pixels across.

    Settings:
        Using default settings. For more info see:
        https://cellpose.readthedocs.io/en/latest/settings.html

    Additional info:
        Explanation of 'channel' parameter:
        https://forum.image.sc/t/about-the-correct-meaning-of-channel-in-cellpose-2-2/79671/7
    """

    # cellpose parameters
    channels = [1,2]

    # load cell image
    img0 = IF.load_image(image_file, verbose)

    # load nuclei labels
    allnuclei = skimage.io.imread(output_files_nuclei["alllabels"], plugin='tifffile')
    allnuclei_mask = np.zeros(np.shape(allnuclei))
    allnuclei_mask[allnuclei>0] = 1

    # pixels per direction
    n = np.shape(img0)[0]

    # input to cellpose: a two-channel image [cells, nuclei]
    input_to_cellpose = np.zeros((2,n,n))
    input_to_cellpose[0,:,:] = img0[:,:]
    input_to_cellpose[1,:,:] = allnuclei_mask[:,:]  # using nuclei masks gives MUCH better cell segmentation!

    # run cellpose
    masks, flows, styles, diams = model.eval(input_to_cellpose, diameter=None, channels=channels, resample=True,
                                             flow_threshold=0.4, cellprob_threshold=0.0, do_3D=False)

    # nuclei mask
    seeds = skimage.io.imread(output_files_nuclei["seeds"], plugin='tifffile')

    # add cells where there was a nucleus
    idx = (seeds==1) * (masks==0)
    masks[idx] = 1

    # remove cells that don't contain nucleus
    labels2 = _exclude_cells_without_nucleus(masks, seeds)

    #from cellpose import plot
    #fig = plt.figure(figsize=(12,5))
    #plot.show_segmentation(fig, img0, labels2, flows[0], channels=channels)
    #plt.tight_layout()
    #plt.show()

    skimage.io.imsave(output_files_cells["labels"], labels2, plugin='tifffile', check_contrast=False)



def segment_cells(algorithm, image_file, output_files_cells, output_files_nuclei, _verbose, _debug, model=None):

    verbose = _verbose
    debug = _debug

#    if algorithm == "distance":
#        _segment_distance_map(image_file, output_files_cells, output_files_nuclei)
#
#    elif algorithm == "intensity":
#        _segment_intensity_map(image_file, output_files_cells, output_files_nuclei)
#
    if algorithm == "distanceIntensity":
        _segment_distanceIntensity(image_file, output_files_cells, output_files_nuclei)

    elif algorithm == "cellpose":
         _segment_cellpose(image_file, output_files_cells, output_files_nuclei, model)

    else:
        print("Segmentation algorithm %s not defined." % algorithm)
        sys.exit()

