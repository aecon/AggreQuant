#!/bin/bash
set -eu


# Parse argument
DIRECTORY=$1

# Check if input directory exists
if [ ! -d "$DIRECTORY" ]; then
    echo "$DIRECTORY does NOT exist. Please give the path to the directory containing the tif files."
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
echo "$plateID"


# Move images
# nuclei
ls "${DIRECTORY}"/*Blue*.tif | while read f
do
    base=`basename "${f}"`
    echo "Copying  $f"
    mv "$f" "${onuc}/Plate${plateID}_${base}"
done


# cells
ls "${DIRECTORY}"/*FarRed*.tif | while read f
do
    base=`basename "${f}"`
    echo "Copying  $f"
    mv "$f" "${ocel}/Plate${plateID}_${base}"
done


# aggregates
ls "${DIRECTORY}"/*Green*.tif | while read f
do
    base=`basename "${f}"`
    echo "Copying  $f"
    mv "$f" "${oagg}/Plate${plateID}_${base}"
done


