import os
import sys
import argparse

from processing.processor import ImageProcessor

# File parsing
parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, required=True, help="paths.txt file with path to tifs, and colour identifiers")
parser.add_argument('-debug', action='store_true')
parser.add_argument('-verbose', action='store_true')

# To generate validation montages (4x5 layout)
parser.add_argument('-validation', action='store_true')

# To write results inside a default folder: <outdir>/`validation`
parser.add_argument('-overwrite_output_folder', action='store_true')

# To dump tifs from the QoI computation process
parser.add_argument('-dump_QoI_tifs', action='store_true')

args = parser.parse_args()


# IMAGE PROCESSING + ANALYSIS PIPELINE

# Create the processor
processor = ImageProcessor(args)

# Set the folder/file paths
processor.set_paths()

# Image Processing + QoI computation
processor.process()

# Generate statistics
#processor.generate_statistics()

# Generate diagnostic images (montage)
processor.make_montage()

