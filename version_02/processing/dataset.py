import os
import sys


class Data:
    # Info for currently processed dataset
    def __init__(self, file_nuclei, file_cells, file_aggregates, output_folder):
        self.n = file_nuclei
        self.c = file_cells
        self.a = file_aggregates
        self.o = output_folder


class Dataset:
    # Info for entire dataset (many files)
    def __init__(self, paths_nuclei, paths_cells, paths_aggregates):
        self.paths_nuceli     = paths_nuclei
        self.paths_cells      = paths_cells
        self.paths_aggregates = paths_aggregates
# ??        self.paths_outdirs    = paths_output_folders
        self.Nfiles = len(paths_nuclei)

        assert(len(paths_nuclei) == len(paths_cells))
        assert(len(paths_nuclei) == len(paths_aggregates))

