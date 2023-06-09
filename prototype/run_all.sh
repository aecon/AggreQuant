#!/bin/bash
set -eu

DATA="/media/neptun/LocalDisk16TB/Athena/PROJECT_aSyn/ViaFlo 090523/20230509_Dalila_Elena_GE_InCell/20230509_Dalila_Elena_GE_InCell_ViaFlo_1"

# aggregates
python3 aggregates.py -i "${DATA}"/*FarRed*.tif

LD_LIBRARY_PATH=
source /home/neptun/.local/miniconda3/etc/profile.d/conda.sh

# nuclei
conda activate tf
python nuclei.py -i "${DATA}"/*Blue*.tif
conda deactivate

# cytoplasm
conda activate cellpose
python cells_cp.py -i "${DATA}"/*Green2*.tif
conda deactivate

