import os
import sys

from utils.dataset import Dataset
from processing.pipeline import process
from processing.montage import montage
from processing.statistics import statistics

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

        dataset = Dataset(ifile)
        process(dataset, verbose, debug)
        statistics(dataset, verbose, debug)
        montage(dataset, verbose, debug)
