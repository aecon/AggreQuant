import os
import sys
import glob
import numpy as np
import matplotlib.pyplot as plt
import skimage.io


class Diagnostics(object):

    def __init__(self, Names):
        self.Names = Names


    def Montage_RandomSelectionZoom_2imageTypes(self, images, images_raw, outname):

        panel_size = [8, 16] # rows, columns
        Npixels = 512
        Nspace = 5

        N = int(panel_size[0] * panel_size[1] * 0.5)
        Nfiles = len(images)
        print(Nfiles)
        if Nfiles < N:
            print("Must have at least %d images!" % (N) )
            sys.exit(1)

        # random selection of images
        rand = np.random.choice(Nfiles, size=N, replace=False)

        # crop images
        image_deck = []
        image_deck_raw = []
        for r in rand:
            img0 = skimage.io.imread(images[r], plugin='tifffile')
            img0[img0>0] = 1
            img0_raw = skimage.io.imread(images_raw[r], plugin='tifffile')
            shape = np.shape(img0)

            if len(shape)==3:
                L = shape[1] - Npixels
                P0 = np.random.randint(0, high=L, size=1)[0]
                img = np.zeros((2,Npixels,Npixels))
                img[:,:,:] = img0[:,P0:P0+Npixels, P0:P0+Npixels]
                img_raw = np.zeros((2,Npixels,Npixels))
                img_raw[:,:,:] = img0_raw[:,P0:P0+Npixels, P0:P0+Npixels]
            elif len(shape)==2:
                L = shape[0] - Npixels
                P0 = np.random.randint(0, high=L, size=1)[0]
                img = np.zeros((Npixels,Npixels))
                img[:,:] = img0[P0:P0+Npixels, P0:P0+Npixels]
                img_raw = np.zeros((Npixels,Npixels))
                img_raw[:,:] = img0_raw[P0:P0+Npixels, P0:P0+Npixels]
            else:
                print("Image shape unsupported. Exiting.")
                sys.exit()
            image_deck.append(img)
            image_deck_raw.append(img_raw)

        # make montage
        if len(shape)==3:
            montage = np.zeros( (2, panel_size[0]*Npixels+Nspace*(panel_size[0]-1) , panel_size[1]*Npixels+Nspace*(panel_size[1]-1) ) , dtype=np.dtype(np.uint16))
            montage[:,:,:] = 65535
        elif len(shape)==2:
            montage = np.zeros( (panel_size[0]*Npixels+Nspace*(panel_size[0]-1) , panel_size[1]*Npixels+Nspace*(panel_size[1]-1) ) , dtype=np.dtype(np.uint16))
