#!/bin/bash
set -eu

IMAGEJ=/home/neptun/Desktop/Fiji_AE.app

INSTALL="${IMAGEJ}/scripts/Plugins/Custom"

# Check if ImageJ path exists
if [ -d "$IMAGEJ" ]; then
    mkdir -p ${INSTALL}

    cp -r *.ijm ${INSTALL}/

    echo "(install.sh) Macros installed: ${INSTALL}/"
else
    echo "(install.sh) Directory ${IMAGEJ} does not exist. Please provide the correct path to ImageJ/Fiji."
    exit
fi

