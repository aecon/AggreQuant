run("Split Channels");
t = getList("image.titles");
run("Merge Channels...", "c4=" +t[0]+ " c6=" +t[1]+ " create");
Stack.setChannel(1);
resetMinAndMax();
run("Enhance Contrast", "saturated=0.35");
Stack.setChannel(2);
resetMinAndMax();
run("Enhance Contrast", "saturated=0.35");