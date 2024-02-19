import os
import sys

from utils.dataset import Dataset
from processing.pipeline import process
from processing.montage import montage
from processing.statistics import statistics


"""
HIGH CONTENT SCREEN IMAGE PROCESSING AND QUANTIFICATION

Application:
    main.py coordinates all operations:
    - stores information about the dataset (input/output paths).
    - stores information about currently processed data.
    - gathers statistics for aggregate localization in cells.
    - generates montage images for screen/segmentation assessment.

Variables:
    - verbose : display status messages in the standard output.
    - debug : display additional messages for debugging.

    - output_directory : choice for the name of the output directory.
      The output directory is generated as a sub-directory inside the
      input directory specified in the yml setup file.
      Possible options:
      * "date" : generates a new directory with current date/time.
      * "debug" : generates/overwrites "output_debug" directory.
      *  anything else inside quotes: a user defined name
"""


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SETTINGS
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
verbose = True
debug = True


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# APPLICATION
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
dataset = Dataset("apps/setup_20240208_HA40_rep1.yml", verbose)

process(dataset, verbose, debug)

statistics(dataset, verbose, debug)

montage(dataset, verbose, debug)

