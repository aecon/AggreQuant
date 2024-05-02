import os
import sys
import glob
from datetime import datetime

from utils import yaml_reader
from utils import printer as p

debug = False

"""
The Dataset class stores information for the entire dataset.

* member varibles:
    #
    # Path options
    self.plate_name         : user-defined name for the plate
    self.paths_nuclei       : sorted paths to all nuclei tif files
    self.paths_cells        : sorted paths to all cell tif files
    self.paths_aggregates   : sorted paths to all aggregate tif files
    self.paths_controls_nuclei    : sorted paths to all control wells 
    self.paths_controls_cells     : sorted paths to all control wells 
    self.paths_controls_aggregates: sorted paths to all control wells 
    self.output_folder_main
    self.output_folder_nuclei
    self.output_folder_cells
    self.output_folder_aggregates
    self.output_folder_QoI
    self.output_folder_QoI_tifs
    self.output_folder_diagnostics
    self.output_folder_statistics
    #
    # Data processing options
    self.Nfiles             : number of tif files per object (cells, nuclei, aggregates)
    self.dump_QoI_tifs      : true/false: whether to generate QOI tif files
    self.type_of_run        : "production" (default) or "validation"
    self.whole_plate        : in a production run, true/false: whether inputs are files from the whole plate or only the control columns
    self.process_only_controls : whether to process only the cdata corresponding to the control columns, not all files in folder
    self.cell_segmentation_algorithm  : "cellpose" (default) or "distanceIntensity"
    #
    # Image segmentation options
    self.nuclei_min_area    : minimum area for a segmented object to be a nucleus
    self.nuclei_max_area    : maximum area for a segmented object to be a nucleus
    #
    # Plate layout
    self.number_plate_columns : number of columns in the plate
    self.number_plate_rows  : number of rows in the plate
    self.number_fields_per_well : number of fields per well
    #
    # Control wells options
    self.number_control_types: number of the different contols used in the plate. E.g. for (NT, Rab13): 2
    self.control_types      : a list names of the control types, E.g. ["NT", "Rab13"]
    self.control_wells      : list (list of wells corresponding to each control type)

* member functions:
    self.make_output_directories : creates output directories
    self.get_output_file_names   : returns dictionary of output file names
"""

