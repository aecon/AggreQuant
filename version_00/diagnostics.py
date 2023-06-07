import os
import sys
import glob
import numpy as np
import matplotlib.pyplot as plt
import skimage.io


class Diagnostics(object):

    def __init__(self, Names, debug):
        self.Names = Names
        self.debug = debug



    def _Montage_RandomSelectionZoom_overlay_cells_nuclei_rawcells(self, images_cells, images_nuclei, images_raw):

        if self.debug == True:
            panel_size = [1, 5] # rows, columns
        else:
            panel_size = [8, 16]

        Npixels = 512
        Nspace = 5

        N = panel_size[0] * panel_size[1]
        Nfiles = len(images_cells)
        print(Nfiles)
        if Nfiles < N:
            print("Must have at least %d images!" % (N ) )
            sys.exit(1)

        # random selection of images
        rand = np.random.choice(Nfiles, size=N, replace=False)

        # crop images
        image_deck = []
        for r in rand:
            img0_raw = skimage.io.imread(images_raw[r], plugin='tifffile')
            img0_nuc = skimage.io.imread(images_nuclei[r], plugin='tifffile')
            img0_cel = skimage.io.imread(images_cells[r], plugin='tifffile')
            #print(images_raw[r])
            #print(images_nuclei[r])
            #print(images_cells[r])
            shape = np.shape(img0_raw)
            if len(shape)==2:
                L = shape[0] - Npixels
                P0 = np.random.randint(0, high=L, size=1)[0]

                img = np.zeros((Npixels,Npixels))

                img[:,:] = img0_raw[P0:P0+Npixels, P0:P0+Npixels]

                # nuclei edges
                nucP = img0_nuc[P0:P0+Npixels, P0:P0+Npixels]
                nucP[nucP>0] = 1
                tmp_ = skimage.filters.sobel(nucP)
                img[tmp_>0] = 0

                # cell edges
                celP = img0_cel[P0:P0+Npixels, P0:P0+Npixels]
                celP[celP>0] = 1
                tmp_ = skimage.filters.sobel(celP)
                img[tmp_>0] = 0

            else:
                print("Image shape unsupported. Exiting.")
                sys.exit()
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

        print("Montage tif shape:", np.shape(montage))

        # save montage
        opath = "%s/%s/diagnostics" % ( self.Names.OUTDIR_PATH, self.Names.OUTDIR )
        if not os.path.exists(opath):
            os.makedirs(opath)

        skimage.io.imsave("%s/Composite_montage_overlay_cellraw_celedge_nucedge%dx%d.tif" % (opath, panel_size[0], panel_size[1]), montage, plugin='tifffile')



    def _Montage_RandomSelectionZoom_2imageTypes(self, images_seg, images_raw, outname):

        if self.debug == True:
            panel_size = [1, 10] # rows, columns
        else:
            panel_size = [8, 16]

        assert(panel_size[1]%2 == 0) # Number of columns must be divisible by 2!
        Npixels = 512
        Nspace = 5

        # N is the number of raw images.
        N = panel_size[0] * int(panel_size[1] * 0.5)
        Nfiles = len(images_seg)
        print(Nfiles)
        if Nfiles < N:
            print("Must have at least %d images!" % (N) )
            sys.exit(1)
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

            if len(shape)==3:
                L = shape[1] - Npixels
                P0 = np.random.randint(0, high=L, size=1)[0]
                img_seg = np.zeros((2,Npixels,Npixels))
                img_seg[:,:,:] = img0_seg[:,P0:P0+Npixels, P0:P0+Npixels]
                img_raw = np.zeros((2,Npixels,Npixels))
                img_raw[:,:,:] = img0_raw[:,P0:P0+Npixels, P0:P0+Npixels]
            elif len(shape)==2:
                L = shape[0] - Npixels
                P0 = np.random.randint(0, high=L, size=1)[0]
                img_seg = np.zeros((Npixels,Npixels))
                img_seg[:,:] = img0_seg[P0:P0+Npixels, P0:P0+Npixels]
                img_raw = np.zeros((Npixels,Npixels))
                img_raw[:,:] = img0_raw[P0:P0+Npixels, P0:P0+Npixels]
                IMIN = np.min(img_raw)
                IMAX = np.max(img_raw)
                img_raw = (img_raw-IMIN) / (IMAX-IMIN)
            else:
                print("Image shape unsupported. Exiting.")
                sys.exit()
            image_deck_seg.append(img_seg)
            image_deck_raw.append(img_raw)

        # make montage
        if len(shape)==3:
            montage = np.zeros( (2, panel_size[0]*Npixels+Nspace*(panel_size[0]-1) , panel_size[1]*Npixels+Nspace*(panel_size[1]-1) ) , dtype=np.dtype(float))
            montage[:,:,:] = 65535
        elif len(shape)==2:
            montage = np.zeros( (panel_size[0]*Npixels+Nspace*(panel_size[0]-1) , panel_size[1]*Npixels+Nspace*(panel_size[1]-1) ) , dtype=np.dtype(float))
