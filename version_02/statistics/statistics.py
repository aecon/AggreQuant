import os
import sys
import numpy as np


class Statistics:

    def __init__(self, dataset, verbose=False, debug=False):
        self.dataset = dataset
        self.table = []


    def _load_all_QoI_files(self):
        for i, file_a in enumerate(self.dataset.paths_aggregates):
            all_QoI_files = self.dataset.get_output_file_names(file_a, "QoI")
            data = np.loadtxt(all_QoI_files["QoI"], skiprows=1)
            if i==0:
                self.table = np.zeros( (len(self.dataset.paths_aggregates), len(data)) )
            self.table[i,:] = data[:]


    def _percent_aggregate_positive_cells(self):
        


    def generate_statistics(self):

        # Load QoI files
        self._load_QoI_files()

        # QoI 1: Percentage of Aggregate Positive Cells
        self._percent_aggregate_positive_cells()

