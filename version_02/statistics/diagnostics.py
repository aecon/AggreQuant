import os
import sys
import glob
import numpy as np
import matplotlib.pyplot as plt
import skimage.io



def montage_simple(image_list, output_filename, debug=False, verbose=False):

    Nfiles = len(image_list)

    if debug:
        panel_size = [1, Nfiles] # rows, columns
    else:
        panel_size = [8, 16]
    Npixels = 512
    Nspace = 5

    N = panel_size[0] * panel_size[1]
    if Nfiles < N:
        print("Must have at least %d images!" % (N ) )
        sys.exit(1)

    # random selection of images
    rand = np.random.choice(Nfiles, size=N, replace=False)

    # crop images
    image_deck = []
    for r in rand:
        img0 = skimage.io.imread(image_list[r], plugin='tifffile')
        shape = np.shape(img0)
        L = shape[0] - Npixels
        P0 = np.random.randint(0, high=L, size=1)[0]
        img = np.zeros((Npixels,Npixels))
        img[:,:] = img0[P0:P0+Npixels, P0:P0+Npixels]
        image_deck.append(img)

    # make montage
    montage = np.zeros( (panel_size[0]*Npixels+Nspace*(panel_size[0]-1) , panel_size[1]*Npixels+Nspace*(panel_size[1]-1) ) , dtype=np.dtype(np.uint16))
    for i in range(panel_size[0]):
        for j in range(panel_size[1]):
            i0 = i*(Npixels+Nspace)
            i1 = i0 + Npixels
            j0 = j*(Npixels+Nspace)
            j1 = j0 + Npixels
            k = i*(panel_size[1]) + j
            montage[i0:i1, j0:j1] = image_deck[k][:,:]

    if verbose:
        print("Montage tif shape:", np.shape(montage))

    # save montage
    skimage.io.imsave("%s_montage%dx%d.tif" % (output_filename, panel_size[0], panel_size[1]), montage, plugin='tifffile', check_contrast=False)




def montage_overlay_two_images(images_raw, images_seg, output_filename, debug=False, verbose=False):

    Nfiles = len(images_raw)

    if debug:
        panel_size = [1, Nfiles] # rows, columns
    else:
        panel_size = [8, 16]
    Npixels = 768
    Nspace = 5

    N = panel_size[0] * panel_size[1]
    if Nfiles < N:
        print("Must have at least %d images!" % (N ) )
        sys.exit(1)

    # random selection of images
    rand = np.random.choice(Nfiles, size=N, replace=False)

    print("Nraw", len(images_raw))
    print("Nseg", len(images_seg))
    assert(len(images_seg) == len(images_raw))

    # random selection of images
    rand = np.random.choice(Nfiles, size=N, replace=False)

    # crop images
    image_deck_seg = []
    image_deck_raw = []
    for r in rand:
        img0_seg = skimage.io.imread(images_seg[r], plugin='tifffile')
        img0_seg[img0_seg>0] = 1
        # reconstruct edges from nuclei seeds
        mask = np.zeros(np.shape(img0_seg))
        mask[img0_seg>0] = 1
        edges0 = skimage.filters.sobel(mask)
        img0_seg = np.zeros(np.shape(edges0), dtype=np.dtype(np.uint8))
        img0_seg[edges0>0] = 1

        img0_raw = skimage.io.imread(images_raw[r], plugin='tifffile')

        print(images_seg[r], images_raw[r])

        assert(np.sum(np.shape(img0_seg)) == np.sum(np.shape(img0_raw)))
        shape = np.shape(img0_seg)
        L = shape[0] - Npixels
        P0 = np.random.randint(0, high=L, size=1)[0]
        img_seg = np.zeros((Npixels,Npixels))
        img_seg[:,:] = img0_seg[P0:P0+Npixels, P0:P0+Npixels]
        img_raw = np.zeros((Npixels,Npixels))
        img_raw[:,:] = img0_raw[P0:P0+Npixels, P0:P0+Npixels]