class Dataset:
    def __init__(self, ymlfile):

        me = "Dataset __init__"

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
        p.msg("Setup dictionary contents: %s" % dictionary, me)

        # set type of run ("validation" or "production")
        self.type_of_run = dictionary["TYPE_OF_RUN"]
        if (self.type_of_run != "validation") and (self.type_of_run != "production"):
            p.err("`TYPE_OF_RUN` must be either `validation` or `production`", me)
            sys.exit()

        # type of production run (whole plate or control columns)
        if self.type_of_run == "production":
            self.whole_plate = dictionary["WHOLE_PLATE"]
        else:
            self.whole_plate = False

        # which data to process (all data in the folder or only control column data)
        self.process_only_controls = dictionary["PROCESS_ONLY_CONTROLS"]

        # Plate name
        self.plate_name = dictionary["PLATE_NAME"]

        # set segmentation method for cells
        self.cell_segmentation_algorithm = "cellpose"
        if dictionary["CELL_SEGMENTATION_ALGORITHM"] == "distanceIntensity":
            self.cell_segmentation_algorithm = "distanceIntensity"
        p.msg("Segmenting cells using algorithm: %s" % self.cell_segmentation_algorithm, me)

        # set input folder
        self.input_folder = dictionary["DIRECTORY"]
        if not os.path.exists(self.input_folder):
            p.err("Input directory does not exist.", me)
            sys.exit()
        else:
            p.msg("Using input directory: %s" % self.input_folder, me)

        # image segmentation
        self.nuclei_min_area = dictionary["NUCLEI_MIN_AREA"]
        self.nuclei_max_area = dictionary["NUCLEI_MAX_AREA"]

        # set plate layout
        self.number_plate_columns   = dictionary["NUMBER_PLATE_COLUMNS"]
        self.number_plate_rows      = dictionary["NUMBER_PLATE_ROWS"]
        self.number_fields_per_well = dictionary["NUMBER_FIELDS_PER_WELL"]
        p.msg("Plate layout: %d columns, %d rows, %d fields per well" % (self.number_plate_columns, self.number_plate_rows, self.number_fields_per_well), me)

        # set control well options
        self.number_control_types = int(dictionary["NUMBER_OF_CONTROL_TYPES"])
        self.control_types = dictionary["CONTROL_TYPES"]
        assert(len(self.control_types) == self.number_control_types)
        p.msg("Number of control types: %d" % self.number_control_types, me)
        p.msg("Control types: " + ', '.join(self.control_types), me)

        p.msg("Control wells:", me)
        self.control_wells = []
        # populate self.control_wells
        for i in range(self.number_control_types):
            CONTROL_WELLS_TYPE_X = "CONTROL_WELLS_TYPE_%d" % (i+1)
            self.control_wells.append(dictionary[CONTROL_WELLS_TYPE_X])
            p.msg("  > " + self.control_types[i] + ": " + ', '.join(self.control_wells[i]), me)

        # set paths to inputs: assumes all tifs located in the same DIRECTORY

        # Paths to all images from control wells
        _paths_nuclei = []
        _paths_cells = []
        _paths_aggregates = []

        for i in range(self.number_control_types):
            for w in self.control_wells[i]:

                id_col = "%02d" % int(w.split("-")[0])
                id_row = w.split("-")[1]

                _files_nuclei     = glob.glob("%s/*%s - %s(*%s*.tif" % (dictionary["DIRECTORY"], id_row, id_col, dictionary["COLOUR_NUCLEI"]))
                _files_cells      = glob.glob("%s/*%s - %s(*%s*.tif" % (dictionary["DIRECTORY"], id_row, id_col, dictionary["COLOUR_CELLS"]))
                _files_aggregates = glob.glob("%s/*%s - %s(*%s*.tif" % (dictionary["DIRECTORY"], id_row, id_col, dictionary["COLOUR_AGGREGATES"]))

                assert(len(_files_nuclei) == len(_files_cells))
                assert(len(_files_nuclei) == len(_files_aggregates))

                if len(_files_nuclei) >= 1:
                    _paths_nuclei.append(_files_nuclei)
                if len(_files_cells) >= 1:
                    _paths_cells.append(_files_cells)
                if len(_files_aggregates) >= 1:
                    _paths_aggregates.append(_files_aggregates)

                p.msg("  > Found [%d] files for well: %s-%s" % (len(_files_nuclei), id_row, id_col), me)

        # Flatten lists
        _paths_nuclei = [x  for items in _paths_nuclei for x in items]
        _paths_cells = [x  for items in _paths_cells for x in items]
        _paths_aggregates = [x  for items in _paths_aggregates for x in items]

        # Check that paths list is indeed flattened
        if (any(isinstance(i, list) for i in _paths_nuclei)==True or 
            any(isinstance(i, list) for i in _paths_cells)==True or
            any(isinstance(i, list) for i in _paths_aggregates)==True):
            p.err("Paths list is not a flat list.", me)
            sys.exit()

        _paths_nuclei       = sorted(_paths_nuclei)
        _paths_cells        = sorted(_paths_cells)
        _paths_aggregates   = sorted(_paths_aggregates)

        self.paths_controls_nuclei     = _paths_nuclei
        self.paths_controls_cells      = _paths_cells
        self.paths_controls_aggregates = _paths_aggregates


        if self.process_only_controls == True:
            p.msg("Processing only control columns", me)
            self.paths_nuclei     = _paths_nuclei
            self.paths_cells      = _paths_cells
            self.paths_aggregates = _paths_aggregates

        else:
            p.msg("Processing all files inside input folder!", me)
            _paths_nuclei = sorted(glob.glob("%s/*%s*.tif" %
                (dictionary["DIRECTORY"], dictionary["COLOUR_NUCLEI"])))
            _paths_cells  = sorted(glob.glob("%s/*%s*.tif" %
                (dictionary["DIRECTORY"], dictionary["COLOUR_CELLS"])))
            _paths_aggregates = sorted(glob.glob("%s/*%s*.tif" %
                (dictionary["DIRECTORY"], dictionary["COLOUR_AGGREGATES"])))

            self.paths_nuclei     = _paths_nuclei
            self.paths_cells      = _paths_cells
            self.paths_aggregates = _paths_aggregates

        if debug == True:
            p.msg("Nuclei files: %s" % self.paths_nuclei, me)
            p.msg("Cell files: %s" % self.paths_cells, me)
            p.msg("Aggregate files: %s" % self.paths_aggregates, me)

        # set Dataset's input paths
        self.Nfiles           = len(self.paths_nuclei)
        assert(len(self.paths_nuclei) == len(self.paths_cells))
        assert(len(self.paths_nuclei) == len(self.paths_aggregates))
        p.msg("Number of image-triplet sets: %d" % self.Nfiles, me)

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
        self.output_folder_statistics = "%s/statistics" % (
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

        if not os.path.exists(self.output_folder_statistics):
            os.makedirs(self.output_folder_statistics)

        if self.dump_QoI_tifs:
            if not os.path.exists(self.output_folder_QoI_tifs):
                os.makedirs(self.output_folder_QoI_tifs)

