import os
import sys
import glob
import numpy as np
import matplotlib.pyplot as plt
import skimage.io


class Diagnostics(object):

    def __init__(self, Names):
        self.Names = Names


    def Montage_RandomSelectionZoom(self):

        # find list Composite images: Raw / Edges
        images = glob.glob("%s/%s/nuclei/*%s.tif" % (self.Names.OUTDIR_PATH, self.Names.OUTDIR, self.Names.COMPOSITE_RAW_NUCLEI_EDGES))

        panel_size = [8, 16] # rows, columns
        Npixels = 512
        Nspace = 5

        N = panel_size[0] * panel_size[1]
        Nfiles = len(images)
        print(Nfiles)
        if Nfiles < N:
            print("Must have at least %d `%s.tif` images inside folder `%s`!" % (N, self.Names.COMPOSITE_RAW_NUCLEI_EDGES, self.Names.OUTDIR ) )
            sys.exit(1)

        # random selection of images
        rand = np.random.choice(Nfiles, size=N, replace=False)

        # crop images
        image_deck = []
        for r in rand:
            img0 = skimage.io.imread(images[r], plugin='tifffile')
            shape = np.shape(img0)
            L = shape[1] - Npixels
            P0 = np.random.randint(0, high=L, size=1)[0]
            img = np.zeros((2,Npixels,Npixels))
            img[:,:,:] = img0[:,P0:P0+Npixels, P0:P0+Npixels]
            image_deck.append(img)

        # make montage
        montage = np.zeros( (2, panel_size[0]*Npixels+Nspace*(panel_size[0]-1) , panel_size[1]*Npixels+Nspace*(panel_size[1]-1) ) , dtype=np.dtype(np.uint16))
        montage[:,:,:] = 65535
        for i in range(panel_size[0]):
            for j in range(panel_size[1]):
                i0 = i*(Npixels+Nspace)
                i1 = i0 + Npixels
                j0 = j*(Npixels+Nspace)
                j1 = j0 + Npixels
                k = i*(panel_size[1]) + j
                montage[:, i0:i1, j0:j1] = image_deck[k][:,:,:]

        print("Montage tif shape:", np.shape(montage))

        # save montage
        opath = "%s/%s/diagnostics" % ( self.Names.OUTDIR_PATH, self.Names.OUTDIR )
        if not os.path.exists(opath):
            os.makedirs(opath)
  
        skimage.io.imsave("%s/Composite_raw_edges_montage%dx%d.tif" % (opath, panel_size[0], panel_size[1]), montage, plugin='tifffile')





#-------- FOR LATER ---------
#
#class Montage(Diagnostics):
#    def __init__(self):
#        super().__init__(  name, attitude, behaviour, face  )
#


