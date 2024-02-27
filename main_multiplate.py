import os
import sys

from utils.dataset import Dataset
from processing.pipeline import process
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

setup_files = [
"apps/Dalila/setup_20240227_HA45_rep1.yml",
"apps/Dalila/setup_20240227_HA45_rep2.yml",
"apps/Dalila/setup_20240227_HA46_rep1.yml",
"apps/Dalila/setup_20240227_HA46_rep2.yml",
"apps/Dalila/setup_20240227_HA47_rep1.yml",
"apps/Dalila/setup_20240227_HA47_rep2.yml"
]

for ifile in setup_files:
    if os.path.isfile(ifile):
        print("Processing setup file:", ifile)

        dataset = Dataset(ifile, verbose)

        process(dataset, verbose, debug)

        statistics(dataset, verbose, debug)

        montage(dataset, verbose, debug)

