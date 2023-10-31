import math
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = (10/2.54, 8/2.54)   # in inches. Divide by 2.54 for cm


# plates
file5 = "../results_plates5and6_minAgg9px/Statistics_Plate_Controls_Col5_Col13_Plate5_PercentAggregatePosCells.txt"
file6 = "../results_plates5and6_minAgg9px/Statistics_Plate_Controls_Col5_Col13_Plate6_PercentAggregatePosCells.txt"
plates = "5and6"

# read data
data5 = np.loadtxt(file5, skiprows=1)
data6 = np.loadtxt(file6, skiprows=1)
alldata = np.concatenate((data5, data6), axis=0)

Nwells = np.shape(alldata)[0]
Ncases = np.shape(alldata)[1]


scatter_width = 0.4

plt.scatter(1-0.5*scatter_width + scatter_width*np.random.rand(Nwells), alldata[:,0], facecolors='none', edgecolors='gray')
plt.scatter(2-0.5*scatter_width + scatter_width*np.random.rand(Nwells), alldata[:,1], facecolors='none', edgecolors='gray')
plt.scatter(3-0.5*scatter_width + scatter_width*np.random.rand(Nwells), alldata[:,2], facecolors='none', edgecolors='gray')
plt.scatter(4-0.5*scatter_width + scatter_width*np.random.rand(Nwells), alldata[:,3], facecolors='none', edgecolors='gray')
# errorbars
plt.errorbar(1, np.mean(alldata[:,0]), yerr=np.std(alldata[:,0]), ecolor='k', elinewidth=2, capthick=2, capsize=4)
plt.errorbar(2, np.mean(alldata[:,1]), yerr=np.std(alldata[:,1]), ecolor='k', elinewidth=2, capthick=2, capsize=4)
plt.errorbar(3, np.mean(alldata[:,2]), yerr=np.std(alldata[:,2]), ecolor='k', elinewidth=2, capthick=2, capsize=4)
plt.errorbar(4, np.mean(alldata[:,3]), yerr=np.std(alldata[:,3]), ecolor='k', elinewidth=2, capthick=2, capsize=4)
# means
plt.scatter(np.linspace(1,4,4), [np.mean(alldata[:,0]), np.mean(alldata[:,1]), np.mean(alldata[:,2]), np.mean(alldata[:,3])], marker='s', facecolors='k', edgecolors='k' )

# axis
axis = plt.gca()
axis.set_xticks( np.linspace(1, Ncases, Ncases ) )
axis.set_xticklabels( ["NT_1", "Rab13_1", "NT_2", "Rab13_2"] )
axis.set_ylabel("Percentage of aggregate positive cells")
plt.ylim([0,80])
axis.set_yticks( np.linspace(0, 80, 20 ) )
plt.title("Plates 5 and 6")

# SSMD annotations
m1 = np.mean(alldata[:,0])
m2 = np.mean(alldata[:,1])
m3 = np.mean(alldata[:,2])
m4 = np.mean(alldata[:,3])
s1 = np.std(alldata[:,0])
s2 = np.std(alldata[:,1])
s3 = np.std(alldata[:,2])
s4 = np.std(alldata[:,3])
SSMD1 = (m1-m2)/(math.sqrt(s1*s1 + s2*s2))
SSMD2 = (m3-m4)/(math.sqrt(s3*s3 + s4*s4))
#axis.annotate(("SSMD=%.2f" % SSMD1), xy=(1, 80))
#axis.annotate(("SSMD=%.2f" % SSMD2), xy=(3, 80))
axis.text(1, np.max(alldata[:,0]+10), ("SSMD=%.2f" % SSMD1), color='black', bbox=dict(facecolor='none', edgecolor='black', boxstyle='round,pad=1'))
axis.text(3, np.max(alldata[:,2]+10), ("SSMD=%.2f" % SSMD2), color='black', bbox=dict(facecolor='none', edgecolor='black', boxstyle='round,pad=1'))


plt.savefig("Statistics_Plates_%s.png" % plates)
#plt.show()
plt.close()

