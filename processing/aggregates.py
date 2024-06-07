import os
import sys
import numpy as np
import skimage.io
import skimage.filters
import scipy.ndimage
import tifffile
import matplotlib.pyplot as plt
import tensorflow as tf


# Image segmentation parameters

median_filter_size = 4      # applied after segmentation to regularize shape
sigma_noise_reduction = 1   # applied on normalized data to reduce digitization noise
sigma_background = 20       # used to generate a model of background illumination
intensity_cap=3500          # used to cap intensity for background estimation
normalized_intensity_threshold=1.60 # threshold on normalized intensity to generate segmentation
small_hole_area_threshold=6000 # fill holes in segmented data that are smaller than this threshold
min_aggreagte_area=9        # ignore segmented objects smaller than this threshold



def segment_aggregates_filters(image_file, output_files_aggregates, verbose, debug):

    # load image
    img = skimage.io.imread(image_file, plugin='tifffile')
    if debug:
        print(np.median(img), np.min(img), np.max(img))

    # cap intensity values only for background intensity estimation
    threshold = intensity_cap  #np.percentile(img, 98)
    if debug:
        print("threshold:", threshold)
    capped = np.zeros(np.shape(img))
    capped[:,:] = img[:,:]
    capped[img>threshold] = threshold

    # background estimation
    back = scipy.ndimage.gaussian_filter(capped, sigma=sigma_background, mode='reflect')
    if debug:
        print(np.median(back), np.min(back), np.max(back))

    # normalized image
    norm = img / back
    assert(np.min(norm)>=0)

    # noise reduction of normalized image
    tmp_ = scipy.ndimage.gaussian_filter(norm, sigma=sigma_noise_reduction, mode='reflect') 
    norm[:,:] = tmp_[:,:]

    # segment
    threshold = normalized_intensity_threshold #max(np.percentile(norm, 98), 1.08)
    segmented_ = np.zeros(np.shape(img), dtype=np.uint8)
    segmented_[norm>threshold] = 1
    if debug:
        print("seg. threshold:", threshold)

    # median
    segmented = scipy.ndimage.median_filter(segmented_, size=median_filter_size)

    # connected components
    labels = skimage.morphology.label(segmented, connectivity=2)
    if debug:
        print("Connected cmoponents (original):", np.max(labels))

    # remove small holes
    Amin_hole = small_hole_area_threshold
    noholes = skimage.morphology.remove_small_holes(segmented.astype(bool, copy=True), area_threshold=Amin_hole, connectivity=2)
    labels = skimage.morphology.label(noholes, connectivity=2)
    if debug:
        print("Removed small holes:", np.max(labels))

    # remove small objects
    nosmall = skimage.morphology.remove_small_objects(labels, min_size=min_aggreagte_area, connectivity=2)
    labels = skimage.morphology.label(nosmall, connectivity=2)
    if debug:
        print("Removed small objects:", np.max(labels))
    obj = np.max(labels)

    # save connected components
    labels = np.asarray(labels, dtype=np.uint32)
    assert(np.max(labels) == obj)
    skimage.io.imsave(output_files_aggregates["alllabels"], labels, plugin='tifffile', check_contrast=False)



def AggregateUnet():
    # Instantiates pre-trained UNet for aggregate image segmentation
    weights_file = "processing/weights_best.keras"  #TODO
    if not os.path.exists(weights_file):
        print("Weights file for aggregate Unet does not exist. Exiting..")
        sys.exit()
    model = tf.keras.models.load_model(weights_file)
    return model