#        IMIN = np.min(img_raw)
#        IMAX = np.max(img_raw)
#        img_raw = (img_raw-IMIN) / (IMAX-IMIN)

        image_deck_seg.append(img_seg)
        image_deck_raw.append(img_raw)

    # make montage
    montage = np.zeros((2, panel_size[0]*Npixels+Nspace*(panel_size[0]-1) , panel_size[1]*Npixels+Nspace*(panel_size[1]-1) ) , dtype=np.dtype(np.uint16))
    for i in range(panel_size[0]):
        for j in range(panel_size[1]):
            i0 = i*(Npixels+Nspace)
            i1 = i0 + Npixels
            j0 = j*(Npixels+Nspace)
            j1 = j0 + Npixels
            k = i*(panel_size[1]) + j
            #tile = image_deck_raw[k][:,:]
            #tile_s = image_deck_seg[k][:,:]
            #tile[tile_s==1] = 65000
            montage[0, i0:i1, j0:j1] = image_deck_raw[k][:,:]
            montage[1, i0:i1, j0:j1] = image_deck_seg[k][:,:]

    if verbose:
        print("Montage tif shape:", np.shape(montage))

    # save montage
    skimage.io.imsave("%s_%dx%d.tif" % (output_filename, panel_size[0], panel_size[1]), montage, plugin='tifffile', imagej=True, check_contrast=False)


def montage_overlay_6Channels_validation(images_raw_nuclei, images_seg_nuclei, 
    images_raw_cells, images_seg_cells,
    images_raw_agg, images_seg_agg,
    output_filename):

    assert(len(images_seg_nuclei) == len(images_raw_cells))
    assert(len(images_seg_cells) == len(images_seg_agg))

    Nfiles = len(images_raw_nuclei)
    Ncolumns = 7
    Nrows = int(np.ceil(Nfiles / Ncolumns))
    panel_size = [Nrows, Ncolumns]

    Npixels = 768
    Nspace = 5

    N = panel_size[0] * panel_size[1]

    # crop images
    image_deck_seg_nuc = []
    image_deck_raw_nuc = []
    image_deck_seg_cel = []
    image_deck_raw_cel = []
    image_deck_seg_agg = []
    image_deck_raw_agg = []
    for r in range(len(images_raw_nuclei)):
        img0_seg_nuc = skimage.io.imread(images_seg_nuclei[r], plugin='tifffile')
        img0_seg_cel = skimage.io.imread(images_seg_cells[r], plugin='tifffile')
        img0_seg_agg = skimage.io.imread(images_seg_agg[r], plugin='tifffile')
        img0_seg_nuc[img0_seg_nuc>0] = 1
        img0_seg_cel[img0_seg_cel>0] = 1
        img0_seg_agg[img0_seg_agg>0] = 1
        
        img0_raw_nuc = skimage.io.imread(images_raw_nuclei[r], plugin='tifffile')
        img0_raw_cel = skimage.io.imread(images_raw_cells[r], plugin='tifffile')
        img0_raw_agg = skimage.io.imread(images_raw_agg[r], plugin='tifffile')

        assert(np.sum(np.shape(img0_seg_nuc)) == np.sum(np.shape(img0_raw_nuc)))
        assert(np.sum(np.shape(img0_seg_cel)) == np.sum(np.shape(img0_raw_cel)))
        assert(np.sum(np.shape(img0_seg_agg)) == np.sum(np.shape(img0_raw_agg)))

        shape = np.shape(img0_seg_nuc)
        L = shape[0] - Npixels
        P0 = np.random.randint(0, high=L, size=1)[0]

        img_seg_nuc = np.zeros((Npixels,Npixels))
        img_raw_nuc = np.zeros((Npixels,Npixels))
        img_seg_cel = np.zeros((Npixels,Npixels))
        img_raw_cel = np.zeros((Npixels,Npixels))
        img_seg_agg = np.zeros((Npixels,Npixels))
        img_raw_agg = np.zeros((Npixels,Npixels))
        
        img_seg_nuc[:,:] = img0_seg_nuc[P0:P0+Npixels, P0:P0+Npixels]
        img_raw_nuc[:,:] = img0_raw_nuc[P0:P0+Npixels, P0:P0+Npixels]
        img_seg_cel[:,:] = img0_seg_cel[P0:P0+Npixels, P0:P0+Npixels]
        img_raw_cel[:,:] = img0_raw_cel[P0:P0+Npixels, P0:P0+Npixels]
        img_seg_agg[:,:] = img0_seg_agg[P0:P0+Npixels, P0:P0+Npixels]
        img_raw_agg[:,:] = img0_raw_agg[P0:P0+Npixels, P0:P0+Npixels]

        image_deck_seg_nuc.append(img_seg_nuc)
        image_deck_raw_nuc.append(img_raw_nuc)
        image_deck_seg_cel.append(img_seg_cel)
        image_deck_raw_cel.append(img_raw_cel)
        image_deck_seg_agg.append(img_seg_agg)
        image_deck_raw_agg.append(img_raw_agg)

    # make montage
    montage = np.zeros((6, panel_size[0]*Npixels+Nspace*(panel_size[0]-1) , panel_size[1]*Npixels+Nspace*(panel_size[1]-1) ) , dtype=np.dtype(np.uint16))
    for i in range(panel_size[0]):
        for j in range(panel_size[1]):
            i0 = i*(Npixels+Nspace)
            i1 = i0 + Npixels
            j0 = j*(Npixels+Nspace)
            j1 = j0 + Npixels
            k = i*(panel_size[1]) + j

            montage[0, i0:i1, j0:j1] = image_deck_raw_nuc[k][:,:]
            montage[1, i0:i1, j0:j1] = image_deck_seg_nuc[k][:,:]
            montage[2, i0:i1, j0:j1] = image_deck_raw_cel[k][:,:]
            montage[3, i0:i1, j0:j1] = image_deck_seg_cel[k][:,:]
            montage[4, i0:i1, j0:j1] = image_deck_raw_agg[k][:,:]
            montage[5, i0:i1, j0:j1] = image_deck_seg_agg[k][:,:]

    # save montage
    skimage.io.imsave("%s_%dx%d.tif" % (output_filename, panel_size[0], panel_size[1]), montage, plugin='tifffile', imagej=True, check_contrast=False)

