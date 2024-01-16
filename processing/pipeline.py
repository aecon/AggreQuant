import os
import sys
import glob
import click
import multiprocessing

from utils import printer as p
from utils.dataset import Dataset
from statistics.diagnostics import *
from processing.nuclei import segment_method_stardist
from processing.cells import segment_cells
from processing.aggregates import segment_aggregates
from processing.quantification import compute_QoI


verbose = False
debug = False


def _image_triplet(file_n, file_c, file_a, dataset, parallel, _model):

    me = "_image_triplet"

    if parallel:
        # start new tensorflow session for each process
        import tensorflow as tf

        # limit GPU usage
        gpus = tf.config.experimental.list_physical_devices('GPU')
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)

        # load StarDist model
        from stardist.models import StarDist2D
        model = StarDist2D.from_pretrained('2D_versatile_fluo')
    else:
        model = _model

    # Get paths to generated (output) files
    output_files_nuclei     = dataset.get_output_file_names(file_n, "nuclei")
    output_files_cells      = dataset.get_output_file_names(file_c, "cells")
    output_files_aggregates = dataset.get_output_file_names(file_a, "aggregates")
    output_files_QoI        = dataset.get_output_file_names(file_a, "QoI")
    if not parallel:
        p.msg(output_files_nuclei, me)
        p.msg(output_files_cells, me)
        p.msg(output_files_aggregates, me)
        p.msg(output_files_QoI, me)
    print(file_n, file_a, file_c, flush=True)

    # nuclei segmentation
    segment_method_stardist(
        model, file_n, output_files_nuclei, verbose, debug)

    # cell segmentation
    segment_cells(dataset.cell_segmentation_algorithm, file_c, output_files_cells, output_files_nuclei, verbose, debug)

    # aggregate segmentation
    segment_aggregates(file_a, output_files_aggregates, verbose, debug)

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

    # Load StarDist model only once
    from stardist.models import StarDist2D
    model = StarDist2D.from_pretrained('2D_versatile_fluo')

    # display progress bar
    bar = click.progressbar(length=dataset.Nfiles, show_eta=False)

    for file_n, file_c, file_a in zip(
        dataset.paths_nuclei, dataset.paths_cells, dataset.paths_aggregates):
        _image_triplet(file_n, file_c, file_a, dataset, False, model)

        print("Total Progress:")
        bar.update(1); print("\n")


# TODO
#def process_multi(dataset, _verbose, _debug):
#    me = "process_multi"
#    verbose = _verbose
#    debug = _debug
#
#    # TODO: add RAM memory in computation of NUM_CPU_CORES
#    MAX_CPU_CORES = multiprocessing.cpu_count()
#    NUM_CPU_CORES = min(dataset.Nfiles, MAX_CPU_CORES)
#    p.msg("Using %d CPU cores" % NUM_CPU_CORES, me)
#
#    # Create pool of worker processes
#    with multiprocessing.Pool(processes=NUM_CPU_CORES) as pool:
#
#        # Process image triplets in parallel
#        pool.starmap(
#            _image_triplet,
#            [(file_n, file_c, file_a, dataset, True, None) for file_n, file_c, file_a in zip(
#                dataset.paths_nuclei,dataset.paths_cells,dataset.paths_aggregates)]
#            )
#
#        # Close pool of worker processes
#        pool.close()
#        pool.join()
