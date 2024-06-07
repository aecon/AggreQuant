import os
import sys
import glob
import multiprocessing

from utils import printer as p
from utils.dataset import Dataset
from statistics.diagnostics import *
from processing.nuclei import segment_method_stardist
from processing.cells import segment_cells
from processing.aggregates import segment_aggregates_UNet, segment_aggregates_filters
from processing.quantification import compute_QoI


verbose = False
debug = False


def _image_triplet(file_n, file_c, file_a, dataset, stardist_model, cellpose_model, aggregate_model):

    me = "_image_triplet"

    # Get paths to generated (output) files
    output_files_nuclei     = dataset.get_output_file_names(file_n, "nuclei")
    output_files_cells      = dataset.get_output_file_names(file_c, "cells")
    output_files_aggregates = dataset.get_output_file_names(file_a, "aggregates")
    output_files_QoI        = dataset.get_output_file_names(file_a, "QoI")
    if verbose:
        p.msg(output_files_nuclei, me)
        p.msg(output_files_cells, me)
        p.msg(output_files_aggregates, me)
        p.msg(output_files_QoI, me)
    p.msg(file_n + ", " + file_a + ", " + file_c, me)

    # nuclei segmentation
    segment_method_stardist(
        stardist_model, file_n, output_files_nuclei, verbose, debug, dataset.nuclei_min_area, dataset.nuclei_max_area)

    # cell segmentation
    segment_cells(dataset.cell_segmentation_algorithm, file_c, output_files_cells, output_files_nuclei, verbose, debug, cellpose_model)

    # aggregate segmentation
    #segment_aggregates_filters(file_a, output_files_aggregates, verbose, debug)
    segment_aggregates_UNet(file_a, output_files_aggregates, verbose, debug, aggregate_model)

    # Compute Quantities of Interest
    compute_QoI(output_files_aggregates, output_files_cells, output_files_QoI,
        verbose, debug, dataset.dump_QoI_tifs)


def process(dataset, _verbose, _debug):
    me = "process"
    verbose = _verbose
    debug = _debug

    import tensorflow as tf
    # limit GPU usage
    gpus = tf.config.experimental.list_physical_devices('GPU')
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)

    # load StarDist model
    from stardist.models import StarDist2D
    stardist_model = StarDist2D.from_pretrained('2D_versatile_fluo')

    # load CellPose model
    from cellpose.models import Cellpose
    cellpose_model = Cellpose(gpu=True, model_type='cyto2')

    # load aggregate model
    from processing.aggregates import AggregateUnet
    aggregate_model = AggregateUnet()  # TODO: edit arguments

    # loop over image triplets
    for file_n, file_c, file_a in zip(
        dataset.paths_nuclei, dataset.paths_cells, dataset.paths_aggregates):
        _image_triplet(file_n, file_c, file_a, dataset, stardist_model, cellpose_model, aggregate_model)

