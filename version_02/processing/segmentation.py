import os
import sys
import glob

from utils.parser import FileParser
from processing.dataset import Dataset, Data


class ImageProcessor:

    def __init__(self, fileParser):
        self.dataset = []
        self.data = []
        self.debug = fileParser.debug
        self.verbose = fileParser.verbose

        self.find_files(fileParser)


    def find_files(self, fileParser):
        paths_nuclei = sorted(glob.glob("%s/*%s*.tif" % (fileParser.input_directory, fileParser.COLOUR_NUCLEI)))
        paths_cells  = sorted(glob.glob("%s/*%s*.tif" % (fileParser.input_directory, fileParser.COLOUR_CELLS)))
        paths_agg    = sorted(glob.glob("%s/*%s*.tif" % (fileParser.input_directory, fileParser.COLOUR_AGGREGATES)))

        self.dataset = Dataset(paths_nuclei, paths_cells, paths_agg)



