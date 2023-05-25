title0 = getTitle();
selectWindow(title0);

resetMinAndMax();
run("Enhance Contrast", "saturated=0.35");

run("Subtract Background...", "rolling=50");

run("Enhance Local Contrast (CLAHE)", "blocksize=127 histogram=256 maximum=3 mask=*None*");
//run("Enhance Local Contrast (CLAHE)", "blocksize=10 histogram=256 maximum=3 mask=*None*");

rename("Nuclei raw");

run("Command From Macro", "command=[de.csbdresden.stardist.StarDist2D], args=['input':'Nuclei raw', 'modelChoice':'Versatile (fluorescent nuclei)', 'normalizeInput':'true', 'percentileBottom':'1.0', 'percentileTop':'99.8', 'probThresh':'0.479071', 'nmsThresh':'0.3', 'outputType':'Both', 'nTiles':'1', 'excludeBoundary':'2', 'roiPosition':'Automatic', 'verbose':'false', 'showCsbdeepProgress':'false', 'showProbAndDist':'false'], process=[false]");

run("Duplicate...", "title=Edges");
run("Find Edges");
setThreshold(1, 65535, "raw");
run("Convert to Mask");
run("Dilate");
run("Invert");

imageCalculator("AND create", "Edges","Label Image");
selectWindow("Result of Edges");
rename("Nuclei Candidates");
selectWindow("Nuclei Candidates");
setThreshold(1, 255, "raw");
run("Convert to Mask");

selectWindow("Label Image");
close();

selectWindow("Nuclei Candidates");
run("Analyze Particles...", "size=200-Infinity show=Masks exclude clear");
rename("Nuclei");

saveAs("Tiff", "/media/neptun/LocalDisk16TB/Athena/PROJECT_aSyn/ViaFlo 090523/AE_tests/Nuclei mask.tif");
run("Find Edges");
run("Invert LUT");
run("Dilate");
saveAs("Tiff", "/media/neptun/LocalDisk16TB/Athena/PROJECT_aSyn/ViaFlo 090523/AE_tests/Nuclei Edges mask.tif");

selectWindow("Nuclei Candidates");
saveAs("Tiff", "/media/neptun/LocalDisk16TB/Athena/PROJECT_aSyn/ViaFlo 090523/AE_tests/Nuclei Candidates mask.tif");
close();

selectWindow("Edges");
saveAs("Tiff", "/media/neptun/LocalDisk16TB/Athena/PROJECT_aSyn/ViaFlo 090523/AE_tests/Nuclei Candidates Edges mask.tif");



selectWindow("Nuclei Candidates Edges mask.tif");
run("Invert");
run("16-bit");

selectWindow("Nuclei Edges mask.tif");
run("16-bit");

run("Merge Channels...", "c4=Nuclei raw c5=[Nuclei Candidates Edges mask.tif] create keep ignore");
rename("Composite Nuclei Candidates");
saveAs("Tiff", "/media/neptun/LocalDisk16TB/Athena/PROJECT_aSyn/ViaFlo 090523/AE_tests/Composite Nuclei Candidates.tif");

run("Merge Channels...", "c4=Nuclei raw c5=[Nuclei Edges mask.tif] create keep ignore");
rename("Composite Nuclei");
saveAs("Tiff", "/media/neptun/LocalDisk16TB/Athena/PROJECT_aSyn/ViaFlo 090523/AE_tests/Composite Nuclei.tif");

run("Close All");

