import os
import sys
from datetime import datetime

class Data:
    # Info for currently processed data
    def __init__(self, file_nuclei, file_cells, file_aggregates):
        self.n = file_nuclei
        self.c = file_cells
        self.a = file_aggregates


class Dataset:
    # Info for entire dataset (many files)
    def __init__(self, paths_nuclei, paths_cells, paths_aggregates, input_directory):
        self.paths_nuclei     = paths_nuclei
        self.paths_cells      = paths_cells
        self.paths_aggregates = paths_aggregates
        self.Nfiles = len(paths_nuclei)

        folderID = datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
        self.output_folder_main = "%s/output_%s" % (input_directory, folderID)
        self.output_folder_nuclei = ""
        self.output_folder_cells = ""
        self.output_folder_aggregates = ""

        assert(len(self.paths_nuclei) == len(self.paths_cells))
        assert(len(self.paths_nuclei) == len(self.paths_aggregates))

