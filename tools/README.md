# Tools for image processing



## Copy and Rename files

**- IMPORTANT - READ BEFORE USING**:  

* Plate folders are expected to have the identifier "_Plate_X" inside their name, where X is the plate number.
* The scipt will rename the tif files inside the Plate folder, by appending the Plate number at the beginning of the tif file-name.
* The script assumes that the tif files contain the identifiers "Blue", "Green", and "FarRed".

**- USAGE**:   
Open the terminal inside the folder that contains the `./run_copy_rename.sh` script (Right click -> Open in terminal).

Then, in the terminal type:
```
./run_copy_rename.sh
```
then drag and drop the Plate folder, from the File Window to the terminal.  
In the terminal you should have something like this:
```
./run_copy_rename.sh '/media/neptun/LocalDist16TB/MyName/SomePath/My_Plate_1_Folder'
```

If yes, then in the terminal, hit Enter.



## Miscellaneous

### Rendering Markdown files

```
pandoc README.md -o Instructions.pdf
```

See [StackOverflow](https://stackoverflow.com/questions/17630486/how-to-convert-a-markdown-file-to-pdf).


### Read only run files

```
chmod 500 run_copy_rename.sh
```

