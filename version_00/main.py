import os
import sys
import glob
import argparse

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


print("\nRunning nuclei segmentation.")
images_nuclei = glob.glob("%s/*%s*.tif" % (path_to_dir, CNUCLEI))
print("Found %d nuclei images." % len(images_nuclei))
nuclei_paths = ""
for f in images_nuclei:
    nuclei_paths+=" '%s'" % f
os.system("conda run -n tf python nuclei.py -i %s" % (nuclei_paths))


