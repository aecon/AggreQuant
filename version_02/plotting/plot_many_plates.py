import math
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = (10/2.54, 8/2.54)   # in inches. Divide by 2.54 for cm


# plates
#file5 = "../results_plates5and6_minAgg9px/Statistics_Plate_Controls_Col5_Col13_Plate5_PercentAggregatePosCells.txt"
#file6 = "../results_plates5and6_minAgg9px/Statistics_Plate_Controls_Col5_Col13_Plate6_PercentAggregatePosCells.txt"
#plates = "5and6"

#file5 = "../results_plates_HA_4_7_8_18/Statistics_Plate_inCell_transfer_20230624_HA_4_badplate_plate7_HA_4_rep1_PercentAggregatePosCells.txt"
#file6 = "../results_plates_HA_4_7_8_18/Statistics_Plate_inCell_transfer_20230624_HA_4_badplate_plate8_HA_4_rep2_PercentAggregatePosCells.txt"
#plates = "HA_4_rep1and2"

file5 = "../results_plates_HA_4_NEWPARAMETERS/Statistics_Plate_plate7_HA_4_rep1_data_PercentAggregatePosCells.txt"
file6 = "../results_plates_HA_4_NEWPARAMETERS/Statistics_Plate_plate8_HA_4_rep2_data_PercentAggregatePosCells.txt"
plates = "HA_4"



# read data
rep1 = np.loadtxt(file5, skiprows=1)
rep2 = np.loadtxt(file6, skiprows=1)
alldata = np.concatenate((rep1, rep2), axis=0)

Nwells = np.shape(alldata)[0]
Ncases = np.shape(alldata)[1]

# column data in plot: WRONG ARRANGEMENT TO MATCH HA_4 PLOT ..
col_NT1 = np.concatenate((rep1[:,0], rep1[:,2]), axis=0)
col_NT2 = np.concatenate((rep2[:,0], rep2[:,2]), axis=0)
col_RP1 = np.concatenate((rep1[:,1], rep1[:,3]), axis=0)
col_RP2 = np.concatenate((rep2[:,1], rep2[:,3]), axis=0)


scatter_width = 0.4

plt.scatter(1-0.5*scatter_width + scatter_width*np.random.rand(Nwells), col_NT1, facecolors='none', edgecolors='gray')
plt.scatter(2-0.5*scatter_width + scatter_width*np.random.rand(Nwells), col_RP1, facecolors='none', edgecolors='gray')
plt.scatter(3-0.5*scatter_width + scatter_width*np.random.rand(Nwells), col_NT2, facecolors='none', edgecolors='gray')
plt.scatter(4-0.5*scatter_width + scatter_width*np.random.rand(Nwells), col_RP2, facecolors='none', edgecolors='gray')
# errorbars
plt.errorbar(1, np.mean(col_NT1), yerr=np.std(col_NT1), ecolor='k', elinewidth=2, capthick=2, capsize=4)
plt.errorbar(2, np.mean(col_RP1), yerr=np.std(col_RP1), ecolor='k', elinewidth=2, capthick=2, capsize=4)
plt.errorbar(3, np.mean(col_NT2), yerr=np.std(col_NT2), ecolor='k', elinewidth=2, capthick=2, capsize=4)
plt.errorbar(4, np.mean(col_RP2), yerr=np.std(col_RP2), ecolor='k', elinewidth=2, capthick=2, capsize=4)
# means
plt.scatter(np.linspace(1,4,4), [np.mean(col_NT1), np.mean(col_RP1), np.mean(col_NT2), np.mean(col_RP2)], marker='s', facecolors='k', edgecolors='k' )

# axis
axis = plt.gca()
axis.set_xticks( np.linspace(1, Ncases, Ncases ) )
axis.set_xticklabels( ["NT_1", "Rab13_1", "NT_2", "Rab13_2"] )
axis.set_ylabel("% positive cells", fontsize=14)
plt.ylim([0,80])
axis.set_yticks( np.linspace(0, 80, 5 ) )
plt.title(plates)

# SSMD annotations
m1 = np.mean(col_NT1)
m2 = np.mean(col_RP1)
m3 = np.mean(col_NT2)
m4 = np.mean(col_RP2)
s1 = np.std(col_NT1)
s2 = np.std(col_RP1)
s3 = np.std(col_NT2)
s4 = np.std(col_RP2)
SSMD1 = (m1-m2)/(math.sqrt(s1*s1 + s2*s2))
SSMD2 = (m3-m4)/(math.sqrt(s3*s3 + s4*s4))
#axis.annotate(("SSMD=%.2f" % SSMD1), xy=(1, 80))
#axis.annotate(("SSMD=%.2f" % SSMD2), xy=(3, 80))
axis.text(1, np.max(col_NT1)+10, ("SSMD=%.2f" % SSMD1), color='black', bbox=dict(facecolor='none', edgecolor='black', boxstyle='round,pad=1'))
axis.text(3, np.max(col_NT2)+10, ("SSMD=%.2f" % SSMD2), color='black', bbox=dict(facecolor='none', edgecolor='black', boxstyle='round,pad=1'))

plt.tight_layout()


plt.savefig("Statistics_Plates_%s.png" % plates)
#plt.show()
plt.close()

