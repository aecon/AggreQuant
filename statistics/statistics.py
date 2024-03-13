import os
import sys
import math
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stat
import pandas as pd

from utils.dataset import Dataset
from statistics.plate import Plate



class Statistics:

    def __init__(self, dataset, plate_name, verbose=False, debug=False):
        self.verbose = verbose
        self.debug = debug

        self.dataset = dataset
        self.plate = Plate(plate_name)

        self.whole_plate = dataset.whole_plate


    def _load_QoI_Controls(self):
        for ControlColumn in self.plate.ControlColumns:
            for row in range(self.plate.Nrows):

                row_letter = self.plate.get_row_letter(row)

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
                    print("Row/Column %s,%s: %d files:" % (row_letter, ControlColumn, len(files_all_fields_per_well)))
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


    def _load_QoI_plate(self):
        for column in range(self.plate.Ncolumns):
            for row in range(self.plate.Nrows):

                row_letter = self.plate.get_row_letter(row)
                col_letter = self.plate.get_column_number(column)

                list_of_files = self.dataset.paths_aggregates

                # patter matching to find correct aggregate filename..
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

                    #if self.verbose:
                    #    print("Well %d %d has %d files!" % (row, column, len(files_all_fields_per_well)))

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
        #plt.scatter(1*np.ones(self.plate.NumberOfControlRows), group_5Up, label="NT_1")
        #plt.scatter(2*np.ones(self.plate.NumberOfControlRows), group_5Dn, label="Rab13_1")
        #plt.scatter(3*np.ones(self.plate.NumberOfControlRows), group_13Dn, label="NT_2")
        #plt.scatter(4*np.ones(self.plate.NumberOfControlRows), group_13Up, label="Rab13_2")
        #plt.ylim([0,80])
        #plt.legend()
        #plt.savefig("%s/Statistics_Plate_%s.png" % (self.dataset.output_folder_statistics, self.plate.name))
        #plt.close()

        plt.rcParams["figure.figsize"] = (7/2.54, 8/2.54)   # in inches. Divide by 2.54 for cm

        scatter_width = 0.4
        plt.scatter(1-0.5*scatter_width + scatter_width*np.random.rand(len(group_5Up )), group_5Up , facecolors='none', edgecolors='gray')
        plt.scatter(2-0.5*scatter_width + scatter_width*np.random.rand(len(group_5Dn )), group_5Dn , facecolors='none', edgecolors='gray')
        plt.scatter(3-0.5*scatter_width + scatter_width*np.random.rand(len(group_13Dn)), group_13Dn, facecolors='none', edgecolors='gray')
        plt.scatter(4-0.5*scatter_width + scatter_width*np.random.rand(len(group_13Up)), group_13Up, facecolors='none', edgecolors='gray')
        # errorbars
        plt.errorbar(1, np.nanmean(group_5Up ), yerr=np.nanstd(group_5Up ), ecolor='k', elinewidth=2, capthick=2, capsize=4)
        plt.errorbar(2, np.nanmean(group_5Dn ), yerr=np.nanstd(group_5Dn ), ecolor='k', elinewidth=2, capthick=2, capsize=4)
        plt.errorbar(3, np.nanmean(group_13Dn), yerr=np.nanstd(group_13Dn), ecolor='k', elinewidth=2, capthick=2, capsize=4)
        plt.errorbar(4, np.nanmean(group_13Up), yerr=np.nanstd(group_13Up), ecolor='k', elinewidth=2, capthick=2, capsize=4)
        # means
        plt.scatter(np.linspace(1,4,4), [np.nanmean(group_5Up), np.nanmean(group_5Dn), np.nanmean(group_13Dn), np.nanmean(group_13Up)], marker='s', facecolors='k', edgecolors='k' )
        # axis
        axis = plt.gca()
        axis.set_xticks( np.linspace(1, 4, 4 ) )
        axis.set_xticklabels( ["NT_1", "Rab13_1", "NT_2", "Rab13_2"] , fontsize=8)
        axis.set_ylabel("% positive cells", fontsize=14)
        Ymax = int(np.max([group_5Up, group_5Dn, group_13Dn, group_13Up])+0.5)
        Ymax = round(Ymax, -1)
        plt.ylim([0,Ymax])
        axis.set_yticks( np.linspace(0, Ymax, int(Ymax/10)+1 ) )
        # SSMD annotations
        mc1 = np.nanmean(group_5Up )
        mr1 = np.nanmean(group_5Dn )
        mc2 = np.nanmean(group_13Dn)
        mr2 = np.nanmean(group_13Up)
        sc1 = np.nanstd(group_5Up )
        sr1 = np.nanstd(group_5Dn )
        sc2 = np.nanstd(group_13Dn)
        sr2 = np.nanstd(group_13Up)
        SSMD1 = (mc1-mr1)/(math.sqrt(sc1*sc1 + sr1*sr1))
        SSMD2 = (mc2-mr2)/(math.sqrt(sc2*sc2 + sr2*sr2))
        axis.text(0.5, -18/80*Ymax, ("SSMD=%.2f" % SSMD1), color='black')
        axis.text(2.5, -18/80*Ymax, ("SSMD=%.2f" % SSMD2), color='black')
        # axis spines and layout
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        plt.tight_layout()
        # save
        plt.savefig("%s/control_replicates.pdf" % (self.dataset.output_folder_statistics))
        plt.close()


        ## Figure 2: CENTERED percent of average positive cells
        #plt.scatter(1*np.ones(self.plate.NumberOfControlRows), group_5Up -np.mean(group_5Up), label="NT_1")
        #plt.scatter(2*np.ones(self.plate.NumberOfControlRows), group_5Dn -np.mean(group_5Up), label="Rab13_1")
        #plt.scatter(3*np.ones(self.plate.NumberOfControlRows), group_13Dn-np.mean(group_13Dn), label="NT_2")
        #plt.scatter(4*np.ones(self.plate.NumberOfControlRows), group_13Up-np.mean(group_13Dn), label="Rab13_2")
        #plt.ylim([-60,60])
        #plt.legend()
        #plt.savefig("%s/Statistics_Plate_Centered_NT%s.png" % (self.dataset.output_folder_statistics, self.plate.name))
        #plt.close()


        """
        Export a text file with a specific QoI for all 4 Control wells in plate
        - structure:
            QoI: percentage of aggregate positive cells
            NT_1    Rab13_1     NT_2    Rab13_2
            x
            x
            ... for as many fields

        """
        table_file = "%s/control_PercentAggregatePosCells.txt" % (self.dataset.output_folder_statistics)
        with open(table_file, 'w') as f:
            f.write("%15s %15s %15s %15s\n" % ("NT_1", "Rab13_1", "NT_2", "Rab13_2"))
            for i in range(self.plate.NumberOfControlRows):
                f.write("%15g %15g %15g %15g\n" % (group_5Up[i], group_5Dn[i], group_13Dn[i], group_13Up[i]) )



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
        axis.set_xticks(np.linspace(0,23,24))
        axis.set_yticks(np.linspace(0,15,16))
        axis.set_xticklabels(np.linspace(1,24,24, dtype=int))
        axis.set_yticklabels(['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P'])
        axis.xaxis.tick_top()
        plt.xticks(fontsize=3)
        plt.yticks(fontsize=3)
        cbar = plt.colorbar(im, fraction=0.046, pad=0.04)
        cbar.ax.tick_params(labelsize=5)
        plt.tight_layout()
        output_file = "%s/plate_density_map_%s.pdf" % (self.dataset.output_folder_statistics, name)
        plt.savefig(output_file, transparent=True)
        plt.close()


    def _make_volcano_plot(self, qoi):
        controls_wells = []
        for ControlColumn in self.plate.ControlColumns:
            for row in range(self.plate.Nrows):
                if (ControlColumn=="05" and row<8) or (ControlColumn=="13" and row>7):
                    column = int(ControlColumn) - 1 # numbering starts with 0!
                    global_index = self.plate.get_global_well_number(row, column)
                    controls_wells.append(qoi[global_index])

        # the following analysis is based on:
        # https://thecodingbiologist.com/posts/Making-volcano-plots-in-python-in-Google-Colab

        # Compute mean of control column
        avg_controls = np.mean(controls_wells)

        # Conmpute log2-fold-changes wrt control
        log2FC = list(np.log2(np.divide(qoi, avg_controls)))

        # Compute p-values
        pvalues = []
        for column in range(self.plate.Ncolumns):
            for row in range(self.plate.Nrows):
                global_index = self.plate.get_global_well_number(row, column)
                ttest_result = stat.ttest_ind(qoi[global_index], controls_wells)
                pvalue = ttest_result[1]
                pvalues.append(pvalue)

        # Bonferroni correction
        Ntests = self.plate.Nwells
        transformed_pvalues = list(-1*np.log10(Ntests*np.array(pvalues)))

        ## Generate pandas dataframe
        #df_data = np.zeros((len(qoi),3))
        #df_data[:,0] = qoi[:]
        #df_data[:,1] = log2FC[:]
        #df_data[:,2] = transformed_pvalues[:]
        #headers = ["QoI", "log2FC", "p-values"]
        #df = pd.DataFrame(data=df_data, columns=headers)

        # Make volcano plot
        plt.scatter(log2FC, transformed_pvalues)
        plt.savefig("%s/volcano_pyplottest.pdf" % self.dataset.output_folder_statistics)
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


            # Other plots
            #self._make_volcano_plot(self.plate.wells_total_agg_pos_cells)  # not used because the computation of this requires two plates


