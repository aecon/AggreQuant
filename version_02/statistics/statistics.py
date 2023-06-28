import os
import sys
import numpy as np

from processing.dataset import Dataset
from statistics.plate import Plate


class Statistics:

    def __init__(self, dataset, plate_name, verbose=False, debug=False):
        self.dataset = dataset
        self.plate = Plate(plate_name)

        #self.table = []


    #def _load_all_QoI_files(self):
    #    for i, file_a in enumerate(self.dataset.paths_aggregates):
    #        all_QoI_files = self.dataset.get_output_file_names(file_a, "QoI")
    #        data = np.loadtxt(all_QoI_files["QoI"], skiprows=1)
    #        if i==0:
    #            self.table = np.zeros( (len(self.dataset.paths_aggregates), len(data)) )
    #        self.table[i,:] = data[:]


    def _percent_aggregate_positive_cells(self):
        print("TODO")


    def _load_QoI_whole_plate(self):
        print("TODO.")


    def _load_QoI_Controls(self):
        for ControlColumn in self.plate.ControlColumns:
            # find files that contain ControlColumn inside

            row = 
            column = 
            file_a = # construct from Well Column and Row

            # load QoI results
            results_dict = self.dataset.get_output_file_names(file_a, "QoI")
            data = np.loadtxt(results_dict["QoI"], skiprows=1)

            # store QoI to respective well
            global_index = self.plate.get_global_well_number(row, column)
            self.plate.well[global_index] = data


    def generate_statistics(self):

        # Load QoI files for the plate
        self._load_QoI_Controls()

        # QoI 1: Percentage of Aggregate Positive Cells
        self._percent_aggregate_positive_cells()


