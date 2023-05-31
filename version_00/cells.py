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

from filenames import Filenames
from diagnostics import Diagnostics


# not needed ..
# parser = argparse.ArgumentParser()
# parser.add_argument('-i', type=str, required=True, nargs='+', help="2D tif images")
# parser.add_argument('-o', type=str, required=True, help="output directory name")
# args = parser.parse_args()


def scale_values_01_float(img):
    """
    Return image with values scaled between 0 and 1
    """
    IMIN = np.min(img)
    IMAX = np.max(img)

    img1 = (img-IMIN)/(IMAX-IMIN)
    img2 = np.asarray(img1, dtype=float)

    scale = np.asarray([IMIN, IMAX])

    return img2, scale


def segment_cellpose():
    print("TODO")
    assert(0)
    nuclei_paths = ""
    for f in images_nuclei:
        nuclei_paths+=" '%s'" % f
    os.system( "conda run -n cellpose python cells_cp.py -o %s -i %s" % (Names.OUTDIR, nuclei_paths) ) ### CHECK THE PATHS !!!!


def segment_distance_map(image_file, seeds_file, opath):

    # TODO:
    # > compute average intensity of image. Proceed based on average intensity ..

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
    img11, scale = scale_values_01_float(img1)
    #print("After scaling 0/1 (float):", np.min(img11), np.max(img11))
    img2 = skimage.exposure.equalize_adapthist(img11, kernel_size=150)
    #print("After CLAHE:", np.min(img2), np.max(img2))

    IMIN = scale[0]
    IMAX = scale[1]
    cells_area = img2*(IMAX-IMIN)+IMIN

    cell_mask = np.zeros(np.shape(cells_area))
    cell_mask[cells_area>1.5] = 1
    plt.imshow(cell_mask)
    plt.show()

    # 2. SPLIT CELL MASK BASED on NUCLEI SEEDS
    # load image and convert to float
    seeds = skimage.io.imread(seeds_file, plugin='tifffile')  # uint8
    # compute distances to seeds
    distances = ndimage.distance_transform_edt(1-seeds)  # float64
    plt.imshow(distances)
    plt.show()
    # watershed of distance map
    labels = watershed(distances, mask=cell_mask, watershed_line=True)
    plt.imshow(labels)
    plt.show()

    edges = np.zeros(np.shape(labels))
    edges[labels==0] = 1
    fat_edges = skimage.morphology.binary_dilation(edges)

    AllLabels = np.unique(labels[labels>0])
    for l in AllLabels:
        idx = labels==l
        is_seed = np.sum(seeds[idx])
        if is_seed < 100:
            labels[idx] = 0
            print("No seed for label", l)

    plt.imshow(labels)
    plt.show()

    # Assign a cell area to each nucleus
    nuclei_labels = np.zeros(np.shape(labels))
    nuclei_labels[labels>0] = labels[labels>0]
    nuclei_labels[seeds==0] = 0
    plt.imshow(nuclei_labels)
    plt.imshow(fat_edges)
    plt.show()


"""
0. load original (cell boundary)
1. duplicate
    smooth: s=2
    CLAHE
    intensity mask using Minimum Error Auto-threshold
    => Now we have a mask of original cells in space.
2. duplicate original
    smooth: s=2
3. duplicate original
    smooth: s=20 --> background: want to remove bright intensities from nucleus
4. Image Calculator: divise s2 / s20
    CLAHE. (here intensity >0.6 shows definitely cells)

Alternative watershed field:
5a. Use last CLAHE'd image. Blur with sigma=6.
5. Convert to 16bit. Equalize Histogram (Only Normalize)
6. Convert to 8bit. Invert (Edit/Invert)
7. Make holes where there are nuclei:
    Image Calculator: inverted Nucleus mask AND Inverted CLAHE etc intensity filed from last step.
8. Do watershed on last field.
9. Clean up:
    Remove basins with no nucleus inside them.
    Remove areas that correspond to excluded nuclei
10. Erode wateshed Lines!!
"""


def segment_intensity_map():
    print("TODO")


def segment_propagation():
    print("TODO")


def cellbody_segmentation(cellbody_images, Names):


    opath = "%s/%s" % ( Names.OUTDIR_PATH, Names.OUTDIR)
    if not os.path.exists(opath):
        print("Path %s does NOT exist. Creating now. " % opath)
        os.makedirs(opath)
    else:
        print("Path %s exists." % opath)

    segmentation_algorithm = Names.CELLBODY_SEGMENTATION_TYPE
    print("Segmenting cell bodies with algorithm:", segmentation_algorithm)

    for ifile, image_file in enumerate(cellbody_images):

        bpath = os.path.basename(image_file)
        print(">> Processing image: %s" % bpath)

        # find corresponding nuclei seeds
        seeds_file = "%s/%s/%s%s).tif_seeds_nuclei.tif" % (Names.OUTDIR_PATH, Names.OUTDIR, bpath.split(Names.COLOR_CELLS,1)[0], Names.COLOR_NUCLEI)
        if not os.path.isfile(seeds_file):
            print("Nuclei Seeds for file %s do NOT exist!", bpath)
            sys.exit()

        # Choose segmentation algorithm for cellbodies
        if segmentation_algorithm == "distance":
            segment_distance_map(image_file, seeds_file, opath)
        elif segmentation_algorithm == "intensity":
            segment_intensity_map()
        elif segmentation_algorithm == "propagation":
            segment_propagation()
        elif segmentation_algorithm == "cellpose":
            segment_cellpose()
        else:
            print("Segmentation algorithm %s not defined." % segmentation_algorithm)
            assert(0)


        assert(0)


