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

* Uses [Cellpose](https://github.com/mouseland/cellpose) pre-trained DL.

```
conda activate cellpose
python cells_cp.py -i <path-to-tif>
```

### aSyn aggregate segmentation

```
python3 aggregates.py -i <path-to-tif>
```


