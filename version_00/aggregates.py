import os
import sys
import numpy as np
import skimage.io
import skimage.filters
import scipy.ndimage
import matplotlib.pyplot as plt
import tifffile

from filenames import Filenames
from diagnostics import Diagnostics


class Quantities:
    def __init__(self):
        self.Percentage_Of_AggregatePositive_Cells = 0
        self.Number_Of_Cells_Per_Image = 0
        self.Percentage_Area_Aggregates = 0
        self.Percentage_Ambiguous_Aggregates = 0
        self.Number_Aggregates_Per_Image_ConnectedComponents = 0
        self.Avg_Number_Aggregates_Per_AggPositive_Cell = 0

    def export_table(self, table_file):
        """
        Export a text file with a table of aggregate characteristics per image set
        """

#        with open(table_file+"_per_aggregate.txt", 'w') as f:
#            f.write("%12s %12s \n" % ("Volume(um3)", "NMolTDP"))
#            for i in range(Nc):
#                f.write("%12.2e %12d \n" % (volumes[i], particles[i] ))
#            f.close()

        with open(table_file, 'w') as f:
            f.write("%15s %15s %15s %15s %15s %16s\n" % ("%Agg.Pos.Cells", "N.Cells", "%Area.Agg.",     "%Ambig.Agg.", "N.Agg.Img(CC)", "Avg.NAgg.perCell"))
            f.write("%15g %15g %15g %15g %15g %16g\n" % (self.Percentage_Of_AggregatePositive_Cells, self.Number_Of_Cells_Per_Image, self.Percentage_Area_Aggregates, self.Percentage_Ambiguous_Aggregates, self.Number_Aggregates_Per_Image_ConnectedComponents, self.Avg_Number_Aggregates_Per_AggPositive_Cell))
            f.close()



def return_mask(img, value):
    mask = np.zeros(np.shape(img))
    mask[img>value] = 1
    return mask


def exclude_outside_cells(img, cells):
    img[cells==0] = 0  # exclude everything not covered by a cell
    tmp1 = np.asarray(scipy.ndimage.maximum_filter(img, size=2), dtype=np.dtype(np.uint16))  # remove watershed lines
    tmp2 = skimage.morphology.remove_small_holes(tmp1, area_threshold=25, connectivity=2) # remove holes
    return tmp2


def QoI(labels_agg0, labels_cells, bpath, opath, check_code=False):
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

    check_code = False

    # aggregate mask (exclude aggregates outside cells)
    tmp_     = return_mask(labels_agg0, 0)
    mask_agg = exclude_outside_cells(tmp_, labels_cells)

    # connected components for aggregates inside cells
    labels_agg = skimage.morphology.label(mask_agg, connectivity=2)
    skimage.io.imsave("%s/%s_labels_aggregates_InsideCells.tif" % (opath, bpath), labels_agg, plugin='tifffile')

    # cell maks
    mask_cell = np.zeros(np.shape(labels_cells))
    mask_cell[labels_cells>0] = 1

    # Overlay of aggregates on cells and total aggregates
    if (check_code==True) and (False):
        _tmp1 = labels_agg0>0
        _tmp2 = labels_agg>0
        _tmp3 = np.zeros(np.shape(_tmp1))
        _tmp3[_tmp1] =  _tmp3[_tmp1]+1
        _tmp3[_tmp2] =  _tmp3[_tmp2]+1
        print(np.unique(_tmp3))
        plt.imshow(_tmp3)
        plt.title("All aggregate mask")
        plt.show()


    # Unique cell IDs
    U_CELLS = np.unique(labels_cells[labels_cells>0])

    # Unique aggregate IDs (connected components)
    U_AGG = np.unique( labels_agg[labels_agg>0] )


    # overlay detected cells and aggregates
    overlay_cells_agg = np.zeros( (np.shape(labels_cells)[1], np.shape(labels_cells)[0]), dtype=np.dtype(np.uint16))
    overlay_cells_agg[mask_cell>0] = 2
    #skimage.io.imsave("%s/%s_overlay_segmented_cells_aggregates.tif" % (opath, bpath), overlay_cells_agg, plugin='tifffile')
    #tifffile.imwrite("%s/%s_overlay_segmented_cells_aggregates.tif" % (opath, bpath), overlay_cells_agg, metadata={"axes": "CYX"}, imagej=True)


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
        #print("aggregate area:", total_agg_area)

        # troubleshooting
        if check_code==True:
            tmp_ = np.zeros(np.shape(mask_agg))
            for ic, icell in enumerate(ID_cells):
                itmp2_ = (labels_cells == icell)
                tmp_[itmp2_] = ic+2
            tmp_[idx_agg] = -1
            tmp_[labels_cells==0] = 0
            tmp_idx_non_zero = np.where(tmp_>0)
            ymin = np.min(tmp_idx_non_zero[0])
            ymax = np.max(tmp_idx_non_zero[0])
            xmin = np.min(tmp_idx_non_zero[1])
            xmax = np.max(tmp_idx_non_zero[1])
            tmp_new = np.zeros((ymax-ymin, xmax-xmin))
            tmp_new[:,:] = tmp_[ymin:ymax, xmin:xmax]
            cmap = plt.get_cmap('gist_yarg')
            cmap.set_under('magenta')  # Color for values less than vmin

            # view figure
            #plt.imshow(tmp_new, cmap='gist_yarg', vmin=0, vmax=len(ID_cells)+1)  # the full cells that it covers
            #plt.show()
            #plt.savefig("fig_pipeline/check_code_%s_IAGG-%04d.png" % (bpath, ia))
            #plt.close()

            # save tif file
            skimage.io.imsave("%s/%s_CHECK_segmented_aggID_%04d_over_cells.tif" % (opath, bpath, iagg), tmp_new, plugin='tifffile')
            #assert(0)



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
            if ratio_of_agg_to_icell_area > 0.1:  # consider only aggregates covering more than X% of cell area
                icell_in_U_CELLS = (U_CELLS == icell)
                list_number_of_aggregates_per_cell[icell_in_U_CELLS] += 1
                # for tif image diagnostics:
                overlay_cells_agg[labels_cells==icell] = 3

        #print("ratio_area_of_agg_split_over_cells:", ratio_area_of_agg_split_over_cells)
        #assert( np.sum(ratio_area_of_agg_split_over_cells)>80 and np.sum(ratio_area_of_agg_split_over_cells)<=100  ) # TODO: CHECK!

        list_number_of_cells_per_aggregate[ia] = np.sum( ratio_area_of_agg_split_over_cells>1. )  # ambiguously split aggregates
        #print("list_number_of_cells_per_aggregate[ia]:", list_number_of_cells_per_aggregate[ia])

    # store tif image diagnostics
    overlay_cells_agg[mask_agg>0]  = 1
    skimage.io.imsave("%s/%s_overlay_segmented_cells_aggregates.tif" % (opath, bpath), overlay_cells_agg, plugin='tifffile')

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


    table_file = "%s/%s_exported_table.txt" % (opath, bpath)
    print("Exporting table to %s" % table_file)
    Q.export_table(table_file)
    #assert(0)



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
    skimage.io.imsave("%s/%s_labels_AllAggregates.tif" % (opath, bpath), labels, plugin='tifffile')
    #plt.imshow(labels)
    #plt.show()

    # load cell labels
    img_cells = skimage.io.imread(cells_file, plugin='tifffile')

    QoI(labels, img_cells, bpath, opath)



def segment_ilastik():
    print("TODO.")
    assert(0)



def aggregate_segmentation(aggregate_images, Names):

    print("Number of aggregate images:", len(aggregate_images))

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

        assert(0)