def segment_aggregates_UNet(image_file, output_files_aggregates, verbose, debug, model):

    #model.summary()

    # parameters
    img_height = 128    # corresponds to nn_input_dim
    img_width  = 128
    ds         = 32
    patch_length = 128  # split image into tiles
    batch_size = 64     # batch size for predictions
    probability_threshold = 0.7 # threshold above which to accept pixels as aggregates

    # load image
    image0 = skimage.io.imread(image_file, plugin='tifffile')

    # Add zero padding such that shape is a power of 2
    Nx = image0.shape[0]
    Ntarget = get_power2(Nx)
    image = np.zeros((Ntarget,Ntarget))
    image[0:Nx,0:Nx] = image0[:,:]
    #plot_image(image, "raw 2048x2048")

    # Split image into tiles
    patches0 = split_image_sliding_window(image, patch_length, ds=ds, dtype='uint16')

    # Preprocess patches
    patches = []
    for img in patches0:
        patches.append(preprocess_raw(img))
    patches = np.asarray(patches, dtype='float32')
    #print(np.shape(patches))

    # Convert to tf tensor
    tensor_raw = tf.constant(patches)
    tensor_raw = tf.expand_dims(tensor_raw, axis=-1)
    #print(tensor_raw.shape)

    # Convert to tf dataset
    dataset_raw  = tf.data.Dataset.from_tensor_slices(tensor_raw)
    Ndata = tf.data.experimental.cardinality(dataset_raw).numpy()
    #print("Number of elements in dataset:", Ndata)

    # Store dataset in batches
    nn_input_dim = patch_length

    AUTOTUNE = tf.data.AUTOTUNE  # for performance reasons
    predict_batch = (
        dataset_raw
        .batch(batch_size)
        .prefetch(AUTOTUNE))
    #print(predict_batch.element_spec)

    # Predict batch images
    patch_predictions = model.predict(predict_batch)  # returns NumPy array(s) of predictions
    #print(np.shape(patch_predictions))   # shape: (Nimages, Nx, Ny, 1)

    # Stitch back patch predictions
    prediction = stitch_patches_sliding_window(patch_predictions, Ntarget, nn_input_dim, ds=ds)
    #plot_image(prediction, "prediction 2048x2048")

    # Revert predictions to original image size
    prediction0 = np.zeros((Nx,Nx))
    prediction0[:,:] = prediction[0:Nx,0:Nx]
    #plot_image(prediction0, "prediction 2040x2040")

    # binarize probability map
    segmented_ = np.zeros(np.shape(image0), dtype=np.uint8)
    segmented_[prediction0 > probability_threshold] = 1

    # median
    #segmented = scipy.ndimage.median_filter(segmented_, size=median_filter_size)
    segmented = segmented_

    # connected components
    labels = skimage.morphology.label(segmented, connectivity=2)
    if debug:
        print("Connected cmoponents (original):", np.max(labels))

    # remove small holes
    Amin_hole = small_hole_area_threshold
    noholes = skimage.morphology.remove_small_holes(segmented.astype(bool, copy=True), area_threshold=Amin_hole, connectivity=2)
    labels = skimage.morphology.label(noholes, connectivity=2)
    if debug:
        print("Removed small holes:", np.max(labels))

    # remove small objects
    nosmall = skimage.morphology.remove_small_objects(labels, min_size=min_aggreagte_area, connectivity=2)
    labels = skimage.morphology.label(nosmall, connectivity=2)
    if debug:
        print("Removed small objects:", np.max(labels))
    obj = np.max(labels)

    # save connected components
    labels = np.asarray(labels, dtype=np.uint32)
    assert(np.max(labels) == obj)
    skimage.io.imsave(output_files_aggregates["alllabels"], labels, plugin='tifffile', check_contrast=False)




"""
Utility functions related to image loading/saving and processing.
"""


def plot_image(x, title=None):
    plt.imshow(x, vmin=0, vmax=np.percentile(x, 98), cmap="gray")
    if title != None:
        plt.title(title)
    plt.colorbar()
    plt.show()


def preprocess_raw(image, normalize_01=True):
    image = image.astype('float32')
    if normalize_01 == True:
        # Rescale image values in the range [0,1]
        image  = image / np.max(image)
    return image


