#!/usr/bin/python3

import os
import sys
import glob
import argparse


###############################
# RUN AS:
# ./rename.py -f "DRAG AND DROP PLATE FOLDER"
#
# EDIT HERE
pattern_from = "Plate2_"   # very important!! We need the underscore in the end
pattern_to   = "Plate2B_"
###############################



parser = argparse.ArgumentParser()
parser.add_argument('-f', type=str, required=True, help="path to Green folder")
args = parser.parse_args()

# Find all files
files = sorted(glob.glob("%s/*%s*" % (args.f, pattern_from)))

print("\nFound %d files\n" % len(files))

# Rename files
for f in files:
    print("processing:", f)

    # get filename
    filename = os.path.basename(f)

    # split using pattern
    f0 = filename.split("%s" % pattern_from)
    prefix = f0[0]
    suffix = f0[1]

    # new filename
    new_filename = "%s%s%s" % (prefix, pattern_to, suffix)
    new_path = "%s/%s" % (os.path.dirname(f), new_filename)

    # rename file
    os.rename(f, new_path)