def montage_overlay_two_images_validation(images_raw, images_seg, output_filename):

    assert(len(images_seg) == len(images_raw))

    Nfiles = len(images_raw)
    Ncolumns = 7
    Nrows = int(np.ceil(Nfiles / Ncolumns))
    panel_size = [Nrows, Ncolumns]

    Npixels = 768
    Nspace = 5

    N = panel_size[0] * panel_size[1]

    # crop images
    image_deck_seg = []
    image_deck_raw = []
    for r in range(len(images_raw)):
        img0_seg = skimage.io.imread(images_seg[r], plugin='tifffile')
        img0_seg[img0_seg>0] = 1
        # reconstruct edges from nuclei seeds
        mask = np.zeros(np.shape(img0_seg))
        mask[img0_seg>0] = 1
        edges0 = skimage.filters.sobel(mask)
        img0_seg = np.zeros(np.shape(edges0), dtype=np.dtype(np.uint8))
        img0_seg[edges0>0] = 1

        img0_raw = skimage.io.imread(images_raw[r], plugin='tifffile')
        assert(np.sum(np.shape(img0_seg)) == np.sum(np.shape(img0_raw)))
        shape = np.shape(img0_seg)
        L = shape[0] - Npixels
        P0 = np.random.randint(0, high=L, size=1)[0]
        img_seg = np.zeros((Npixels,Npixels))
        img_seg[:,:] = img0_seg[P0:P0+Npixels, P0:P0+Npixels]
        img_raw = np.zeros((Npixels,Npixels))
        img_raw[:,:] = img0_raw[P0:P0+Npixels, P0:P0+Npixels]

#        IMIN = np.min(img_raw)
#        IMAX = np.max(img_raw)
#        img_raw = (img_raw-IMIN) / (IMAX-IMIN)

        image_deck_seg.append(img_seg)
        image_deck_raw.append(img_raw)

    # make montage
    montage = np.zeros((2, panel_size[0]*Npixels+Nspace*(panel_size[0]-1) , panel_size[1]*Npixels+Nspace*(panel_size[1]-1) ) , dtype=np.dtype(np.uint16))
    for i in range(panel_size[0]):
        for j in range(panel_size[1]):
            i0 = i*(Npixels+Nspace)
            i1 = i0 + Npixels
            j0 = j*(Npixels+Nspace)
            j1 = j0 + Npixels
            k = i*(panel_size[1]) + j
            #tile = image_deck_raw[k][:,:]
            #tile_s = image_deck_seg[k][:,:]
            #tile[tile_s==1] = 65000
            montage[0, i0:i1, j0:j1] = image_deck_raw[k][:,:]
            montage[1, i0:i1, j0:j1] = image_deck_seg[k][:,:]

    # save montage
    skimage.io.imsave("%s_%dx%d.tif" % (output_filename, panel_size[0], panel_size[1]), montage, plugin='tifffile', imagej=True, check_contrast=False)
