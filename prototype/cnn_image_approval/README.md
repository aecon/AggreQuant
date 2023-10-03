# Filter out images with CNNs


## Example images with evident artefacts

See `/media/neptun/LocalDisk16TB/Athena/PROJECT_aSyn/ViaFlo 090523/test_data_20img/raw_Blue/raw`. 


## ilastik predictions

* It predicts that blur is cells (are they excluded afterwards in cellprofiler?)


## Plan

* Split images into patches so that we increase the training dataset (see also data augmentation).
* Image resolution is 2048x2048 pixels. Can be converted to low res images so that eatch patch contains a reasonable amount of cels.
* Pre-classify images with other methods so that its easier to generate training labels.
* 

