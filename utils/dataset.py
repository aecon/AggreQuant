import os
import sys
import glob
from datetime import datetime

from utils import yaml_reader
from utils import printer as p


"""
The Dataset class stores information for the entire dataset.

* member varibles:
    self.paths_nuclei       : sorted paths to all nuclei tif files
    self.paths_cells        : sorted paths to all cell tif files
    self.paths_aggregates   : sorted paths to all aggregate tif files
    self.Nfiles             : number of tif files per structure
    self.dump_QoI_tifs      : true/false: whether to generate QOI tif files
    self.output_folder_main
    self.output_folder_nuclei
    self.output_folder_cells
    self.output_folder_aggregates
    self.output_folder_QoI
    self.output_folder_QoI_tifs
    self.output_folder_diagnostics
    self.type_of_run        : production (default) or validation

* member functions:
    self.make_output_directories : creates output directories
"""

class Dataset:
    def __init__(self, ymlfile, verbose=False):

        me = "Dataset __init__"

        if verbose:
            p.msg("Instantiating Dataset", me)

        if not os.path.isfile(ymlfile):
            p.err("File %s does not exist." % ymlfile, me)
            sys.exit() 

        yml = yaml_reader.load(ymlfile)

        # only 1 dictionary in the yml file is currently supported
        if len(yml.keys()) > 1:
            p.err("Setup yml file should contain only 1 dictionary.", me)
            sys.exit() 

        # parse dictionary
        dataset_name = list(yml.keys())[0]
        dictionary = yml[dataset_name] 
        if verbose:
            p.msg("Dictionary contents: %s" % dictionary, me)

        # set type of run ("validation" or "production")
        self.type_of_run = dictionary["TYPE_OF_RUN"]
        if (self.type_of_run != "validation") and (self.type_of_run != "production"):
            p.err("`TYPE_OF_RUN` must be either `validation` or `production`", me)
            sys.exit()

        # set input folder
        self.input_folder = dictionary["DIRECTORY"]

        # set paths to inputs: assumes all tifs located in the same DIRECTORY
        _paths_nuclei = sorted(glob.glob("%s/*%s*.tif" %
            (dictionary["DIRECTORY"], dictionary["COLOUR_NUCLEI"])))
        _paths_cells  = sorted(glob.glob("%s/*%s*.tif" %
            (dictionary["DIRECTORY"], dictionary["COLOUR_CELLS"])))
        _paths_aggregates = sorted(glob.glob("%s/*%s*.tif" %
            (dictionary["DIRECTORY"], dictionary["COLOUR_AGGREGATES"])))
        if verbose:
            p.msg("Nuclei files: %s" % _paths_nuclei, me)
            p.msg("Cell files: %s" % _paths_cells, me)
            p.msg("Aggregate files: %s" % _paths_aggregates, me)

        # set Dataset's input paths
        self.paths_nuclei     = _paths_nuclei
        self.paths_cells      = _paths_cells
        self.paths_aggregates = _paths_aggregates
        self.Nfiles           = len(_paths_nuclei)
        if verbose:
            p.msg("Number of files: %d" % self.Nfiles, me)

        # set Dataset's input directory
        input_directory = dictionary["DIRECTORY"]

        # set basename of output directory
        if dictionary["OUTPUT_DIRECTORY"] == "date":
            outdir_basename = "output_%s" % (
                datetime.today().strftime('date%Y%m%d_time%H%M%S'))
        elif dictionary["OUTPUT_DIRECTORY"] == "debug": 
            outdir_basename = "output_debug"
        else:
            outdir_basename = dictionary["OUTPUT_DIRECTORY"]
        if verbose:
            p.msg("Output directory basename: %s" % outdir_basename, me)

        # set output paths
        self.output_folder_main = "%s/%s" % (
            input_directory, outdir_basename)
        self.output_folder_nuclei = "%s/nuclei" % self.output_folder_main
        self.output_folder_cells = "%s/cells" % self.output_folder_main
        self.output_folder_aggregates = "%s/aggregates" % (
            self.output_folder_main)
        self.output_folder_QoI = "%s/quantification" % self.output_folder_main
        self.output_folder_QoI_tifs = "%s/quantification/tifs" % (
            self.output_folder_main)
        self.output_folder_diagnostics = "%s/diagnostics" % (
            self.output_folder_main)

        # Check that number of nuclei, cell and aggregate tifs is the same
        assert(len(self.paths_nuclei) == len(self.paths_cells))
        assert(len(self.paths_nuclei) == len(self.paths_aggregates))

        # create output directories
        self.dump_QoI_tifs = dictionary["DUMP_QOI_TIFS"]
        self.make_output_directories()


    def get_output_file_names(self, input_file, data_type):
        me = "get_output_file_names"

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
            img_LabelsInsideCells = "%s/tifs/%s_%s.tif" % (self.output_folder_QoI, bpath, "labels_aggregates_InsideCells")
            img_OverSegCellsAggr = "%s/tifs/%s_%s.tif" % (self.output_folder_QoI, bpath, "overlay_segmented_cells_aggregates")
            img_NumberAggregatesPerCell = "%s/tifs/%s_%s.tif" % (self.output_folder_QoI, bpath, "overlay_naggregates_per_cell")
            outpaths = {
                        "QoI": file_QoI,
                        "LinsideC": img_LabelsInsideCells,
                        "OvSegCA": img_OverSegCellsAggr,
                        "NAggrCell": img_NumberAggregatesPerCell
                        }
            return outpaths

        else:
            p.err("Data type %s not supported!" % data_type, me)
            sys.exit()


    def make_output_directories(self):
        if not os.path.exists(self.output_folder_nuclei):
            os.makedirs(self.output_folder_nuclei)

        if not os.path.exists(self.output_folder_cells):
            os.makedirs(self.output_folder_cells)

        if not os.path.exists(self.output_folder_aggregates):
            os.makedirs(self.output_folder_aggregates)

        if not os.path.exists(self.output_folder_QoI):
            os.makedirs(self.output_folder_QoI)

        if self.dump_QoI_tifs:
            if not os.path.exists(self.output_folder_QoI_tifs):
                os.makedirs(self.output_folder_QoI_tifs)
