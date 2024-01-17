# aSynAgreeCount

Codebase for analysis of High Content Screens.



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
    pip install scikit-image matplotlib click pytest pyyaml pandas plotly kaleido
-->




## Modules

### Nuclei segmentation

* Uses [StarDist](https://github.com/stardist/stardist) pre-trained DL.
* Note: Results improve if Background Equalization is done before segmentation.

<!---
Installation:  
* tensorflow: https://www.tensorflow.org/install/pip
* cupy: https://docs.cupy.dev/en/stable/install.html (`conda install -c conda-forge cupy`)
* pip install scikit-image
* pip install stardist
-->

### Cell membrane segmentation

* Using [Cellpose](https://github.com/mouseland/cellpose) pre-trained DL.

* Using the Propagation algorithm from [CellProfiler](https://cellprofiler.org).  

    * Identifies cell boundary as a Secondary object.  
    * Uses primary objects seeds.  
    * Secondary objects are identified based on the shortest path to an adjacent primary object.  
    * The distance metric is a sum of the absolute differences in a 3x3 (8-connected) kernel.  
    * The dividing lines between secondary objects are determined by a combination of: the distance to the nearest primary object, and intensity gradients.  


### aggregate segmentation

* Uses a sequence of conventional Image Processing filters.

<!---
### Unit tests

```
conda install pytest
cd unitTests
./run.sh
```
-->


## TODOs
* [ ] Expose image processing parameters to the user.
* [ ] Test nnU-Net for cell and nuclei segmentation. Run on validation cases.
* [ ] Parallelize computations over image sets (see _prototype/multiprocess examples).
* [ ] Train a classifier to detect images that the software cannot process and alert the user about how many unprocessable images exist.
* [ ] Add more unit tests.


<!---
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
-->



## Authors

The code was written by Athena Economides. The corresponding publication is in preparation.

Lab of Prof. Adriano Aguzzi  
Institute of Neuropathology  
University of Zurich  
Schmelzbergstrasse 12  
CH-8091 Zurich  
Switzerland