#            montage[:,:] = 65535

        for i in range(panel_size[0]):      # row
            for j in range(panel_size[1]):  # column
                i0 = i*(Npixels+Nspace)
                i1 = i0 + Npixels
                j0 = j*(Npixels+Nspace)
                j1 = j0 + Npixels
                if j%2==0:  # seg column
                    k =  i*int(0.5*panel_size[1]) + (j//2)
                    if len(shape)==3:
                        montage[:, i0:i1, j0:j1] = image_deck_seg[k][:,:,:]
                    elif len(shape)==2:
                        montage[i0:i1, j0:j1] = image_deck_seg[k][:,:]
                if j%2==1:  # raw column
                    k =  i*int(0.5*panel_size[1]) + (j//2)
                    if len(shape)==3:
                        montage[:, i0:i1, j0:j1] = image_deck_raw[k][:,:,:]
                    elif len(shape)==2:
                        montage[i0:i1, j0:j1] = image_deck_raw[k][:,:]

        print("Montage tif shape:", np.shape(montage))

        # save montage
        opath = "%s/%s/diagnostics" % ( self.Names.OUTDIR_PATH, self.Names.OUTDIR )
        if not os.path.exists(opath):
            os.makedirs(opath)
  
        skimage.io.imsave("%s/Composite_%s_montage_withRaw_%dx%d.tif" % (opath, outname, panel_size[0], panel_size[1]), montage, plugin='tifffile')


    def _Montage_RandomSelectionZoom(self, images, outname):

        if self.debug == True:
            panel_size = [1, 5] # rows, columns
        else:
            panel_size = [8, 16]
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
                img = np.zeros((Npixels,Npixels))
                img[:,:] = img0[0, P0:P0+Npixels, P0:P0+Npixels]
                edges3d = img0[1, P0:P0+Npixels, P0:P0+Npixels]
                img[edges3d>0] = 0

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
        montage = np.zeros( (panel_size[0]*Npixels+Nspace*(panel_size[0]-1) , panel_size[1]*Npixels+Nspace*(panel_size[1]-1) ) , dtype=np.dtype(np.uint16))

        for i in range(panel_size[0]):
            for j in range(panel_size[1]):
                i0 = i*(Npixels+Nspace)
                i1 = i0 + Npixels
                j0 = j*(Npixels+Nspace)
                j1 = j0 + Npixels
                k = i*(panel_size[1]) + j
                montage[i0:i1, j0:j1] = image_deck[k][:,:]

        print("Montage tif shape:", np.shape(montage))

        # save montage
        opath = "%s/%s/diagnostics" % ( self.Names.OUTDIR_PATH, self.Names.OUTDIR )
        if not os.path.exists(opath):
            os.makedirs(opath)
  
        skimage.io.imsave("%s/Composite_%s_montage%dx%d.tif" % (opath, outname, panel_size[0], panel_size[1]), montage, plugin='tifffile')



    def Montage_nuclei_RandomSelectionZoom(self):
        images = glob.glob("%s/%s/nuclei/*%s.tif" % (self.Names.OUTDIR_PATH, self.Names.OUTDIR, self.Names.COMPOSITE_RAW_NUCLEI_EDGES))
        self._Montage_RandomSelectionZoom(images, "nuclei")


    def Montage_cells_RandomSelectionZoom(self):
        images_raw = sorted(glob.glob("%s/*%s*.tif" % (self.Names.OUTDIR_PATH, self.Names.COLOR_CELLS)))
        images_composite = sorted(glob.glob("%s/%s/%s/*%s.tif" % (self.Names.OUTDIR_PATH, self.Names.OUTDIR, self.Names.CELLBODY_ODIR_NAME, self.Names.COMPOSITE_CELLS_AND_NUCLEI)))
        images_cells     = sorted(glob.glob("%s/%s/%s/*%s.tif" % (self.Names.OUTDIR_PATH, self.Names.OUTDIR, self.Names.CELLBODY_ODIR_NAME, "cellbodies_labels")))
        images_nuclei    = sorted(glob.glob("%s/%s/%s/*%s.tif" % (self.Names.OUTDIR_PATH, self.Names.OUTDIR, self.Names.CELLBODY_ODIR_NAME, "corresponding_nuclei")))

#        self._Montage_RandomSelectionZoom(images_composite, "cells")
#        self._Montage_RandomSelectionZoom_2imageTypes(images_composite, images_raw, "cells")

        self._Montage_RandomSelectionZoom_overlay_cells_nuclei_rawcells(images_cells, images_nuclei, images_raw)





#-------- FOR LATER ---------
#
#class Montage(Diagnostics):
#    def __init__(self):
#        super().__init__(  name, attitude, behaviour, face  )
#


