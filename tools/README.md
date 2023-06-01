# Tools for image processing



## Copy and Rename files

**Note**:
* This tool assumes that your tif files contain the identifiers "Blue", "Green", and "FarRed".

Open the terminal inside this folder (Right click -> Open in terminal).

Then, in the terminal type:
```
./run_copy_rename.sh  <PATH>
```
where `<PATH>` is the full path to the plate directory, which contains the tiff images.

For example:
```
./run_copy_rename.sh /Documents/user/my new images/plate1
```

After you specified the PATH, hit Enter.



## Rendering Markdown files

```
pandoc README.md -o Instructions.pdf
```

See [StackOverflow](https://stackoverflow.com/questions/17630486/how-to-convert-a-markdown-file-to-pdf).

