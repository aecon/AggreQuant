import os
import sys
from datetime import datetime

class Data:
    # Info for currently processed data
    def __init__(self, file_nuclei, file_cells, file_aggregates):
        # inputs
        self.n = file_nuclei
        self.c = file_cells
        self.a = file_aggregates


class Dataset:
    # Info for entire dataset (many files)
    def __init__(self, paths_nuclei, paths_cells, paths_aggregates, input_directory):
        self.paths_nuclei     = paths_nuclei
        self.paths_cells      = paths_cells
        self.paths_aggregates = paths_aggregates
        self.Nfiles           = len(paths_nuclei)

        self.input_folder     = input_directory

        folderID = datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
        self.output_folder_main = "%s/output_%s" % (input_directory, folderID)
        self.output_folder_nuclei = "%s/nuclei" % self.output_folder_main
        self.output_folder_cells = "%s/cells" % self.output_folder_main
        self.output_folder_aggregates = "%s/aggregates" % self.output_folder_main
        self.output_folder_QoI = "%s/quantification" % self.output_folder_main

        assert(len(self.paths_nuclei) == len(self.paths_cells))
        assert(len(self.paths_nuclei) == len(self.paths_aggregates))


    def get_output_file_names(self, input_file, data_type):
        bpath = os.path.basename(input_file)

        if data_type=="nuclei":
            filename_all_nuclei = "%s/%s_%s.tif" % (self.output_folder_nuclei, bpath, "nuclei_all_labels")
            filename_seeds = "%s/%s_%s.tif" % (self.output_folder_nuclei, bpath, "nuclei_seeds")
            outpaths = {
                        "seeds": filename_seeds,
                        "alllabels": filename_all_nuclei
                        }
            return outpaths

        elif data_type=="cells":
            file_cell_labels = "%s/%s_%s.tif" % (self.output_folder_cells, bpath, "cell_labels")
            outpaths = {
                        "labels": file_cell_labels
                        }
            return outpaths

        elif data_type=="aggregates":
            file_agg_alllabels = "%s/%s_%s.tif" % (self.output_folder_aggregates, bpath, "aggregates_all_labels")
            outpaths = {
                        "alllabels": file_agg_alllabels
                        }
            return outpaths

        elif data_type=="QoI":
            file_QoI = "%s/%s_%s.txt" % (self.output_folder_QoI, bpath, "QoI")
            img_LabelsInsideCells = "%s/%s_%s.tif" % (self.output_folder_QoI, bpath, "labels_aggregates_InsideCells")
            img_OverSegCellsAggr = "%s/%s_%s.tif" % (self.output_folder_QoI, bpath, "overlay_segmented_cells_aggregates")
            img_NumberAggregatesPerCell = "%s/%s_%s.tif" % (self.output_folder_QoI, bpath, "overlay_naggregates_per_cell")
            outpaths = {
                        "QoI": file_QoI,
                        "LinsideC": img_LabelsInsideCells,
                        "OvSegCA": img_OverSegCellsAggr,
                        "NAggrCell": img_NumberAggregatesPerCell
                        }
            return outpaths

        else:
            print("Data type %s not supported!" % data_type)
            sys.exit()


