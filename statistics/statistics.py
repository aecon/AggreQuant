import os
import sys
import math
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stat
import pandas as pd

from utils import printer as p
from utils.dataset import Dataset
from statistics.plate import Plate



class Statistics:

    def __init__(self, dataset, verbose=False, debug=False):

        me = "Statistics __init__"

        self.verbose = verbose
        self.debug = debug

        self.dataset = dataset
        self.plate = Plate(dataset.plate_name, dataset.number_plate_columns, dataset.number_plate_rows, dataset.number_fields_per_well, dataset.control_types, dataset.control_wells)
        p.msg("Plate name: %s " % dataset.plate_name, me)

        self.whole_plate = dataset.whole_plate


    def _load_QoI_Controls(self):

        # Loop over control wells
        for i in range(self.plate.Nctypes):
            for w in self.plate.control_wells[i]:

                ControlColumn = "%02d" % int(w.split("-")[0])
                row_letter = w.split("-")[1]
                row = self.plate.get_row_number(row_letter)

                list_of_files = self.dataset.paths_aggregates

                # patter matching to find correct aggregate filename..
                # - match row
                pattern = "%s - " % row_letter
                sublistR = [x for x in list_of_files if pattern in x]
                # - match column
                pattern = "- %s" % ControlColumn
                files_all_fields_per_well = [x for x in sublistR if pattern in x]
                assert(len(files_all_fields_per_well)<=self.plate.Nfields)
                if self.verbose:
                    print("Row/Column %s,%s: found %d files:" % (row_letter, ControlColumn, len(files_all_fields_per_well)))
                    print(files_all_fields_per_well, "\n")

                # initialize Well
                column = int(ControlColumn) - 1 # numbering starts with 0!
                global_index = self.plate.get_global_well_number(row, column)
                self.plate.wells[global_index] = [None] * self.plate.Nfields

                # fill in QoI for all fields in Well
                # loop over all QoI files, for all fields in the well
                for field, file_a in enumerate(files_all_fields_per_well):
                    # load QoI results
                    results_dict = self.dataset.get_output_file_names(file_a, "QoI")
                    data = np.loadtxt(results_dict["QoI"], skiprows=1)

                    # store all QoIs to respective field of the well
                    self.plate.wells[global_index][field] = data


    def _load_QoI_plate(self):
        for column in range(self.plate.Ncolumns):
            for row in range(self.plate.Nrows):

                row_letter = self.plate.get_row_letter(row)
                col_letter = self.plate.get_column_number(column)

                list_of_files = self.dataset.paths_aggregates

                # pattern matching to find correct aggregate filename..
                # - match row
                pattern = "%s - " % row_letter
                sublistR = [x for x in list_of_files if pattern in x]
                # - match column
                pattern = "- %s" % col_letter
                files_all_fields_per_well = [x for x in sublistR if pattern in x]
                assert(len(files_all_fields_per_well)<=self.plate.Nfields)
                #if self.verbose:
                #    print("Row/Column %s,%s: %d files:" % (row, column, len(files_all_fields_per_well)))
                #    print(files_all_fields_per_well, "\n")

                # initialize Well
                global_index = self.plate.get_global_well_number(row, column)
                self.plate.wells[global_index] = [None] * self.plate.Nfields
                #if self.verbose:
                #    print("Initialized well:", global_index)

                # fill in QoI for all fields in Well
                if len(files_all_fields_per_well)>=1:

                    if self.verbose:
                        print("Well %d %d has %d files!" % (row, column, len(files_all_fields_per_well)))

                    for field, file_a in enumerate(files_all_fields_per_well):
                        # load QoI results
                        results_dict = self.dataset.get_output_file_names(file_a, "QoI")
                        data = np.loadtxt(results_dict["QoI"], skiprows=1)

                        # store QoI to respective well
                        self.plate.wells[global_index][field] = data
                else:
                    for field in range(self.plate.Nfields):
                        self.plate.wells[global_index][field] = np.zeros((2))


    def _agg_pos_cells_in_well(self, field_PAggPosCells, field_Ncells):
        """
            1. Sum over all detected cells in each field inside a well.
            2. Sum over all aggregate-positive cells in fields of the well.
            3. Return percentage of aggregate positive cells in well.
        """
        well_Ncells = np.sum(field_Ncells)
        field_NAggPosCells = np.multiply(field_PAggPosCells/100., field_Ncells)
        TotalAggPosCells = np.sum(field_NAggPosCells)
        return TotalAggPosCells / well_Ncells * 100.
 

    def _percent_aggregate_area_over_cells_in_well(self, field_PAggregateArea, field_AreaCells):
        """
            1. Sum area of aggregates across all field in the well.
            2. Sum area of cells in well.
            3. Return percentage of cell area occupied by aggregates.
        """
        TotalAggregateArea = np.sum( np.multiply(field_PAggregateArea/100., field_AreaCells) )
        TotalCellArea = np.sum(field_AreaCells)
        return TotalAggregateArea / TotalCellArea * 100.
 

    def _percent_aggregate_positive_cells_Controls(self):

        control_fields = [None] * self.plate.Nctypes

        # Loop over control types and gather QoI from all fields per type
        for i in range(self.plate.Nctypes):
            control_fields[i] = np.zeros( len(self.plate.control_wells[i]) )

            for j, w in enumerate(self.plate.control_wells[i]):

                # get column and row indices
                column = int(w.split("-")[0]) - 1           # index - starting from 0
                row_letter = w.split("-")[1]
                row = self.plate.get_row_number(row_letter) # index - starting from 0
                assert(column>=0 and row>=0)
                assert(column<self.plate.Ncolumns and row<self.plate.Nrows)

                global_index = self.plate.get_global_well_number(row, column)
                assert(global_index>=0 and global_index<self.plate.Nwells)

                data = np.asarray(self.plate.wells[global_index])
                PercAggPosCells = data[:,0] # per field quantities
                Ncells          = data[:,1] # per field quantities
                control_fields[i][j] = self._agg_pos_cells_in_well(PercAggPosCells, Ncells)


        # Figure: percent of average positive cells

        plt.rcParams["figure.figsize"] = (7/2.54, 8/2.54)   # in inches. Divide by 2.54 for cm

        scatter_width = 0.4
        Nplot_columns = self.plate.Nctypes
        for i in range(Nplot_columns):
            xloc = i+1
            # all points
            plt.scatter(xloc-0.5*scatter_width + scatter_width*np.random.rand(len(control_fields[i])), control_fields[i], facecolors='none', edgecolors='gray')
            # standard deviation
            plt.errorbar(xloc, np.nanmean(control_fields[i]), yerr=np.nanstd(control_fields[i]), ecolor='k', elinewidth=1.7, capthick=1.7, capsize=4)
            # means
            plt.scatter(xloc, np.nanmean(control_fields[i]), marker='s', s=10, facecolors='k', edgecolors='k' )

        # axis
        axis = plt.gca()
        axis.set_xticks( np.linspace(1, Nplot_columns, Nplot_columns ) )
        axis.set_xticklabels( self.plate.control_types , fontsize=8)
        axis.set_ylabel("% positive cells", fontsize=14)
        Ymax = int(np.max(control_fields)+5)
        Ymax = round(Ymax, -1)
        plt.ylim([0,Ymax])
        plt.xlim([0,max(2, Nplot_columns)])
        axis.set_yticks( np.linspace(0, Ymax, int(Ymax/10)+1 ) )

        # SSMD annotations
        if self.plate.Nctypes == 2:
            m = np.zeros(Nplot_columns)
            s = np.zeros(Nplot_columns)
            for i in range(Nplot_columns):
                m[i] = np.nanmean(control_fields[i])
                s[i] = np.nanstd( control_fields[i])
            SSMD = (m[0]-m[1])/(math.sqrt(s[0]*s[0] + s[1]*s[1]))
            axis.text(1, -18/80*Ymax, ("SSMD=%.2f" % SSMD), color='black')
        else:
            print("No SSMD annotations because the number of control types is != 2."
)
        # axis spines and layout
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        plt.tight_layout()

        # save
        plt.savefig("%s/control_replicates.pdf" % (self.dataset.output_folder_statistics))
        plt.close()

        """
        Export a text file with a specific QoI for all Control wells in plate
        - structure:
            QoI: percentage of aggregate positive cells
            Well    NT    Well  Rab13
            A-01    x     A-01  y
            B-01    x     B-01  y
            ... for as many fields
        """

        table_file = "%s/control_PercentAggregatePosCells.txt" % (self.dataset.output_folder_statistics)
        with open(table_file, 'w') as f:
            for i in range(self.plate.Nctypes):
                f.write("%15s " % "Well")
                f.write("%15s " % self.plate.control_types[i])
            f.write("\n")
            for i in range(len(self.plate.control_wells[0])):   # assumes the same number of control wells per control type
                for j in range(self.plate.Nctypes):
                    f.write("%15s " % self.plate.control_wells[j][i] )
                    f.write("%15g " % control_fields[j][i] )
                f.write("\n")



    def _export_plate_quantities_per_well(self):

        table_file = "%s/quantities_per_well.txt" % (self.dataset.output_folder_statistics)
        with open(table_file, 'w') as f:
            f.write("%15s %5s %5s %15s %15s %15s\n" % ("Plate name", "Row", "Column", "Ncells", "%AggPosCells", "%AreaAgg2Cells"))

            for row in range(self.plate.Nrows):
                for column in range(self.plate.Ncolumns):

                    global_index = self.plate.get_global_well_number(row, column)

                    # f.write("%15s %15s %15s %15s %15s %15s %16s\n" % ("%Agg.Pos.Cells", "N.Cells", "%Area.Agg.", "AreaCells", "%Ambig.Agg.", "N.Agg.Img(CC)", "Avg.NAgg.perCell"))
                    data = np.asarray(self.plate.wells[global_index])
                    PercAggPosCells = data[:,0] # per field quantities
                    Ncells          = data[:,1] # per field quantities
                    PercAreaAggre   = data[:,2] # per field quantities
                    CellArea        = data[:,3] # per field quantities

                    # Total percentage of aggregate-positive cells in each well
                    total_aggPosCells = self._agg_pos_cells_in_well(PercAggPosCells, Ncells)
                    self.plate.wells_total_agg_pos_cells[global_index] = total_aggPosCells

                    # Total number of cells per well
                    total_NCells = np.sum(Ncells)
                    self.plate.wells_Ncells[global_index] = np.sum(Ncells)

                    # Percent of Cell area occupied by aggregates
                    total_percentAreaAggregates = self._percent_aggregate_area_over_cells_in_well(PercAreaAggre, CellArea)
                    self.plate.wells_percent_area_aggregates_over_cells[global_index] = total_percentAreaAggregates

                    # export to text file
                    row_letter = self.plate.get_row_letter(row)
                    f.write("%15s %5s %5g %15g %15.2f %15.2f\n" % ( self.plate.name, row_letter, (column+1), total_NCells, total_aggPosCells, total_percentAreaAggregates ) )


    def _density_map(self, qoi, name):
        table = np.zeros((self.plate.Nrows, self.plate.Ncolumns))
        for column in range(self.plate.Ncolumns):
            for row in range(self.plate.Nrows):
                global_index = self.plate.get_global_well_number(row, column)
                table[row, column] = qoi[global_index]

        # store table as image
        im = plt.imshow(table)
        axis = plt.gca()
        #axis.get_xaxis().set_visible(False)
        #axis.get_yaxis().set_visible(False)
        axis.set_xticks(np.linspace(0, self.plate.Ncolumns-1, self.plate.Ncolumns))
        axis.set_yticks(np.linspace(0, self.plate.Nrows-1, self.plate.Nrows))
        axis.set_xticklabels(np.linspace(1, self.plate.Ncolumns, self.plate.Ncolumns, dtype=int))
        axis.set_yticklabels(self.plate.alphabet)
        axis.xaxis.tick_top()
        plt.xticks(fontsize=3)
        plt.yticks(fontsize=3)
        cbar = plt.colorbar(im, fraction=0.046, pad=0.04)
        cbar.ax.tick_params(labelsize=5)
        plt.tight_layout()
        output_file = "%s/plate_density_map_%s.pdf" % (self.dataset.output_folder_statistics, name)
        plt.savefig(output_file, transparent=True)
        plt.close()




    def generate_statistics(self):

        # PROCESS THE WHOLE PLATE
        print("Processing Control Columns ...")
        # Load QoI files for the plate
        self._load_QoI_Controls()

        # QoI 1: Percentage of Aggregate-Positive Cells
        self._percent_aggregate_positive_cells_Controls()

        if self.whole_plate:
            print("Processing whole plate ...")

            # Whole-plate Map for percentage of aggregate-positive cells
            self._load_QoI_plate()

            # Compute quantities per well
            self._export_plate_quantities_per_well()

            # Generate density maps
            self._density_map(self.plate.wells_total_agg_pos_cells, "PecrentPositiveCells")
            self._density_map(self.plate.wells_Ncells, "NumberOfCells")

