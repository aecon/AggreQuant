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
dataset = Dataset("applications/setup.yml")
process(dataset, verbose, debug)
statistics(dataset, verbose, debug)
montage(dataset, verbose, debug)
