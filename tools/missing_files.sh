#!/bin/bash
set -eu

PLATE=3
WELLS=('A' 'B' 'C' 'D' 'E' 'F' 'G' 'H' 'I' 'J' 'K' 'L' 'M' 'N' 'O' 'P')
NUMBERS=`seq 1 24`
FIELDS=`seq 1 9`

for w in ${WELLS[@]}; do
for n in ${NUMBERS[@]}; do
for l in ${FIELDS[@]}; do

    N=$(printf "%02d" $n)
    f="Plate${PLATE}_${w} - ${N}(fld ${l} wv 390 - Blue).tif"
    if [ ! -f "${f}" ]; then
        echo "File not found: ${f}"
    fi

done
done
done
