import os
import sys
import argparse

from processing.processor import ImageProcessor

# File parsing
parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, required=True, help="paths.txt file with path to tifs, and colour identifiers")
parser.add_argument('-debug', action='store_true')
parser.add_argument('-dump_tifs', action='store_true')
parser.add_argument('-verbose', action='store_true')
args = parser.parse_args()


# IMAGE PROCESSING + ANALYSIS PIPELINE

# Create the processor
processor = ImageProcessor(args)

# Set the folder/file paths
processor.set_paths()

# Perform Image Processing + QoI computation
processor.process()

# Generate statistics
#processor.generate_statistics()

# Generate diagnostic images (montage)
#processor.make_montage()

