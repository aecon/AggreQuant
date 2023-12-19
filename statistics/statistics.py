import os
import sys
import numpy as np
import matplotlib.pyplot as plt

from utils.dataset import Dataset
from statistics.plate import Plate


class Statistics:

    def __init__(self, dataset, plate_name, verbose=False, debug=False):
        self.verbose = verbose
        self.debug = debug

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
                if self.verbose:
                    print("Row/Column %s,%s: %d files:" % (row, ControlColumn, len(files_all_fields_per_well)))
                    print(files_all_fields_per_well, "\n")

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


    def _agg_pos_cells_in_well(self, field_PAggPosCells, field_Ncells):
        """
            Sum over all detected cells in each field inside a well.
            Sum over all aggregate-positive cells in fields of the well.
            Return percentage of aggregate positive cells in well.
        """
        well_Ncells = np.sum(field_Ncells)
        field_NAggPosCells = np.multiply(field_PAggPosCells/100., field_Ncells)
        TotalAggPosCells = np.sum(field_NAggPosCells)
        return TotalAggPosCells / well_Ncells * 100.
 

    def _percent_aggregate_positive_cells_Controls(self):

        group_5Up  = np.zeros(self.plate.NumberOfControlRows)
        group_5Dn  = np.zeros(self.plate.NumberOfControlRows)
        group_13Up = np.zeros(self.plate.NumberOfControlRows)
        group_13Dn = np.zeros(self.plate.NumberOfControlRows)

        for i in range(self.plate.NumberOfControlRows):
            # Control Column 05:
            global_index = self.plate.get_global_well_number(i, 4)
            data = np.asarray(self.plate.wells[global_index])
            PercAggPosCells = data[:,0] # per field quantities
            Ncells          = data[:,1] # per field quantities
            group_5Up[i] = self._agg_pos_cells_in_well(PercAggPosCells, Ncells)

            global_index = self.plate.get_global_well_number(i+self.plate.NumberOfControlRows, 4)
            data = np.asarray(self.plate.wells[global_index])
            PercAggPosCells = data[:,0] # per field quantities
            Ncells          = data[:,1] # per field quantities
            group_5Dn[i] = self._agg_pos_cells_in_well(PercAggPosCells, Ncells)

            # Control Column 13:
            global_index = self.plate.get_global_well_number(i, 12)
            data = np.asarray(self.plate.wells[global_index])
            PercAggPosCells = data[:,0] # per field quantities
            Ncells          = data[:,1] # per field quantities
            group_13Up[i] = self._agg_pos_cells_in_well(PercAggPosCells, Ncells)

            global_index = self.plate.get_global_well_number(i+self.plate.NumberOfControlRows, 12)
            data = np.asarray(self.plate.wells[global_index])
            PercAggPosCells = data[:,0] # per field quantities
            Ncells          = data[:,1] # per field quantities
            group_13Dn[i] = self._agg_pos_cells_in_well(PercAggPosCells, Ncells)


        # Figure 1: percent of average positive cells
        plt.scatter(1*np.ones(self.plate.NumberOfControlRows), group_5Up, label="NT_1")
        plt.scatter(2*np.ones(self.plate.NumberOfControlRows), group_5Dn, label="Rab13_1")
        plt.scatter(3*np.ones(self.plate.NumberOfControlRows), group_13Dn, label="NT_2")
        plt.scatter(4*np.ones(self.plate.NumberOfControlRows), group_13Up, label="Rab13_2")
        plt.ylim([0,80])
        plt.legend()
        plt.savefig("Statistics_Plate_%s.png" % self.plate.name)
        plt.close()


        # Figure 2: CENTERED percent of average positive cells
        plt.scatter(1*np.ones(self.plate.NumberOfControlRows), group_5Up -np.mean(group_5Up), label="NT_1")
        plt.scatter(2*np.ones(self.plate.NumberOfControlRows), group_5Dn -np.mean(group_5Up), label="Rab13_1")
        plt.scatter(3*np.ones(self.plate.NumberOfControlRows), group_13Dn-np.mean(group_13Dn), label="NT_2")
        plt.scatter(4*np.ones(self.plate.NumberOfControlRows), group_13Up-np.mean(group_13Dn), label="Rab13_2")
        plt.ylim([-60,60])
        plt.legend()
        plt.savefig("Statistics_Plate_Centered_NT%s.png" % self.plate.name)
        plt.close()


        """
        Export a text file with a specific QoI for all 4 Control wells in plate
        - structure:
            QoI: percentage of aggregate positive cells
            NT_1    Rab13_1     NT_2    Rab13_2
            x
            x
            ... for as many fields

        """
        table_file = "Statistics_Plate_%s_PercentAggregatePosCells.txt" % self.plate.name
        with open(table_file, 'w') as f:
            f.write("%15s %15s %15s %15s\n" % ("NT_1", "Rab13_1", "NT_2", "Rab13_2"))
            for i in range(self.plate.NumberOfControlRows):
                f.write("%15g %15g %15g %15g\n" % (group_5Up[i], group_5Dn[i], group_13Dn[i], group_13Up[i]) )



    def generate_statistics(self):

        # Load QoI files for the plate
        self._load_QoI_Controls()

        # QoI 1: Percentage of Aggregate Positive Cells
        self._percent_aggregate_positive_cells_Controls()

