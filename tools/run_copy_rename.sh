#!/bin/bash
set -eu


# Parse argument
DIRECTORY=$1

# Check if input directory exists
if [ ! -d "$DIRECTORY" ]; then
    echo "$DIRECTORY does NOT exist. Please give the path to the directory containing the tif files."
    exit
fi

# Check if the input directory contains "Plate" in it
if [[ ${DIRECTORY} == *"Plate"* ]]; then
    echo "Processing directory: ${DIRECTORY}"
else
    echo "${DIRECTORY} does not contain 'Plate' in its name. Exiting."
    exit
fi


# Define output directories
onuc="$DIRECTORY/Blue"
ocel="$DIRECTORY/FarRed"
oagg="$DIRECTORY/Green"

# Create output directories
mkdir -p "$onuc"
mkdir -p "$ocel"
mkdir -p "$oagg"

# Get plate number
plateID=`basename "${DIRECTORY}" | awk -F '_Plate_' '{print $2}' | awk -F '_' '{print $1}'`
echo "Processing plate: $plateID"


# Move images
# nuclei
ls "${DIRECTORY}"/*Blue*.tif | while read f
do
    ls "${f}"
    base=`basename "${f}"`
    mv "${f}" "${onuc}/Plate${plateID}_${base}"
done


# cells
ls "${DIRECTORY}"/*FarRed*.tif | while read f
do
    ls "${f}"
    base=`basename "${f}"`
    mv "${f}" "${ocel}/Plate${plateID}_${base}"
done


# aggregates
ls "${DIRECTORY}"/*Green*.tif | while read f
do
    ls "${f}"
    base=`basename "${f}"`
    mv "${f}" "${oagg}/Plate${plateID}_${base}"
done


