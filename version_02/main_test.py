import os
import sys
import argparse

from utils.parser import FileParser


parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, required=True, help="paths.txt file with path to tifs, and colour identifiers")
parser.add_argument('-debug', action='store_true')
parser.add_argument('-verbose', action='store_true')
args = parser.parse_args()


fileParser = FileParser(args)


