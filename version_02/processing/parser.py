import os
import sys


class FileParser:

    def __init__(self, args):

        self.pathfile = args.i
        self.verbose = args.verbose
        self.debug = args.debug
        self.dump_tifs = args.dump_tifs

        self.input_directory = ""
        self.COLOUR_NUCLEI = ""
        self.COLOUR_AGGREGATES = "" 
        self.COLOUR_CELLS = ""


        # check if paths file exists
        if os.path.exists(self.pathfile):
            if self.verbose:
                print("\nReading paths and colours from file: %s \n" % self.pathfile)
        else:
            print("File %s does NOT exist! Give a valid path to a file." % self.pathfile)
            sys.exit()

        # parse paths file
        with open(self.pathfile) as file:
            for line in file:

                if line.find("PATH_TO_IMAGES")==0:
                    path_to_dir = (line.split(sep="=")[1].rstrip()).replace("\"", "")

                    if os.path.exists(path_to_dir) == True:
                        print("Processing directory: %s" % path_to_dir)
                        self.input_directory = path_to_dir
                    else:
                        print("Directory %s does NOT exist! Make sure that there are no spaces before/after the = symbol in %s" % (path_to_dir, self.pathfile))
                        sys.exit()

                if line.find("COLOUR_NUCLEI")==0:
                    self.COLOUR_NUCLEI = (line.split(sep="=")[1].rstrip()).replace("\"", "")
                    if self.verbose:
                        print("COLOUR_NUCLEI = %s" % self.COLOUR_NUCLEI)

                if line.find("COLOUR_AGGREGATES")==0:
                    self.COLOUR_AGGREGATES = (line.split(sep="=")[1].rstrip()).replace("\"", "")
                    if self.verbose:
                        print("COLOUR_AGGREGATES = %s" % self.COLOUR_AGGREGATES)

                if line.find("COLOUR_CELLS")==0:
                    self.COLOUR_CELLS = (line.split(sep="=")[1].rstrip()).replace("\"", "")
                    if self.verbose:
                        print("COLOUR_CELLS = %s" % self.COLOUR_CELLS)


