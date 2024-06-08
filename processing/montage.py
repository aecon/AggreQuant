import os
import sys
import glob

from utils import printer as p
from utils.dataset import Dataset
from statistics.diagnostics import *


def _get_control_filepaths(dataset, stucture):

    if stucture == "nuclei":
        colour = dataset.colour_nuclei
        paths_controls = dataset.paths_controls_nuclei
        output_id = "seeds"
    elif stucture == "cells":
        colour = dataset.colour_cells
        paths_controls = dataset.paths_controls_cells
        output_id = "labels"
    elif stucture == "aggregates":
        colour = dataset.colour_aggregates
        paths_controls = dataset.paths_controls_aggregates
        output_id = "alllabels"
    else:
        print("No structure with name: %s. Exiting ..." % stucture)
        sys.exit()

    # Select only the middle field in the well
    Nfields = dataset.number_fields_per_well
    fieldID = int(Nfields//2) + 1

    paths_raw = []
    paths_seg = []

    # Arrage paths with respect to control types
    for i in range(dataset.number_control_types):
        for w in dataset.control_wells[i]:

            id_col = "%02d" % int(w.split("-")[0])
            id_row = w.split("-")[1]

            file_raw = glob.glob("%s/*%s - %s(fld*%d* wv *%s*.tif" % (dataset.input_folder, id_row, id_col, fieldID, colour))[0]  # keep only first occurance in case there are several
            paths_raw.append(file_raw)
            output_files = dataset.get_output_file_names(file_raw, stucture)
            paths_seg.append(output_files[output_id])

    return paths_raw, paths_seg


#def _get_control_filepaths(all_raw, all_seg):
#
#    paths_Col05 = sorted([s for s in all_seg if "- 05(fld 5" in s])
#    paths_Col13 = sorted([s for s in all_seg if "- 13(fld 5" in s])
#    paths_NT1 = paths_Col05[0:8]
#    paths_NT2 = paths_Col13[8::]
#    paths_RB1 = paths_Col05[8::]
#    paths_RB2 = paths_Col13[0:8]
#    paths_seg_nuclei = paths_NT1 + paths_NT2 + paths_RB1 + paths_RB2
#
#    paths_Col05 = sorted([s for s in all_raw if "- 05(fld 5" in s])
#    paths_Col13 = sorted([s for s in all_raw if "- 13(fld 5" in s])
#    paths_NT1 = paths_Col05[0:8]
#    paths_NT2 = paths_Col13[8::]
#    paths_RB1 = paths_Col05[8::]
#    paths_RB2 = paths_Col13[0:8]
#    paths_raw_nuclei = paths_NT1 + paths_NT2 + paths_RB1 + paths_RB2
#
#    return paths_raw_nuclei, paths_seg_nuclei


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
        paths_raw, paths_seg = _get_control_filepaths(dataset, "nuclei")
        montage_overlay_control_columns(paths_raw, paths_seg, montage_filename, verbose=False)
        print("Files and file-order used in montage for nuclei:", paths_raw)

        print("Generating CONTROLS montage for cells segmentation\n")
        montage_filename = "%s/montage_controls_cells.tif" % (dataset.output_folder_diagnostics)
        paths_raw, paths_seg = _get_control_filepaths(dataset, "cells")
        montage_overlay_control_columns(paths_raw, paths_seg, montage_filename, verbose=False)

        print("Generating CONTROLS montage for aggregate segmentation\n")
        montage_filename = "%s/montage_controls_aggregates.tif" % (dataset.output_folder_diagnostics)
        paths_raw, paths_seg = _get_control_filepaths(dataset, "aggregates")
        montage_overlay_control_columns(paths_raw, paths_seg, montage_filename, verbose=False)

