import os
import sys
import glob

from utils import printer as p
from utils.dataset import Dataset
from statistics.diagnostics import *


def montage(dataset, verbose, debug):
    """
    Makes a montage (i.e. a grid of images) with the aim of
    checking the segmentation and quantification quality.

    Functions are separated in `validaton` and `production` groups.
    - production: a random sample of images is selected for the montage.
    - validation: all images of the validation dataset are displayed.
    """

    print("\n\nSTEP MONTAGE:\n")

    if not os.path.exists(dataset.output_folder_diagnostics):
        os.makedirs(dataset.output_folder_diagnostics)

    # Case: Validation run
    if dataset.type_of_run == "validation":

            print("Generating montage for nuclei segmentation\n")
            montage_filename = "%s/montage_overlay_nuclei.tif" % (
                dataset.output_folder_diagnostics)
            paths_seg_nuclei = sorted(glob.glob("%s/*Blue*seeds*.tif" % (
                dataset.output_folder_nuclei)))
            montage_overlay_two_images_validation(
                dataset.paths_nuclei, paths_seg_nuclei, montage_filename)

            print("Generating montage for cell segmentation\n")
            montage_filename = "%s/montage_overlay_cells.tif" % (
                dataset.output_folder_diagnostics)
            paths_seg_cells = sorted(glob.glob("%s/*Red*labels*.tif" % (
                dataset.output_folder_cells)))
            montage_overlay_two_images_validation(
                dataset.paths_cells, paths_seg_cells, montage_filename)

            print("Generating montage for aggregate segmentation\n")
            montage_filename = "%s/montage_overlay_aggregates.tif" % (
                dataset.output_folder_diagnostics)
            paths_seg_agg = sorted(glob.glob("%s/*Green*labels*.tif" % (
                dataset.output_folder_aggregates)))
            montage_overlay_two_images_validation(
                dataset.paths_aggregates, paths_seg_agg, montage_filename)

        #if 0: 
        #    print("Generating 6-Channel montage\n")
        #    montage_filename = "%s/montage_overlay_6Channels.tif" % (
        #        dataset.output_folder_diagnostics)
        #    paths_seg_nuclei = sorted(glob.glob(
        #        "%s/*Blue*seeds*.tif" % (dataset.output_folder_nuclei)))
        #    paths_seg_cells = sorted(glob.glob(
        #        "%s/*Red*labels*.tif" % (dataset.output_folder_cells)))
        #    paths_seg_agg = sorted(glob.glob(
        #        "%s/*Green*labels*.tif" % (
        #            dataset.output_folder_aggregates)))
        #    montage_overlay_6Channels_validation(
        #        dataset.paths_nuclei, paths_seg_nuclei,
        #        dataset.paths_cells, paths_seg_cells,
        #        dataset.paths_aggregates, paths_seg_agg,
        #        montage_filename)

   
    elif dataset.type_of_run == "production":

        if 0:
            montage_filename = "%s/montage_simple_nuclei.tif" % (
                dataset.output_folder_diagnostics)
            montage_simple(
                dataset.paths_nuclei, montage_filename, 
                debug=debug)

        # overlay nuclei
        montage_filename = "%s/montage_overlay_nuclei.tif" % (
            dataset.output_folder_diagnostics)
        paths_seg_nuclei = sorted(glob.glob("%s/*Blue*seeds*.tif" % (
            dataset.output_folder_nuclei)))
        montage_overlay_two_images(
            dataset.paths_nuclei, paths_seg_nuclei, montage_filename, 
            debug=debug, verbose=verbose)

        # overlay cells
        montage_filename = "%s/montage_overlay_cells.tif" % (
            dataset.output_folder_diagnostics)
        paths_seg_cells = sorted(glob.glob("%s/*Red*labels*.tif" % (
            dataset.output_folder_cells)))
        montage_overlay_two_images(
            dataset.paths_cells, paths_seg_cells, montage_filename, 
            debug=debug, verbose=verbose)

        # overlay aggregates
        montage_filename = "%s/montage_overlay_aggregates.tif" % (
            dataset.output_folder_diagnostics)
        paths_seg_agg = sorted(glob.glob("%s/*Green*labels*.tif" % (
            dataset.output_folder_aggregates)))
        montage_overlay_two_images(
            dataset.paths_aggregates, paths_seg_agg, montage_filename,
            debug=False, verbose=False)

