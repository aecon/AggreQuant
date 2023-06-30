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

    assert(panel_size[1]%2 == 0) # Number of columns must be divisible by 2!
    Npixels = 512
    Nspace = 5

    # N is the number of raw images.
    N = panel_size[0] * int(panel_size[1] * 0.5)
    if Nfiles < N:
        print("Must have at least %d images!" % (N) )
        sys.exit(1)

    print("Nraw", len(images_raw))
    print("Nraw", len(images_raw))
    assert(len(images_seg) == len(images_raw))

    # random selection of images
    rand = np.random.choice(Nfiles, size=N, replace=False)

    # crop images
    image_deck_seg = []
    image_deck_raw = []
    for r in rand:
        img0_seg = skimage.io.imread(images_seg[r], plugin='tifffile')
        img0_seg[img0_seg>0] = 1

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
        IMIN = np.min(img_raw)
        IMAX = np.max(img_raw)
        img_raw = (img_raw-IMIN) / (IMAX-IMIN)
        image_deck_seg.append(img_seg)
        image_deck_raw.append(img_raw)

    # make montage
    montage = np.zeros( (panel_size[0]*Npixels+Nspace*(panel_size[0]-1) , panel_size[1]*Npixels+Nspace*(panel_size[1]-1) ) , dtype=np.dtype(float))

    for i in range(panel_size[0]):      # row
        for j in range(panel_size[1]):  # column
            i0 = i*(Npixels+Nspace)
            i1 = i0 + Npixels
            j0 = j*(Npixels+Nspace)
            j1 = j0 + Npixels
            if j%2==0:  # seg column
                k =  i*int(0.5*panel_size[1]) + (j//2)
                montage[i0:i1, j0:j1] = image_deck_seg[k][:,:]
            if j%2==1:  # raw column
                k =  i*int(0.5*panel_size[1]) + (j//2)
                montage[i0:i1, j0:j1] = image_deck_raw[k][:,:]

    if verbose:
        print("Montage tif shape:", np.shape(montage))

    # save montage
    skimage.io.imsave("%s_%dx%d.tif" % (output_filename, panel_size[0], panel_size[1]), montage, plugin='tifffile')


