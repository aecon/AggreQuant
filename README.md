# aSynAgreeCount


## Requirements

* tensorflow2
* [StarDist](https://github.com/stardist/stardist)



## Quantification


### Nuclei segmentation

* Uses [StarDist](https://github.com/stardist/stardist) pre-trained DL.
* Results improve if Background Equalization is done before segmentation.

```
conda activate tf
python nuclei.py -i <path-to-tif>
```

### Cell membrane segmentation

* Using [Cellpose](https://github.com/mouseland/cellpose) pre-trained DL.

```
conda activate cellpose
python cells_cp.py -i <path-to-tif>
```

* Using the Propagation algorithm from [CellProfiler](https://cellprofiler.org).  

- Identifies cell boundary as a Secondary object.  
- Uses primary objects seeds.  
- Secondary objects are identified based on the shortest path to an adjacent primary object.  
- The distance metric is a sum of the absolute differences in a 3x3 (8-connected) kernel.  
- The dividing lines between secondary objects are determined by a combination of: the distance to the nearest primary object, and intensity gradients.  



### aSyn aggregate segmentation

```
python3 aggregates.py -i <path-to-tif>
```



## TODO

Need to make diagnostics.
E.g. random selection of images and zoom-in in a random location within each selected image.
Show overlay of segmented Edges and raw in a Montage-type og figure.
Do the above for both nuclei and cell boundary segmentations.



