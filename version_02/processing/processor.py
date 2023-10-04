import os
import sys
import glob
import click
import argparse
import tensorflow as tf
from stardist.models import StarDist2D

from processing.parser import FileParser
from processing.dataset import Dataset
from processing.data import Data
from processing.nuclei import NucleiSegmentation
from processing.cells import CellSegmentation
from processing.aggregates import AggregateSegmentation
from processing.quantification import compute_QoI
from statistics.statistics import Statistics
from statistics.diagnostics import *


class ImageProcessor:

    def __init__(self, argparser, process_nuclei=True, process_cells=True, process_aggregates=True):
        fileParser = FileParser(argparser)

        self.dataset = []
        self.data = []
        self.statistics = []
        self.debug = fileParser.debug
        self.dump_tifs = fileParser.dump_tifs
        self.verbose = fileParser.verbose
        self.fileParser = fileParser
        self.process_nuclei = process_nuclei
        self.process_cells = process_cells
        self.process_aggregates = process_aggregates


    # Public functions

    def set_paths(self):
        self._set_dataset_paths(self.fileParser)
        self._make_output_directories()


    def process(self):
        # limit GPU usage
        gpus = tf.config.experimental.list_physical_devices('GPU')
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)

        # display progress bar
        bar = click.progressbar(length=self.dataset.Nfiles, show_eta=False)

        # Load pretrained StarDist model only once!
        NucleiModel = StarDist2D.from_pretrained('2D_versatile_fluo')

        print("\n\nBEGIN IMAGE PROCESSING. TOTAL NUMBER OF IMAGE PAIRS:", self.dataset.Nfiles)

        # loop over all "pairs" of files
        for file_n, file_c, file_a in zip(self.dataset.paths_nuclei, self.dataset.paths_cells, self.dataset.paths_aggregates):

            print("\n\nProcessing files:")
            print("  ", file_n)
            print("  ", file_c)
            print("  ", file_a)
            print("Total Progress:")
            bar.update(1); print("\n")

            self._set_data_paths(file_n, file_c, file_a)

            self._process(NucleiModel)


    def generate_statistics(self):
        platename = "%s_%s" % ( os.path.basename(os.path.dirname(self.dataset.input_folder)), os.path.basename(self.dataset.input_folder) )
        self.statistics = Statistics(self.dataset, platename, self.verbose, self.debug)
        self.statistics.generate_statistics()


    def make_montage(self):
        if not os.path.exists(self.dataset.output_folder_diagnostics):
            os.makedirs(self.dataset.output_folder_diagnostics)

        if 0:
            montage_filename = "%s/montage_simple_nuclei.tif" % (self.dataset.output_folder_diagnostics)
            montage_simple(self.dataset.paths_nuclei, montage_filename, debug=False)

        # overlay nuclei
        if 0:
            montage_filename = "%s/montage_overlay_nuclei.tif" % (self.dataset.output_folder_diagnostics)
            paths_seg_nuclei = sorted(glob.glob("%s/*Blue*seeds*.tif" % (self.dataset.output_folder_nuclei)))
            montage_overlay_two_images(self.dataset.paths_nuclei, paths_seg_nuclei, montage_filename, debug=False, verbose=False)

        # overlay cells
        if 0:
            montage_filename = "%s/montage_overlay_cells.tif" % (self.dataset.output_folder_diagnostics)
            paths_seg_cells = sorted(glob.glob("%s/*Red*labels*.tif" % (self.dataset.output_folder_cells)))
            montage_overlay_two_images(self.dataset.paths_cells, paths_seg_cells, montage_filename, debug=False, verbose=False)

        # overlay aggregates
        if 1:
            montage_filename = "%s/montage_overlay_aggregates.tif" % (self.dataset.output_folder_diagnostics)
            paths_seg_agg = sorted(glob.glob("%s/*Green*labels*.tif" % (self.dataset.output_folder_aggregates)))
            montage_overlay_two_images(self.dataset.paths_aggregates, paths_seg_agg, montage_filename, debug=False, verbose=False)



    # Intended private functions

    def _set_data_paths(self, file_n, file_c, file_a):
        if not os.path.isfile(file_n):
            print("File %s does NOT exist!", file_n)
            sys.exit()
        if not os.path.isfile(file_c):
            print("File %s does NOT exist!", file_c)
            sys.exit()
        if not os.path.isfile(file_a):
            print("File %s does NOT exist!", file_a)
            sys.exit()
        self.data = Data(file_n, file_c, file_a)


    def _set_dataset_paths(self, fileParser):
        paths_nuclei = sorted(glob.glob("%s/*%s*.tif" % (fileParser.input_directory, fileParser.COLOUR_NUCLEI)))
        paths_cells  = sorted(glob.glob("%s/*%s*.tif" % (fileParser.input_directory, fileParser.COLOUR_CELLS)))
        paths_agg    = sorted(glob.glob("%s/*%s*.tif" % (fileParser.input_directory, fileParser.COLOUR_AGGREGATES)))
        self.dataset = Dataset(paths_nuclei, paths_cells, paths_agg, fileParser.input_directory)


    def _make_output_directories(self):
        if not os.path.exists(self.dataset.output_folder_nuclei):
            os.makedirs(self.dataset.output_folder_nuclei)

        if not os.path.exists(self.dataset.output_folder_cells):
            os.makedirs(self.dataset.output_folder_cells)

        if not os.path.exists(self.dataset.output_folder_aggregates):
            os.makedirs(self.dataset.output_folder_aggregates)

        if not os.path.exists(self.dataset.output_folder_QoI):
            os.makedirs(self.dataset.output_folder_QoI)


    def _process(self, NucleiModel):
        if self.verbose:
            print("\nProcessing files:")
            print(" > %s" % self.data.n)
            print(" > %s" % self.data.c)
            print(" > %s" % self.data.a)
            print("")

        # Get paths to generated (output) files
        output_files_nuclei     = self.dataset.get_output_file_names(self.data.n, "nuclei")
        output_files_cells      = self.dataset.get_output_file_names(self.data.c, "cells")
        output_files_aggregates = self.dataset.get_output_file_names(self.data.a, "aggregates")
        output_files_QoI        = self.dataset.get_output_file_names(self.data.a, "QoI")
        if self.debug:
            print(output_files_nuclei)
            print(output_files_cells)
            print(output_files_aggregates)
            print(output_files_QoI)

        # Process nuclei
        if self.process_nuclei:
            nuclei = NucleiSegmentation(self.data.n, output_files_nuclei, NucleiModel, self.verbose, self.debug)
            Number_of_nuclei = nuclei.segment_nuclei()

        if self.process_cells:
            # Process cells
            cells = CellSegmentation(self.data.c, output_files_nuclei, output_files_cells, self.verbose, self.debug)
            cells.segment_cells()

        if self.process_aggregates:
            # Process aggregates
            aggregates = AggregateSegmentation(self.data.a, output_files_aggregates, self.verbose, self.debug)
            aggregates.segment_aggregates()

            # Quantities of Interest
            compute_QoI(output_files_aggregates, output_files_cells, output_files_QoI, self.verbose, self.debug)


