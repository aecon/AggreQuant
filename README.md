# aSynAgreeCount


## Requirements

* [scikit-image](https://scikit-image.org/docs/stable/user_guide/install.html)
* [tensorflow2](//www.tensorflow.org/install/pip)
* [StarDist](https://github.com/stardist/stardist)
* [pytest](https://docs.pytest.org/en/7.4.x/)



## Modules

### Nuclei segmentation

* Uses [StarDist](https://github.com/stardist/stardist) pre-trained DL.
* Results improve if Background Equalization is done before segmentation.

```
conda activate tf
```

Installation:  
* tensorflow: https://www.tensorflow.org/install/pip
* cupy: https://docs.cupy.dev/en/stable/install.html (`conda install -c conda-forge cupy`)
* pip install scikit-image
* pip install stardist


### Cell membrane segmentation

* Using [Cellpose](https://github.com/mouseland/cellpose) pre-trained DL.

```
conda activate cellpose
```

* Using the Propagation algorithm from [CellProfiler](https://cellprofiler.org).  

    * Identifies cell boundary as a Secondary object.  
    * Uses primary objects seeds.  
    * Secondary objects are identified based on the shortest path to an adjacent primary object.  
    * The distance metric is a sum of the absolute differences in a 3x3 (8-connected) kernel.  
    * The dividing lines between secondary objects are determined by a combination of: the distance to the nearest primary object, and intensity gradients.  


### aggregate segmentation

- Uses conventional Image Processing filters. Requires `scikit-image`.



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

