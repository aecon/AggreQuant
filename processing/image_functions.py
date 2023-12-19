import os
import skimage.io


"""
A collection of generic image processing functions.
"""


def load_image(image_file, verbose):
    """
    Input:
        Path to a tif image
    Output:
        narray of the same size and shape as the number of pixels in x and y 
    """
    if verbose:
        print(">> Processing image: %s" % os.path.basename(image_file))
    img = skimage.io.imread(image_file, plugin='tifffile')
    return img


