import os
import sys
import numpy as np
import skimage.io
import skimage.filters
import scipy.ndimage
import matplotlib.pyplot as plt

from filenames import Filenames
from diagnostics import Diagnostics


class Quantities:
    def __init__(self):
        self.Percentage_Of_AggregatePositive_Cells = 0
        self.Number_Of_Cells_Per_Image = 0
        self.Percentage_Area_Aggregates = 0
        self.Percentage_Ambiguous_Aggregates = 0
        self.Number_Aggregates_Per_Image_ConnectedComponents = 0
        self.Number_Aggregates_Per_Image_SplitOnCells = 0 # number of aggregates split on cells
        self.Avg_Number_Aggregates_Per_AggPositive_Cell = 0


def return_mask(img, value):
    mask = np.zeros(np.shape(img))
    mask[img>value] = 1
    return mask


def exclude_outside_cells(img, cells):
    img[cells==0] = 0  # exclude everything not covered by a cell
    tmp1 = np.asarray(scipy.ndimage.maximum_filter(img, size=2), dtype=np.dtype(np.uint16))  # remove watershed lines
    tmp2 = skimage.morphology.remove_small_holes(tmp1, area_threshold=25, connectivity=2) # remove holes
    return tmp2


def QoI(labels_agg0, labels_cells):
    """
    Quantities of Interest:
        1. Percentage of aggregate-positive cells
        2. Number of cells per image
        3. Total area of aggregates (in percentage of cell area)
        4. Percentage of ambiguous aggregates (corresponding to more than 1 cell)
        5. Number of aggregates per image
        6. Prototype: Number of aggregates per cell

        labels_agg: Connected comp. of aggregates inside cells
        mask_cell:  Binary mask of cells
        U_CELLS:    Unique cell IDs
        U_AGG:      Unique aggrgate IDs (Connected components)

        list_number_of_aggregates_per_cell = np.zeros(len(U_CELLS)) - List with number of aggregates per cell.
        list_number_of_cells_per_aggregate = np.zeros(len(U_AGG)) - List with number of cell per aggregate.
    """

    # aggregate mask (exclude aggregates outside cells)
    tmp_     = return_mask(labels_agg0, 0)
    mask_agg = exclude_outside_cells(tmp_, labels_cells)

    # connected components for aggregates inside cells
    labels_agg = skimage.morphology.label(mask_agg, connectivity=2)

    # cell maks
    mask_cell = np.zeros(np.shape(labels_cells))
    mask_cell[labels_cells>0] = 1

    # Overlay of aggregates on cells and total aggregates
    if 0:
        _tmp1 = labels_agg0>0
        _tmp2 = labels_agg>0
        _tmp3 = np.zeros(np.shape(_tmp1))
        _tmp3[_tmp1] =  _tmp3[_tmp1]+1
        _tmp3[_tmp2] =  _tmp3[_tmp2]+1
        plt.imshow(_tmp3)
        plt.show()
        print(np.unique(_tmp3))
        assert(0)

    # Unique cell IDs
    U_CELLS = np.unique(labels_cells[labels_cells>0])

    # Unique aggregate IDs (connected components)
    U_AGG = np.unique( labels_agg[labels_agg>0] )



    # QUANTIFICATION
    Q = Quantities()

    # Q2. Number of cells per image
    Q.Number_Of_Cells_Per_Image = len(U_CELLS)

    # Q5. Number of Aggregates Per Image
    Q.Number_Aggregates_Per_Image_ConnectedComponents = len(U_AGG)

    # Q3. Total area of aggregates (in percentage of cell area)
    Q.Percentage_Area_Aggregates = np.sum(mask_agg) / np.sum(mask_cell) * 100.


    list_number_of_aggregates_per_cell = np.zeros(len(U_CELLS))
    list_number_of_cells_per_aggregate = np.zeros(len(U_AGG))
    
    for ia, iagg in enumerate(U_AGG):

        # indices of aggregate
        idx_agg = (labels_agg==iagg)   # 2040x2040 T/F

        # cell indices/IDs under aggregate
        lbl_cells = labels_cells[idx_agg]  # list of cell Labels
        ID_cells  = np.unique(lbl_cells[lbl_cells>0])

        # total aggregate area
        total_agg_area = np.sum(idx_agg)

        # percentage of aggregate over each overlapping cell
        ratio_area_of_agg_split_over_cells = np.zeros(len(ID_cells))  # to find ambiguous aggregates (split over many cells)

        # loop over cells under aggregate
        for ic, icell in enumerate(ID_cells):

            # area of aggregate over cell `icell`
            agg_area = np.sum(lbl_cells==icell)

            # total area of cell `icell`
            icell_area = np.sum(labels_cells==icell)

            ratio_area_of_agg_split_over_cells[ic] = agg_area / total_agg_area * 100.

            ratio_of_agg_to_icell_area = agg_area / icell_area * 100.
            if ratio_of_agg_to_icell_area > 1.:  # consider only aggregates covering more than 1% of cell area
                icell_in_U_CELLS = (U_CELLS == icell)
                list_number_of_aggregates_per_cell[icell_in_U_CELLS] += 1

        assert( np.sum(ratio_area_of_agg_split_over_cells)>80 and np.sum(ratio_area_of_agg_split_over_cells)<=100  )

        list_number_of_cells_per_aggregate[ia] = np.sum( ratio_area_of_agg_split_over_cells>1. )  # ambiguously split aggregates


    # Q4. Percentage of Ambiguous aggregates
    Q.Percentage_Ambiguous_Aggregates = np.sum(list_number_of_cells_per_aggregate>1) / len(U_AGG) * 100.
    print("")
    print("list_number_of_cells_per_aggregate")
    print(list_number_of_cells_per_aggregate)
    print("Ambiguous aggregates (%):", Q.Percentage_Ambiguous_Aggregates)

    # Q1. Percentage of aggregate-positive cells
    Q.Percentage_Of_AggregatePositive_Cells = np.sum(list_number_of_aggregates_per_cell>0) / len(U_CELLS) * 100.
    print("")
    print("list_number_of_aggregates_per_cell")
    print(list_number_of_aggregates_per_cell)
    print("Aggregate-positive Cells (%):", Q.Percentage_Of_AggregatePositive_Cells)

    # Q6. Average Number of Aggregates per aggregate-positive Cell
    Q.Avg_Number_Aggregates_Per_AggPositive_Cell = np.mean( list_number_of_aggregates_per_cell[list_number_of_aggregates_per_cell>0] )
    print("")
    print("Average number of aggregates, per aggregate-positive cell")
    print(Q.Avg_Number_Aggregates_Per_AggPositive_Cell)


    assert(0)




