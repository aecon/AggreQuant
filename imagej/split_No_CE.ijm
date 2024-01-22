// get current title
title0=getTitle();

run("Duplicate...", "duplicate");
rename("p");

// select origina image and close it
selectImage(title0);
close();

// select duplicate image
selectImage("p");

// split stack
run("Stack to Images");

// select segmentation channel
selectImage("p-0002");
resetMinAndMax();
run("Find Edges");
setMinAndMax(0, 1);
setAutoThreshold("Default dark no-reset");
setOption("BlackBackground", true);
run("Convert to Mask");

// select raw channel
selectImage("p-0001");
run("Grays");

// Segmented: convert to 16-bit
selectImage("p-0002");
resetMinAndMax();
run("16-bit");

// Merge channels
run("Merge Channels...", "c4=p-0001 c6=p-0002 create ignore");
rename(title0);

//run("Brightness/Contrast...");
run("Enhance Contrast", "saturated=0.35");
