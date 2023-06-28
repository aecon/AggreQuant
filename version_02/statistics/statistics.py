import os
import sys
import numpy as np
import matplotlib.pyplot as plt

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


    def _load_QoI_whole_plate(self):
        print("TODO.")


    def _load_QoI_Controls(self):
        for ControlColumn in self.plate.ControlColumns:
            for row in range(self.plate.Nrows):

                row_letter = self.plate.get_row_letter(row)

                list_of_files = self.dataset.paths_aggregates

                # patter matching to find correct aggregate filename..
                # - match row
                pattern = "_%s " % row_letter
                sublistR = [x for x in list_of_files if pattern in x]
                # - match column
                pattern = "- %s" % ControlColumn
                files_all_fields_per_well = [x for x in sublistR if pattern in x]
                assert(len(files_all_fields_per_well)<=self.plate.Nfields)

                # initialize Well
                column = int(ControlColumn) - 1 # numbering starts with 0!
                global_index = self.plate.get_global_well_number(row, column)
                self.plate.wells[global_index] = [None] * self.plate.Nfields

                # fill in QoI for all fields in Well
                for field, file_a in enumerate(files_all_fields_per_well):
                    # load QoI results
                    results_dict = self.dataset.get_output_file_names(file_a, "QoI")
                    data = np.loadtxt(results_dict["QoI"], skiprows=1)

                    # store QoI to respective well
                    self.plate.wells[global_index][field] = data


    def _percent_aggregate_positive_cells_Controls(self):

        group_5Up  = np.zeros(8)
        group_5Dn  = np.zeros(8)
        group_13Up = np.zeros(8)
        group_13Dn = np.zeros(8)

        for i in range(8):
            global_index = self.plate.get_global_well_number(i, 4)
            data = np.asarray(self.plate.wells[global_index])
            QoI = data[:,0]
            group_5Up[i] = np.mean(QoI)

            global_index = self.plate.get_global_well_number(i+8, 4)
            data = np.asarray(self.plate.wells[global_index])
            QoI = data[:,0]
            group_5Dn[i] = np.mean(QoI)

            global_index = self.plate.get_global_well_number(i, 12)
            data = np.asarray(self.plate.wells[global_index])
            QoI = data[:,0]
            group_13Up[i] = np.mean(QoI)

            global_index = self.plate.get_global_well_number(i+8, 12)
            data = np.asarray(self.plate.wells[global_index])
            QoI = data[:,0]
            group_13Dn[i] = np.mean(QoI)


        plt.scatter(1*np.ones(8), group_5Up, label="NT_1")
        plt.scatter(2*np.ones(8), group_5Dn, label="Rab13_1")
        plt.scatter(3*np.ones(8), group_13Dn, label="NT_2")
        plt.scatter(4*np.ones(8), group_13Up, label="Rab13_2")
        plt.ylim([0,80])
        plt.legend()
#        plt.show()
        plt.close()


    def generate_statistics(self):

        # Load QoI files for the plate
        self._load_QoI_Controls()

        # QoI 1: Percentage of Aggregate Positive Cells
        self._percent_aggregate_positive_cells_Controls()

