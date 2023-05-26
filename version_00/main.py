import os
import sys
import glob
import argparse

from filenames import Filenames
from diagnostics import Diagnostics

parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, required=True, help="text file with path to tifs, and colour identifiers")
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
Names.OUTDIR_PATH = path_to_dir
Names.OUTDIR = "output_V0.1"
Names.NUCLEI_ALL_LABELS = "labels_StarDist" # same as in nuclei.py
Names.NUCLEI_SEEDS = "seeds_nuclei" # same as in nuclei.py
Names.COMPOSITE_RAW_NUCLEI_EDGES = "composite_edges" # same as in nuclei.py

if 1:
    print("\nRunning nuclei segmentation.")
    images_nuclei = glob.glob("%s/*%s*.tif" % (path_to_dir, CNUCLEI))
    print("Found %d nuclei images." % len(images_nuclei))
    nuclei_paths = ""
    for f in images_nuclei:
        nuclei_paths+=" '%s'" % f
    os.system( "conda run -n tf python nuclei.py -o %s -i %s" % (Names.OUTDIR, nuclei_paths) )


if 0:
    print("\n Running cellbody segmentation.")
    images_cells = glob.glob("%s/*%s*.tif" % (path_to_dir, CCELLS))
    print("Found %d cellbody images." % len(images_cells))



# Generate dignostics for segmentation performance
print("\nGenerating Diagnostics.")
Diagnosis = Diagnostics(Names)
Diagnosis.Montage_RandomSelectionZoom()