#            montage[:,:] = 65535

        for i in range(panel_size[0]):
            for j in range(panel_size[1]):
                i0 = i*(Npixels+Nspace)
                i1 = i0 + Npixels
                j0 = j*(Npixels+Nspace)
                j1 = j0 + Npixels
                k =  i*(panel_size[1]) + j
                if j%2==0:
                    if len(shape)==3:
                        montage[:, i0:i1, j0:j1] = image_deck[k][:,:,:]
                    elif len(shape)==2:
                        print(i0, i1, j0, j1, k)
                        montage[i0:i1, j0:j1] = image_deck[k//2][:,:]
                if j%2==1:
                    if len(shape)==3:
                        montage[:, i0:i1, j0:j1] = image_deck_raw[k][:,:,:]
                    elif len(shape)==2:
                        print(i0, i1, j0, j1, k)
                        montage[i0:i1, j0:j1] = image_deck_raw[k//2][:,:]

        # Normalize montage image
        IMEAN = np.mean(montage[:,int(0.5*panel_size[1])*(Npixels+Nspace)::])
        montage[:,0:int(0.5*panel_size[1])*(Npixels+Nspace)] *= int(1.3*IMEAN)

        print("Montage tif shape:", np.shape(montage))

        # save montage
        opath = "%s/%s/diagnostics" % ( self.Names.OUTDIR_PATH, self.Names.OUTDIR )
        if not os.path.exists(opath):
            os.makedirs(opath)
  
        skimage.io.imsave("%s/Composite_%s_montage_withRaw_%dx%d.tif" % (opath, outname, panel_size[0], panel_size[1]), montage, plugin='tifffile')


    def Montage_RandomSelectionZoom(self, images, outname):

        panel_size = [8, 16] # rows, columns
        Npixels = 512
        Nspace = 5

        N = panel_size[0] * panel_size[1]
        Nfiles = len(images)
        print(Nfiles)
        if Nfiles < N:
            print("Must have at least %d images!" % (N ) )
            sys.exit(1)

        # random selection of images
        rand = np.random.choice(Nfiles, size=N, replace=False)

        # crop images
        image_deck = []
        for r in rand:
            img0 = skimage.io.imread(images[r], plugin='tifffile')
            shape = np.shape(img0)

            if len(shape)==3:
                L = shape[1] - Npixels
                P0 = np.random.randint(0, high=L, size=1)[0]
                img = np.zeros((2,Npixels,Npixels))
                img[:,:,:] = img0[:,P0:P0+Npixels, P0:P0+Npixels]
            elif len(shape)==2:
                L = shape[0] - Npixels
                P0 = np.random.randint(0, high=L, size=1)[0]
                img = np.zeros((Npixels,Npixels))
                img[:,:] = img0[P0:P0+Npixels, P0:P0+Npixels]
            else:
                print("Image shape unsupported. Exiting.")
                sys.exit()
            image_deck.append(img)

        # make montage
        if len(shape)==3:
            montage = np.zeros( (2, panel_size[0]*Npixels+Nspace*(panel_size[0]-1) , panel_size[1]*Npixels+Nspace*(panel_size[1]-1) ) , dtype=np.dtype(np.uint16))
            montage[:,:,:] = 65535
        elif len(shape)==2:
            montage = np.zeros( (panel_size[0]*Npixels+Nspace*(panel_size[0]-1) , panel_size[1]*Npixels+Nspace*(panel_size[1]-1) ) , dtype=np.dtype(np.uint16))
#            montage[:,:] = 65535

        for i in range(panel_size[0]):
            for j in range(panel_size[1]):
                i0 = i*(Npixels+Nspace)
                i1 = i0 + Npixels
                j0 = j*(Npixels+Nspace)
                j1 = j0 + Npixels
                k = i*(panel_size[1]) + j
                if len(shape)==3:
                    montage[:, i0:i1, j0:j1] = image_deck[k][:,:,:]
                elif len(shape)==2:
                    montage[i0:i1, j0:j1] = image_deck[k][:,:]

        print("Montage tif shape:", np.shape(montage))

        # save montage
        opath = "%s/%s/diagnostics" % ( self.Names.OUTDIR_PATH, self.Names.OUTDIR )
        if not os.path.exists(opath):
            os.makedirs(opath)
  
        skimage.io.imsave("%s/Composite_%s_montage%dx%d.tif" % (opath, outname, panel_size[0], panel_size[1]), montage, plugin='tifffile')


    def Montage_nuclei_RandomSelectionZoom(self):
        images = glob.glob("%s/%s/nuclei/*%s.tif" % (self.Names.OUTDIR_PATH, self.Names.OUTDIR, self.Names.COMPOSITE_RAW_NUCLEI_EDGES))
        self.Montage_RandomSelectionZoom(images, "nuclei")


    def Montage_cells_RandomSelectionZoom(self):
        images = glob.glob("%s/%s/cellbodies/*%s.tif" % (self.Names.OUTDIR_PATH, self.Names.OUTDIR, self.Names.COMPOSITE_CELLS_AND_NUCLEI))
        self.Montage_RandomSelectionZoom(images, "cells")

        images_raw = glob.glob("%s/*%s*.tif" % (self.Names.OUTDIR_PATH, self.Names.COLOR_CELLS))
        self.Montage_RandomSelectionZoom_2imageTypes(images, images_raw, "cells")




#-------- FOR LATER ---------
#
#class Montage(Diagnostics):
#    def __init__(self):
#        super().__init__(  name, attitude, behaviour, face  )
#


