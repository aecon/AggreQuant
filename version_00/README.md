# Version 0.0

First attempt of a multi-plate analysis, for the segmentation of nuclei, cell bodies and a-Syn aggregates.


## Instructions

Specify the path to the directory containing the tif images, and
the identifiers for the Nuclei, Aggregates and Cells, inside `paths.txt`.

An example for how `paths.txt` should look like is:

```
PATH_TO_IMAGES="/Documents/athena/trial_20230525_01"
COLOUR_NUCLEI="Blue"
COLOUR_AGGREGATES="Green2"
COLOUR_CELLS="FarRed"
```


## Requirements


### Nuclei segmentation

* Uses [StarDist](https://github.com/stardist/stardist) pre-trained DL.
* Results improve if Background Equalization is done before segmentation.



