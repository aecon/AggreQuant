# aSynAgreeCount

A python package for analysis of image-based, High-Throughput / High-Content Screens.



## Installation

### Conda environment
Create and activate a new conda environment
```
conda create --name aSynAgreeCount python=3.9.18
conda activate aSynAgreeCount
```

### Tensorflow
* [Installation instructions](https://www.tensorflow.org/install/pip)
* Summary:
```
# For GPU users:
pip install --extra-index-url https://pypi.nvidia.com tensorrt-bindings==8.6.1 tensorrt-libs==8.6.1
pip install -U tensorflow[and-cuda]
# Verification of the installation:
python3 -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

### StarDist
* [Installation instructions](https://github.com/stardist/stardist#installation)
* Summary:
```
pip install stardist
```

### Cellpose 2.0 with GUI  
* [Installation instructions](https://github.com/MouseLand/cellpose)
* Summary:
```
pip install cellpose[gui]
```

### Additional python packages
```
pip install -r requirements.txt
```
<!---
I installed:
    pip install scikit-image matplotlib click pytest pyyaml pandas plotly
-->




## Modules

### Nuclei segmentation

* Uses [StarDist](https://github.com/stardist/stardist) pre-trained DL.
* Results improve if Background Equalization is done before segmentation.

Installation:  
* tensorflow: https://www.tensorflow.org/install/pip
* cupy: https://docs.cupy.dev/en/stable/install.html (`conda install -c conda-forge cupy`)
* pip install scikit-image
* pip install stardist


### Cell membrane segmentation

* Using [Cellpose](https://github.com/mouseland/cellpose) pre-trained DL.

* Using the Propagation algorithm from [CellProfiler](https://cellprofiler.org).  

    * Identifies cell boundary as a Secondary object.  
    * Uses primary objects seeds.  
    * Secondary objects are identified based on the shortest path to an adjacent primary object.  
    * The distance metric is a sum of the absolute differences in a 3x3 (8-connected) kernel.  
    * The dividing lines between secondary objects are determined by a combination of: the distance to the nearest primary object, and intensity gradients.  


### aggregate segmentation

* Uses conventional Image Processing filters.


### Unit tests

```
conda install pytest
cd unitTests
./run.sh
```






## TODO

* [x] Diagnostics.
* [x] - E.g. random selection of images and zoom-in in a random location within each selected image.
* [x] - Show overlay of segmented Edges and raw in a Montage-type og figure.
* [x] - Do the above for both nuclei and cell boundary segmentations.
* [x] Data management: Rename data to include plate number in filename.
* [ ] Segmentation:
* [ ] - Finalize version 0.0. Include aggregate segmentation and quantification. Add validation cases.
* [ ] - Test nnU-Net for cell and nuclei segmentation. Run on validation cases.
* [ ] Validation: Select datasets and add to validation stack.
* [ ] Parallelize computations over image sets (see _prototype/multiprocess examples).
* [ ] Add option to use cellpose for cell detection
    * [ ] with only cell channel as input (terrible resutls)
    * [ ] with both nuclei and cell channel inputs

* For publication:
    * Data: `validation_dataset_Nov032023` for segmentation visuals and `inCell_transfer_20230930_HA_7-HA_8-HA_13_goodplates` for statistics.
    * [ ] Expose image processing parameters to user, so that multiple parameter sets can be tested.
    * [ ] CNN classifier to detect images than cannot be processed by the software and alert the user about how many unprocessable images exist :)





## Package tracking

To collect all packages used by the code, [pipreqs](https://github.com/bndr/pipreqs) is used.
```
conda install pipreqs
```

Collect installed packages:
```
pip freeze > requirements.txt
```

The packages inside the requirements.txt file can be installed with
```
pip install -r requirements.txt
```





## Authors

The package was written by Athena Economides, for the publication:

```
XXX TO BE ADDED XXX
```

Lab of Prof. Adriano Aguzzi  
Institute of Neuropathology  
University of Zurich  
Schmelzbergstrasse 12  
CH-8091 Zurich  
Switzerland

