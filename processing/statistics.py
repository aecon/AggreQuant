import os
import sys
import glob

from utils import printer as p
from utils.dataset import Dataset
from statistics.statistics import *


def statistics(dataset, verbose, debug):
    platename = "%s_%s" % (
        os.path.basename(os.path.dirname(dataset.input_folder)),
        os.path.basename(dataset.input_folder) )
    if verbose:
        print("Plate name:", platename)
    statistics = Statistics(dataset, platename, verbose, debug)
    statistics.generate_statistics()

