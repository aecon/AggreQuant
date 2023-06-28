import os
import sys
import numpy as np
import re

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
            for row in range(self.plate.Nrows):

                row_letter = self.plate.get_row_letter(row)

                list_of_files = self.dataset.paths_aggregates

                # patter matching to find correct aggregate filename..
                # - match row
                pattern = ".*_%s *" % row_letter
                expression = re.compile(pattern)
                sublistR = list(filter(expression.match, list_of_files))
                # - match column
                pattern = ".*- %s*" % ControlColumn
                expression = re.compile(pattern)
                files_all_fields_per_well = list(filter(expression.match, sublistR))
                assert(len(files_all_fields_per_well)<=self.plate.Nfields)

                # initialize Well
                column = int(ControlColumn)
                global_index = self.plate.get_global_well_number(row, column)
                self.plate.wells[global_index] = [None] * self.plate.Nfields

                # fill in QoI for all fields in well
                for field, file_a in enumerate(files_all_fields_per_well):
                    print(file_a)

                    # load QoI results
                    results_dict = self.dataset.get_output_file_names(file_a, "QoI")
                    data = np.loadtxt(results_dict["QoI"], skiprows=1)

                    # store QoI to respective well
                    self.plate.wells[global_index][field] = data


    def generate_statistics(self):

        # Load QoI files for the plate
        self._load_QoI_Controls()

        assert(0)


        # QoI 1: Percentage of Aggregate Positive Cells
        self._percent_aggregate_positive_cells()


