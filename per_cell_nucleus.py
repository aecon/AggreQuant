import os
import sys
import numpy as np
import argparse
import skimage.io
import skimage.filters
import scipy.ndimage


parser = argparse.ArgumentParser()
parser.add_argument('-n', type=str, required=True, nargs='+', help="tif, labels nuclei")
parser.add_argument('-c', type=str, required=True, nargs='+', help="tif, labels cells")
parser.add_argument('-a', type=str, required=True, nargs='+', help="tif, labels aggregates")
args = parser.parse_args()


for fnuc, fcel, fagg in zip(args.n, args.c, args.a):

    # load labels images
    nuc = skimage.io.imread(fnuc, plugin='tifffile')
    cel = skimage.io.imread(fcel, plugin='tifffile')
    agg = skimage.io.imread(fagg, plugin='tifffile')

    # clean cell labels (keep the ones with a nucleus inside)
    Ncel = np.shape(np.unique(cel))[0]
    cells_to_nuclei = np.zeros(np.shape(cel), dtype=np.uint32)
    for i in range(1,Ncel):
        idx = (cel==i)
        Vcell = np.sum(nuc[idx])
        if Vcell==0:
            cel[idx] = 0
        else:
            # assign cell to nucleus
            labels = nuc[idx]
            unique_nuclei, unique_counts = np.unique(labels, return_counts=True)
            idm = np.argmax(unique_counts)
            nucid = unique_nuclei[idm]             
            cells_to_nuclei[idx] = nucid

    # assign aggregates to cells
    Nagg = np.shape(np.unique(agg))[0]
    aggregates_to_nuclei = np.zeros(np.shape(agg), dtype=np.uint32)
    for i in range(1,Nagg):
        idx = (agg==i)
        Vcell = np.sum(cel[idx])
        # if the aggregates are not in a cell, ignore them
        if Vcell>0:
            labels = nuc[idx]
            unique_nuclei, unique_counts = np.unique(labels, return_counts=True)
            idm = np.argmax(unique_counts)
            nucid = unique_nuclei[idm]
            aggregates_to_nuclei[idx] = nucid 

    # save 
    opath = "%s" % os.path.dirname(fagg)
    if not os.path.exists(opath):
        os.makedirs(opath)
    # aggregates per cell
    labels = np.asarray(aggregates_to_nuclei, dtype=np.uint32)
    bpath = os.path.basename(fagg)
    skimage.io.imsave("%s/%s_aggregates_per_cell.tif" % (opath, bpath), labels, plugin='tifffile')
    # cell per nucleus
    labels = np.asarray(cells_to_nuclei, dtype=np.uint32)
    bpath = os.path.basename(fcel)
    skimage.io.imsave("%s/%s_cell_per_nucleus.tif" % (opath, bpath), labels, plugin='tifffile')

