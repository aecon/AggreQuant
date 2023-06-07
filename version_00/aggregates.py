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
        self.Number_Aggregates_Per_Cell = 0


def QoI(labels_agg, labels_cells):
    """
    Quantities of Interest:
        1. Percentage of aggregate-positive cells
        2. Number of cells per image
        3. Total area of aggregates (in percentage of cell area)
        4. Percentage of ambiguous aggregates (corresponding to more than 1 cell)
        5. Number of aggregates per image.
        6. Prototype: Number of aggregates per cell.
    """

    if 0:
        combined = np.zeros( ( np.shape(labels_agg)[0], 10+2*np.shape(labels_agg)[1] ) )
        combined[:, 0:np.shape(labels_agg)[1]] = labels_agg[:,:] * 20 # color scaling
        combined[:, 10+np.shape(labels_agg)[1]::] = labels_cells[:,:]
        plt.imshow(combined)
        plt.show()

    # mask of potential aggregates
    mask_agg = np.zeros(np.shape(labels_cells))
    mask_agg[labels_agg>0] = 1

    # aggregate mask, only inside cells
    mask_agg[labels_cells==0] = 0
    mask_agg_ = scipy.ndimage.maximum_filter(mask_agg, size=2)
    mask_agg  = skimage.morphology.remove_small_holes(mask_agg_>0, area_threshold=25, connectivity=2)
    #plt.imshow(mask_agg)
    #plt.show()

    # relabel aggregates inside cells
    labels_agg2 = skimage.morphology.label(mask_agg, connectivity=2)

    # QUANTIFICATION
    Q = Quantities()

    # Q1. Percentage of aggregate-positive cells
    Q.Percentage_Of_AggregatePositive_Cells = 0
    aggregate_labels_per_cell = np.zeros(np.shape(mask_agg))
    for icell in np.unique(labels_cells):
        if icell==0:
            continue
        idx_cells = labels_cells==icell
        s = np.sum(mask_agg[idx_cells])
        if s>4:  # ignore very small aggregates in cells
            tmp = np.zeros(np.shape(mask_agg))
            tmp[idx_cells] = 1
            idx_agg = mask_agg>0
            idx_agg_in_cell = idx_cells * idx_agg
            tmp[idx_agg_in_cell] = 2
            #plt.imshow(tmp)
            #plt.show()
            Q.Percentage_Of_AggregatePositive_Cells = Q.Percentage_Of_AggregatePositive_Cells + 1
            aggregate_labels_per_cell[idx_agg_in_cell] = icell

    # Q2. Number of cells per image
    Q.Number_Of_Cells_Per_Image = len(np.unique(labels_cells)) - 1  # ignore background label

    # Q3. Total area of aggregates (in percentage of cell area)
    Q.Percentage_Area_Aggregates = np.sum(mask_agg>0) / np.sum(labels_cells>0) * 100.

    # Q4. Percentage of Ambiguous aggregates
    Q.Percentage_Ambiguous_Aggregates = 0
    for iagg in np.unique(labels_agg2):
        if iagg==0:
            continue

        # find in how many cells the aggregate is split
        idx_agg = labels_agg2==iagg  # indices of one connected comp. aggregate

        # find cell IDs that the aggregate spans over
        single_agg_span_cells = np.zeros(np.shape(labels_agg))
        single_agg_span_cells[idx_agg] = aggregate_labels_per_cell[idx_agg]
        #plt.imshow(single_agg_span_cells)
        #plt.show()
        #assert(0)

        cell_ids_in_aggregate_ = np.unique(aggregate_labels_per_cell[idx_agg])
        cell_ids_in_aggregate = cell_ids_in_aggregate_[cell_ids_in_aggregate_>0]

        print(cell_ids_in_aggregate, "length:", len(cell_ids_in_aggregate))
        if len(cell_ids_in_aggregate)==1:
            Q.Number_Aggregates_Per_Image_SplitOnCells += 1
        elif len(cell_ids_in_aggregate)>1:
            # Check if aggregate split is too much or not.. ignore very small overlapping areas..    
            area_of_aggregate_per_cell = np.zeros(len(cell_ids_in_aggregate))
            aggregate_area = np.sum(idx_agg)
            for ii in range(len(cell_ids_in_aggregate)):
                s = np.sum(single_agg_span_cells==cell_ids_in_aggregate[ii])
                print(s, aggregate_area)
                area_of_aggregate_per_cell[ii] = s / aggregate_area * 100.
            print("area_of_aggregate_per_cell:", area_of_aggregate_per_cell)
            ncells_ = area_of_aggregate_per_cell[area_of_aggregate_per_cell>2]
            print(ncells_, len(ncells_))
            Q.Number_Aggregates_Per_Image_SplitOnCells += len(ncells_)
            print(Q.Number_Aggregates_Per_Image_SplitOnCells)
            assert(0)

    # Q5. Number of Aggregates Per Image
    Q.Number_Aggregates_Per_Image_ConnectedComponents = len(np.unique(labels_agg2)) - 1  # exclude background

    # Q6. Number of Aggregates per Cell
    # TODO


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

