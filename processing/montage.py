import os
import sys
import glob

from utils import printer as p
from utils.dataset import Dataset
from statistics.diagnostics import *


def _get_control_filepaths(all_raw, all_seg):

    paths_Col05 = sorted([s for s in all_seg if "- 05(fld 5" in s])
    paths_Col13 = sorted([s for s in all_seg if "- 13(fld 5" in s])
    paths_NT1 = paths_Col05[0:8]
    paths_NT2 = paths_Col13[8::]
    paths_RB1 = paths_Col05[8::]
    paths_RB2 = paths_Col13[0:8]
    paths_seg_nuclei = paths_NT1 + paths_NT2 + paths_RB1 + paths_RB2

    paths_Col05 = sorted([s for s in all_raw if "- 05(fld 5" in s])
    paths_Col13 = sorted([s for s in all_raw if "- 13(fld 5" in s])
    paths_NT1 = paths_Col05[0:8]
    paths_NT2 = paths_Col13[8::]
    paths_RB1 = paths_Col05[8::]
    paths_RB2 = paths_Col13[0:8]
    paths_raw_nuclei = paths_NT1 + paths_NT2 + paths_RB1 + paths_RB2

    return paths_raw_nuclei, paths_seg_nuclei


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

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Montage for whole plate
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # overlay nuclei
        print("Generating montage for nuclei segmentation\n")
        montage_filename = "%s/montage_overlay_nuclei.tif" % (
            dataset.output_folder_diagnostics)
        paths_seg_nuclei = sorted(glob.glob("%s/*Blue*seeds*.tif" % (
            dataset.output_folder_nuclei)))
        rand = montage_overlay_two_images(
            dataset.paths_nuclei, paths_seg_nuclei, montage_filename, genRand=True,
            debug=False, verbose=False)

        # overlay cells
        print("Generating montage for cell segmentation\n")
        montage_filename = "%s/montage_overlay_cells.tif" % (
            dataset.output_folder_diagnostics)
        paths_seg_cells = sorted(glob.glob("%s/*Red*labels*.tif" % (
            dataset.output_folder_cells)))
        montage_overlay_two_images(
            dataset.paths_cells, paths_seg_cells, montage_filename, rand, genRand=False,
            debug=False, verbose=False)

        # overlay aggregates
        print("Generating montage for aggregate segmentation\n")
        montage_filename = "%s/montage_overlay_aggregates.tif" % (
            dataset.output_folder_diagnostics)
        paths_seg_agg = sorted(glob.glob("%s/*Green*labels*.tif" % (
            dataset.output_folder_aggregates)))
        montage_overlay_two_images(
            dataset.paths_aggregates, paths_seg_agg, montage_filename, rand, genRand=False,
            debug=False, verbose=False)


        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Montage for Control columns
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        print("Generating CONTROLS montage for nuclei segmentation\n")
        montage_filename = "%s/montage_controls_nuclei.tif" % (dataset.output_folder_diagnostics)
        paths_raw, paths_seg = _get_control_filepaths( 
            dataset.paths_nuclei, glob.glob("%s/*Blue*seeds*.tif" % (dataset.output_folder_nuclei)) )
        montage_overlay_control_columns(paths_raw, paths_seg, montage_filename, verbose=False)

        print("Generating CONTROLS montage for cells segmentation\n")
        montage_filename = "%s/montage_controls_cells.tif" % (dataset.output_folder_diagnostics)
        paths_raw, paths_seg = _get_control_filepaths( 
            dataset.paths_cells, glob.glob("%s/*Red*labels*.tif" % (dataset.output_folder_cells)) )
        montage_overlay_control_columns(paths_raw, paths_seg, montage_filename, verbose=False)

        print("Generating CONTROLS montage for aggregate segmentation\n")
        montage_filename = "%s/montage_controls_aggregates.tif" % (dataset.output_folder_diagnostics)
        paths_raw, paths_seg = _get_control_filepaths( 
            dataset.paths_aggregates, glob.glob("%s/*Green*labels*.tif" % (dataset.output_folder_aggregates)) )
        montage_overlay_control_columns(paths_raw, paths_seg, montage_filename, verbose=False)

