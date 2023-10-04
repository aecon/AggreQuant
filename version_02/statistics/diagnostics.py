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
    skimage.io.imsave("%s_montage%dx%d.tif" % (output_filename, panel_size[0], panel_size[1]), montage, plugin='tifffile')




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
    skimage.io.imsave("%s_%dx%d.tif" % (output_filename, panel_size[0], panel_size[1]), montage, plugin='tifffile', imagej=True)


def montage_overlay_two_images_validation(images_raw, images_seg, output_filename):

    assert(len(images_seg) == len(images_raw))

    Nfiles = len(images_raw)
    Ncolumns = 5
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
    skimage.io.imsave("%s_%dx%d.tif" % (output_filename, panel_size[0], panel_size[1]), montage, plugin='tifffile', imagej=True)