def split_image_sliding_window(image, Nx_patch, ds, dtype, show_plots=False):
    """
        Splits an image into overlapping patches, in a sliding window fashion.

        image       : Original image with shape e.g.: 2048x2048
        Nx_patch    : Input patches to U-Net
        ds          : Displacement of sliding window in x and y directions
        dtype       : Type of input image
    """

    # Get image shape
    assert(len(image.shape)==2)
    Nx = image.shape[0]
    Ny = image.shape[1]
    assert(Nx==Ny)

    # Number of patches per direction
    Np = int( (Nx - Nx_patch) / ds + 1 )
    #print("Number of patches per dimension:", Np)

    # pixel counter, counting the number of times each pixel is used in a patch
    counter = np.zeros(image.shape)

    # Generate patches
    patches = []    # TODO: Convert to numpy array of known dimensions (Np*Np, Nx_patch, Nx_patch)
    for i in range(Np):
        for j in range(Np):
            x0 = i*ds
            x1 = i*ds + Nx_patch
            y0 = j*ds
            y1 = j*ds + Nx_patch

            assert(x0<Nx and y0<Ny)
            if x1>Nx:
                x0 = x0 - (x1-Nx)
                x1 = Nx
            if y1>Ny:
                y0 = y0 - (y1-Ny)
                y1 = Ny

            # add the counter patch on the total counter:
            counter_patch = np.ones((x1-x0, y1-y0))
            counter[x0:x1, y0:y1] += counter_patch[:,:]

            # Patch data
            patch  = np.asarray(image[x0:x1, y0:y1], dtype=dtype) # 'uint16' for raw, 'uint8' for mask
            patches.append(patch)

    if show_plots==True:
        plot_image(counter)

    return patches



def stitch_patches_sliding_window(patch_predictions, Nx, Nx_patch, ds, show_plots=False):
    """
        Returns a stitched image from overlapping sliding windows

        Arguments:
        - patch_predictions: NumPy array(s) of predictions.
                             shape: (Np, patch_dim, patch_dim).
                             Where Np the number of patches, and
                             patch_dim the number of pixels per patch dimension.
        - Nx: Number of pixels per dimension of the stitched image.
        - Nx_patch: Number of pixels per dimension of each patch.
        - ds: Displacement between patches
    """
    prediction = np.zeros((Nx,Nx), dtype='float32')

    # Number of patches per direction
    Np = int( (Nx - Nx_patch) / ds + 1 )
    #print("Number of patches per dimension:", Np)

    # pixel counter, counting the number of times each pixel is used in a patch
    counter = np.zeros((Nx,Nx))

    # Stitch patches
    for i in range(Np):
        for j in range(Np):
            x0 = i*ds
            x1 = i*ds + Nx_patch
            y0 = j*ds
            y1 = j*ds + Nx_patch

            assert(x0<Nx and y0<Nx)
            assert(x1<=Nx and y1<=Nx)
            k = i*Np + j

            # Adjust coordinates depending on whether the patch is on the edge of the image or not:
            z0 = 0
            h0 = 0
            z1 = Nx_patch
            h1 = Nx_patch
            if i>0:
                x0 = x0+ds # ignore left perimeter of patch
                z0 = ds
            if i<Np-1:
                x1 = x1-ds # ignore right perimeter of patch
                z1 = Nx_patch - ds
            if j>0:
                y0 = y0+ds # ignore bottom perimeter of patch
                h0 = ds
            if j<Np-1:
                y1 = y1-ds # ignore top perimeter of patch
                h1 = Nx_patch - ds

            # add the counter patch on the total counter:
            counter_patch = np.ones((x1-x0, y1-y0))
            counter[x0:x1, y0:y1] += counter_patch[:,:]
            prob = patch_predictions[k]
            prediction[x0:x1, y0:y1] += prob[z0:z1,h0:h1,0]

    # Divide sum of predictions by pixel counter
    prediction /= counter
    if show_plots==True:
        plot_image(counter)

    return prediction


def get_power2(x):
# https://stackoverflow.com/questions/14267555/find-the-smallest-power-of-2-greater-than-or-equal-to-n-in-python
    if x == 0:
        return 1
    else:
        return 2**(x - 1).bit_length()


