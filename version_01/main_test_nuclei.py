import os
import sys
import glob
import time
import argparse

from multiprocessing import Pool

from utils.fileinfo import FileInfo
from segmentation.nuclei import Nuclei
# from segmentation.cells import cellbody_segmentation
# from segmentation.aggregates import aggregate_segmentation
# from postprocess.diagnostics import Diagnostics


start = time.time()
def stamp(s):
    sys.stderr.write("%d: %s\n" % (time.time() - start, s))


def process_nuclei(fileInfo, image_list):
    nuclei = Nuclei(fileInfo)
    nuclei.segment_nuclei(image_list)
    return nuclei


def process_cells(fileInfo, image_list):
    print("TODO")
    sys.exit()


def process_aggregates(fileInfo, image_list):
    print("TODO")
    sys.exit()



def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, required=True, help="paths.txt file with path to tifs, and colour identifiers")
    parser.add_argument('-debug', action='store_true')
    parser.add_argument('-verbose', action='store_true')
    args = parser.parse_args()


    if os.path.exists(args.i):
        if args.verbose:
            print("\nReading paths and colours from file: %s \n" % args.i)
    else:
        print("File %s does NOT exist! Give a valid path to a file." % args.i)
        sys.exit()

    with open(args.i) as file:
        for line in file:

            if line.find("PATH_TO_IMAGES")==0:
                path_to_dir = (line.split(sep="=")[1].rstrip()).replace("\"", "")

                if os.path.exists(path_to_dir) == True:
                    print("Processing directory: %s" % path_to_dir)
                else:
                    print("Directory %s does NOT exist! Make sure that there are no spaces before/after the = symbol in %s" % (path_to_dir, args.i))
                    sys.exit()

            if line.find("COLOUR_NUCLEI")==0:
                CNUCLEI = (line.split(sep="=")[1].rstrip()).replace("\"", "")
                if args.verbose:
                    print("COLOUR_NUCLEI = %s" % CNUCLEI)

            if line.find("COLOUR_AGGREGATES")==0:
                CAGGREGATES = (line.split(sep="=")[1].rstrip()).replace("\"", "")
                if args.verbose:
                    print("COLOUR_AGGREGATES = %s" % CAGGREGATES)

            if line.find("COLOUR_CELLS")==0:
                CCELLS = (line.split(sep="=")[1].rstrip()).replace("\"", "")
                if args.verbose:
                    print("COLOUR_CELLS = %s" % CCELLS)




    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Filename conventions
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    fileInfo = FileInfo()

    # color identifiers in tif files
    fileInfo.COLOR_NUCLEI = CNUCLEI
    fileInfo.COLOR_CELLS = CCELLS
    fileInfo.COLOR_AGGREGATES = CAGGREGATES

    # folders
    fileInfo.INPUT_DIR = path_to_dir
    fileInfo.OUTPUT_DIR = "%s/output_V0.5_gpu_v1" % fileInfo.INPUT_DIR

    # nuclei segmentation
    fileInfo.NUCLEI_SEEDS = "seeds"
    fileInfo.NUCLEI_ALL_LABELS = "allLabels"

#    # cellbody segmentation
#    fileInfo.CELLBODY_SEGMENTATION_TYPE = "distance" #"propagation"  #"distance"
#    fileInfo.CELLBODY_ODIR_NAME = "cellbodies_%s" % fileInfo.CELLBODY_SEGMENTATION_TYPE
#
#    # aggregate segmentation
#    fileInfo.AGGREGATE_SEGMENTATION_TYPE = "intensity"
#    fileInfo.AGGREGATE_ODIR_NAME = "aggregates_%s" % fileInfo.AGGREGATE_SEGMENTATION_TYPE
#
#    # diagnostics
#    fileInfo.COMPOSITE_RAW_NUCLEI_EDGES = "composite_edges" # same as in nuclei.py
#    fileInfo.COMPOSITE_CELLS_AND_NUCLEI = "composite_nuclei"




    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Image processing
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


    # Nuclei segmentation
    if args.verbose:
        print("\nRunning nuclei segmentation.")

    images_nuclei = sorted(glob.glob("%s/*%s*.tif" % (fileInfo.INPUT_DIR, fileInfo.COLOR_NUCLEI)))

    stamp("A")
    nuclei = process_nuclei(fileInfo, images_nuclei)
    stamp("B")

    assert(0)



    # Create a pool of worker processes
    #pool = Pool(processes=32)  # Number of CPU cores
    #
    # Process images in parallel using the worker processes
    #pool.map(process_nuclei, images_nuclei)  # images is the list of 10,000 images
    #pool.starmap(process_nuclei, [(fileInfo.OUTDIR, path) for path in images_nuclei[0:10]])
    #
    # Close the pool of worker processes
    #pool.close()
    #pool.join()

    assert(0)



#    if 0:
#        print("\n Running cellbody segmentation.")
#        images_cells = sorted(glob.glob("%s/*%s*.tif" % (path_to_dir, CCELLS)))
#        print("Found %d cellbody images." % len(images_cells))
#        if args.debug == True:
#            print("Running in debug mode. Processing only 5 first images")
#            cellbody_segmentation(images_cells[0:5], fileInfo)
#        else:
#            cellbody_segmentation(images_cells, fileInfo)
#    
#    if 0:
#        print("\n Running aggregate segmentation.")
#        images_agg = sorted(glob.glob("%s/*%s*.tif" % (path_to_dir, CAGGREGATES)))
#        print("Found %d aggregate images." % len(images_agg))
#        if args.debug == True:
#            print("Running in debug mode. Processing only 5 first images")
#            aggregate_segmentation(images_agg[0:5], fileInfo)
#        else:
#            aggregate_segmentation(images_agg, fileInfo)
#    
#    
#    
#    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    # Diagnostics
#    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    
#    # Generate dignostics for segmentation performance
#    Diagnosis = Diagnostics(fileInfo, args.debug)
#    
#    if 0:
#        print("\nGenerating nuclei Diagnostics.")
#        Diagnosis.Montage_nuclei_RandomSelectionZoom()
#    
#    if 0:
#        print("\nGenerating cellbody Diagnostics.")
#        Diagnosis.Montage_cells_RandomSelectionZoom()
    


if __name__ == '__main__':
    main()


