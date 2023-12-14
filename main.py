import os
import sys

from utils.dataset import Dataset
from processing.pipeline import process, process_multi
from processing.montage import montage
from processing.statistics import statistics


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
debug = True


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# APPLICATION
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
dataset = Dataset("setup.yml", verbose)

process(dataset, verbose, debug)
#process_multi(dataset, verbose, debug)
sys.exit()
assert(0)

statistics(dataset, verbose, debug)
montage(dataset, verbose, debug)
