import os
import sys
import numpy as np
import skimage.io
import skimage.filters
import scipy.ndimage
import matplotlib.pyplot as plt
import tifffile


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

        # Summary for per-Image quantities
        with open(table_file, 'w') as f:
            f.write("%15s %15s %15s %15s %15s %16s\n" % ("%Agg.Pos.Cells", "N.Cells", "%Area.Agg.", "%Ambig.Agg.", "N.Agg.Img(CC)", "Avg.NAgg.perCell"))
            f.write("%15g %15g %15g %15g %15g %16g\n" % (self.Percentage_Of_AggregatePositive_Cells, self.Number_Of_Cells_Per_Image, self.Percentage_Area_Aggregates, self.Percentage_Ambiguous_Aggregates, self.Number_Aggregates_Per_Image_ConnectedComponents, self.Avg_Number_Aggregates_Per_AggPositive_Cell))
            f.close()




def return_mask(img, value):
    mask = np.zeros(np.shape(img))
    mask[img>value] = 1
    return mask


def exclude_outside_cells(mask, cells):
#    tmp1 = np.asarray(scipy.ndimage.maximum_filter(mask, size=2), dtype=np.dtype(np.uint16))  # remove watershed lines
    tmp1 = np.zeros(np.shape(mask), dtype=np.dtype(np.uint8))
    tmp1[mask>0] = 1
    tmp2 = skimage.morphology.remove_small_holes(tmp1, area_threshold=25, connectivity=2) # remove holes
    tmp2[cells==0] = 0  # exclude everything not covered by a cell
    return tmp2


def compute_QoI(output_files_aggregates, output_files_cells, output_files_QoI, verbose=False, debug=False):
    """
    Quantities of Interest:
        1. [CHK] Percentage of aggregate-positive cells
        2. [CHK] Number of cells per image
        3. [CHK] Total area of aggregates (in percentage of cell area)
        4. [CHK] Percentage of ambiguous aggregates (corresponding to more than 1 cell)
        5. [CHK] Number of aggregates per image
        6. [CHK] Prototype: Number of aggregates per cell

        labels_agg: Connected comp. of aggregates inside cells
        mask_cell:  Binary mask of cells
        U_CELLS:    Unique cell IDs
        U_AGG:      Unique aggrgate IDs (Connected components)

        list_number_of_aggregates_per_cell = np.zeros(len(U_CELLS)) - List with number of aggregates per cell.
        list_number_of_cells_per_aggregate = np.zeros(len(U_AGG)) - List with number of cell per aggregate.
    """

    check_code = debug


    # load cell labels
    labels_cells = skimage.io.imread(output_files_cells["labels"], plugin='tifffile')

    # load aggregate labels
    labels_agg0 = skimage.io.imread(output_files_aggregates["alllabels"], plugin='tifffile')

    # aggregate mask (exclude aggregates outside cells)
    tmp_     = return_mask(labels_agg0, 0)
    mask_agg = exclude_outside_cells(tmp_, labels_cells)

    # connected components for aggregates inside cells
    labels_agg = skimage.morphology.label(mask_agg, connectivity=2)
    if debug:
        skimage.io.imsave(output_files_QoI["LinsideC"], labels_agg, plugin='tifffile')

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
    overlay_cells_agg = np.zeros(np.shape(labels_cells), dtype=np.dtype(float))
    overlay_cells_agg[mask_cell>0] = -1

    # figure: color cells with number of aggregates per cell
    overlay_nagg_per_cell = np.ones(np.shape(labels_cells), dtype=np.dtype(float)) * -1
    overlay_nagg_per_cell[mask_cell>0] = 0


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

    AreaRatioThreshold = 0.1


    # Loop over all aggregates
    for ia, iagg in enumerate(U_AGG):

        # indices of aggregate
        idx_agg = (labels_agg==iagg)   # 2040x2040 T/F

        # total aggregate area
        total_agg_area = np.sum(idx_agg)

        # cell indices/IDs under aggregate
        lbl_cells = labels_cells[idx_agg]  # list of cell Labels
        ID_cells  = np.unique(lbl_cells[lbl_cells>0])
        assert( len(ID_cells) >= 1 ) # assert there is at least one cell under aggregate

        # fraction of aggregate in particular cell, compared to total Aggregate area
        ratio_area_of_agg_split_over_cells = np.zeros(len(ID_cells))  # to find ambiguous aggregates (split over many cells)



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

            # save tif file
            #if debug:
            # MUST CHANGE FILENAME!   skimage.io.imsave("%s/%s_CHECK_segmented_aggID_%04d_over_cells.tif" % (opath, bpath, iagg), tmp_new, plugin='tifffile')



        # loop over cells under aggregate
        for ic, icell in enumerate(ID_cells):

            # area of aggregate over cell `icell`
            agg_area = np.sum(lbl_cells==icell)

            # total area of cell `icell`
            icell_area = np.sum(labels_cells==icell)

            # Fraction of aggregate in particular cell, compared to total Aggregate area
            ratio_area_of_agg_split_over_cells[ic] = agg_area / total_agg_area * 100.

            ratio_of_agg_to_icell_area = agg_area / icell_area * 100.

            if ratio_of_agg_to_icell_area > AreaRatioThreshold:  # consider only aggregates covering more than X% of cell area
                icell_in_U_CELLS = (U_CELLS == icell)
                list_number_of_aggregates_per_cell[icell_in_U_CELLS] += 1
                list_number_of_cells_per_aggregate[ia] += 1

                # for tif image diagnostics:
                overlay_cells_agg[(labels_cells==icell)*(mask_agg==0)] = -2

                # Color cell by number of aggregates per cell
                overlay_nagg_per_cell[(labels_cells==icell)] = list_number_of_aggregates_per_cell[icell_in_U_CELLS]



        if (np.sum(ratio_area_of_agg_split_over_cells)<90) or (np.sum(ratio_area_of_agg_split_over_cells)>101):
            print("Inconsistent sum of ratio_area_of_agg_split_over_cells")
            assert(0)

        # Color by number of cells per aggregate
        overlay_cells_agg[idx_agg] = list_number_of_cells_per_aggregate[ia]



    # save tif image diagnostics
    overlay_cells_agg[mask_cell==0] = 0
    overlay_nagg_per_cell[mask_agg>0] = -2  # comment-out to show only cells
    if debug:
        skimage.io.imsave(output_files_QoI["OvSegCA"], overlay_cells_agg, plugin='tifffile')
        skimage.io.imsave(output_files_QoI["NAggrCell"], overlay_nagg_per_cell, plugin='tifffile')


    # Q4. Percentage of Ambiguous aggregates
    Q.Percentage_Ambiguous_Aggregates = np.sum(list_number_of_cells_per_aggregate>1) / len(U_AGG) * 100.

    # Q1. Percentage of aggregate-positive cells
    Q.Percentage_Of_AggregatePositive_Cells = np.sum(list_number_of_aggregates_per_cell>0) / len(U_CELLS) * 100.

    # Q6. Average Number of Aggregates per aggregate-positive Cell
    Q.Avg_Number_Aggregates_Per_AggPositive_Cell = np.mean( list_number_of_aggregates_per_cell[list_number_of_aggregates_per_cell>0] )

    # Export to data file
    table_file = output_files_QoI["QoI"]
    print("Exporting table to %s" % table_file)
    Q.export_table(table_file)


