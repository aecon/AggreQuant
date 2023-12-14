import os
import sys

from processing.dataset import Dataset

#import argparse
# parser.add_argument('-overwrite_output_folder', action='store_true')
# parser.add_argument('-dump_QoI_tifs', action='store_true')


"""
HIGH THROUGHPUT SCREEN IMAGE PROCESSING AND QUANTIFICATION

Application:
    This main script coordinates all operations:
    - stores information about the dataset (input/output paths).
    - stores information about currently processed data.
    - launches parallel processing of image-pairs.

Variables:
    - verbose : whether informative status messages are displayed
      in the standard output.
    - output_directory : choice for the name of the output directory.
      The output directory is generated as a sub-directory inside the
      input directory specified in the yml setup file.
      Possible options:
      * "date" : generates a new directory with current date/time.
      * "debug" : generates/overwrites "output_debug" directory.
      * anything else inside quotes: a user defined name
"""


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SETTINGS
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
verbose = True


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# APPLICATION
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
dataset = Dataset("setup.yml", verbose)
#processor = ImageProcessor("setup.yml")


# # Set the folder/file paths
# processor.set_paths()
# 
# # Image Processing + QoI computation
# processor.process()
# 
# # Generate statistics
# processor.generate_statistics()
# 
# # Generate diagnostic images (montage)
# processor.make_montage()

