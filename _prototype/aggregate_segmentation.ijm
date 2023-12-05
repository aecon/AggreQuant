// Segmentation of aggregates

title0=getTitle();

run("Duplicate...", "title=norm duplicate");
titleNorm=getTitle();

selectImage(titleNorm);
run("Max...", "value=3500 stack");
run("Gaussian Blur...", "sigma=100 stack");

imageCalculator("Divide create 32-bit stack", title0,titleNorm);
titleFore=getTitle();

selectImage(titleFore);
run("Gaussian Blur...", "sigma=3 stack");

setAutoThreshold("Default dark no-reset");
setThreshold(2.2, 1000000000000000000000000000000);
run("Convert to Mask", "background=Dark black");

run("Properties...", "channels=1 slices=20 frames=1 pixel_width=1 pixel_height=1 voxel_depth=1");

run("Median...", "radius=4 stack");

run("Analyze Particles...", "size=9-Infinity pixel show=Masks clear include stack");