def segment_intensity_map(image_file, cells_file, opath, Names):

    # load input image
    img = skimage.io.imread(image_file, plugin='tifffile')
    print(np.median(img), np.min(img), np.max(img))

    # cap values
    threshold = np.percentile(img, 98)
    print("threshold:", threshold)
    capped = np.zeros(np.shape(img))
    capped[:,:] = img[:,:]
    capped[img>threshold] = threshold
    #plt.imshow(capped)
    #plt.show()

    # background division
    back = scipy.ndimage.gaussian_filter(capped, sigma=100, mode='reflect')
    print(np.median(back), np.min(back), np.max(back))
    #plt.imshow(back)
    #plt.show()

    # normalized
    norm = img / back
    assert(np.min(norm)>=0)
    #plt.imshow(norm)
    #plt.show()

    # segment
    threshold = np.percentile(norm, 98)
    segmented_ = np.zeros(np.shape(img), dtype=np.uint8)
    segmented_[norm>threshold] = 1
    print("seg. threshold:", threshold)
    #plt.imshow(segmented_)
    #plt.show()

    # median
    segmented = scipy.ndimage.median_filter(segmented_, size=2)

    # connected components
    labels = skimage.morphology.label(segmented, connectivity=2)
    print("Connected cmoponents (original):", np.max(labels))
    #plt.imshow(labels)
    #plt.show()

    # remove small holes
    noholes = skimage.morphology.remove_small_holes(segmented, area_threshold=400, connectivity=2)
    #plt.imshow(noholes)
    #plt.show()
    labels = skimage.morphology.label(noholes, connectivity=2)
    print("Removed small holes:", np.max(labels))
    #plt.imshow(labels)
    #plt.show()

    # remove small objects
    nosmall = skimage.morphology.remove_small_objects(labels, min_size=9, connectivity=2)
    labels = skimage.morphology.label(nosmall, connectivity=2)
    print("Removed small objects:", np.max(labels))
    obj = np.max(labels)
    #plt.imshow(labels)
    #plt.show()

    # save connected components
    bpath = os.path.basename(image_file)
    labels = np.asarray(labels, dtype=np.uint32)
    assert(np.max(labels) == obj)
    skimage.io.imsave("%s/%s_labels_aggregates.tif" % (opath, bpath), labels, plugin='tifffile')
    #plt.imshow(labels)
    #plt.show()

    # load cell labels
    img_cells = skimage.io.imread(cells_file, plugin='tifffile')

    QoI(labels, img_cells)


def segment_ilastik():
    print("TODO.")
    assert(0)



def aggregate_segmentation(aggregate_images, Names):

    segmentation_algorithm = Names.AGGREGATE_SEGMENTATION_TYPE
    print("Segmenting aggregates with algorithm:", segmentation_algorithm)

    for ifile, image_file in enumerate(aggregate_images):

        bpath = os.path.basename(image_file)
        print(">> Processing image: %s" % bpath)

        # find corresponding cellbodies
        cells_file = "%s/%s/%s/%s%s).tif_cellbodies_labels.tif" % ( Names.OUTDIR_PATH, Names.OUTDIR, Names.CELLBODY_ODIR_NAME, bpath.split(Names.COLOR_AGGREGATES,1)[0], Names.COLOR_CELLS)
        if not os.path.isfile(cells_file):
            print("Cellbody labels for file %s do NOT exist!", bpath)
            sys.exit()

        # Output folder for aggregate segmentation
        opath = "%s/%s/%s" % ( Names.OUTDIR_PATH, Names.OUTDIR, Names.AGGREGATE_ODIR_NAME)
        if not os.path.exists(opath):
            print("Path %s does NOT exist. Creating now. " % opath)
            os.makedirs(opath)
        else:
            print("Path %s exists." % opath)

        # Choose segmentation algorithm for aggregates
        if segmentation_algorithm == "intensity":
            segment_intensity_map(image_file, cells_file, opath, Names)

        elif segmentation_algorithm == "ilastik":
            segment_ilastik()

        else:
            print("Segmentation algorithm %s not defined." % segmentation_algorithm)
            sys.exit()

