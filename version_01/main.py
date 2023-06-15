import os
import sys
import glob
import argparse

from filenames import Filenames
from diagnostics import Diagnostics
from cells import cellbody_segmentation
from aggregates import aggregate_segmentation

parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, required=True, help="text file with path to tifs, and colour identifiers")
parser.add_argument('-debug', action='store_true')
args = parser.parse_args()


if os.path.exists(args.i):
    print("\nReading paths and colours from file: %s \n" % args.i)
else:
    print("File %s does NOT exist! Give a valid path to a file." % args.i)
    sys.exit()

with open(args.i) as file:
    for line in file:

        if line.find("PATH_TO_IMAGES")==0:
            path_to_dir = (line.split(sep="=")[1].rstrip()).replace("\"", "")

            if os.path.exists(path_to_dir) == True:
                print("Found directory: %s" % path_to_dir)
            else:
                print("Directory %s does NOT exist! Make sure that there are no spaces before/after the = symbol in %s" % (path_to_dir, args.i))
                sys.exit()

        if line.find("COLOUR_NUCLEI")==0:
            CNUCLEI = (line.split(sep="=")[1].rstrip()).replace("\"", "")
            print("COLOUR_NUCLEI = %s" % CNUCLEI)

        if line.find("COLOUR_AGGREGATES")==0:
            CAGGREGATES = (line.split(sep="=")[1].rstrip()).replace("\"", "")
            print("COLOUR_AGGREGATES = %s" % CAGGREGATES)

        if line.find("COLOUR_CELLS")==0:
            CCELLS = (line.split(sep="=")[1].rstrip()).replace("\"", "")
            print("COLOUR_CELLS = %s" % CCELLS)


# Filename conventions
# TODO: Set defaults in some other txt file (?)
Names = Filenames()
# color identifiers in tif filenames
Names.COLOR_NUCLEI = CNUCLEI
Names.COLOR_CELLS = CCELLS
Names.COLOR_AGGREGATES = CAGGREGATES
# folders
Names.OUTDIR_PATH = path_to_dir
Names.OUTDIR = "output_V0.3"
# nuclei segmentation
Names.NUCLEI_ALL_LABELS = "labels_StarDist" # same as in nuclei.py
Names.NUCLEI_SEEDS = "seeds_nuclei" # same as in nuclei.py
# cellbody segmentation
Names.CELLBODY_SEGMENTATION_TYPE = "distance" #"propagation"  #"distance"
Names.CELLBODY_ODIR_NAME = "cellbodies_%s" % Names.CELLBODY_SEGMENTATION_TYPE
# aggregate segmentation
Names.AGGREGATE_SEGMENTATION_TYPE = "intensity"
Names.AGGREGATE_ODIR_NAME = "aggregates_%s" % Names.AGGREGATE_SEGMENTATION_TYPE
# diagnostics
Names.COMPOSITE_RAW_NUCLEI_EDGES = "composite_edges" # same as in nuclei.py
Names.COMPOSITE_CELLS_AND_NUCLEI = "composite_nuclei"


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Segmentation
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if 0:
    print("\nRunning nuclei segmentation.")
    images_nuclei = sorted(glob.glob("%s/*%s*.tif" % (path_to_dir, CNUCLEI)))
    if args.debug == True:
        print("Running in debug mode. Processing only 5 first images")
        images_nuclei = images_nuclei[0:5]
    print("Found %d nuclei images." % len(images_nuclei))
    nuclei_paths = ""
    for f in images_nuclei:
        nuclei_paths+=" '%s'" % f
    os.system( "conda run -n tf python nuclei.py -o %s -i %s" % (Names.OUTDIR, nuclei_paths) )


if 0:
    print("\n Running cellbody segmentation.")
    images_cells = sorted(glob.glob("%s/*%s*.tif" % (path_to_dir, CCELLS)))
    print("Found %d cellbody images." % len(images_cells))
    if args.debug == True:
        print("Running in debug mode. Processing only 5 first images")
        cellbody_segmentation(images_cells[0:5], Names)
    else:
        cellbody_segmentation(images_cells, Names)

if 1:
    print("\n Running aggregate segmentation.")
    images_agg = sorted(glob.glob("%s/*%s*.tif" % (path_to_dir, CAGGREGATES)))
    print("Found %d aggregate images." % len(images_agg))
    if args.debug == True:
        print("Running in debug mode. Processing only 5 first images")
        aggregate_segmentation(images_agg[0:5], Names)
    else:
        aggregate_segmentation(images_agg, Names)



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Diagnostics
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Generate dignostics for segmentation performance
Diagnosis = Diagnostics(Names, args.debug)

if 0:
    print("\nGenerating nuclei Diagnostics.")
    Diagnosis.Montage_nuclei_RandomSelectionZoom()

if 0:
    print("\nGenerating cellbody Diagnostics.")
    Diagnosis.Montage_cells_RandomSelectionZoom()


