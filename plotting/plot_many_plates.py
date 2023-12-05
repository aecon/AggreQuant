import math
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = (7/2.54, 8/2.54)   # in inches. Divide by 2.54 for cm


# plates
#file5 = "../results_plates5and6_minAgg9px/Statistics_Plate_Controls_Col5_Col13_Plate5_PercentAggregatePosCells.txt"
#file6 = "../results_plates5and6_minAgg9px/Statistics_Plate_Controls_Col5_Col13_Plate6_PercentAggregatePosCells.txt"
#plates = "5and6"

#file5 = "../results_plates_HA_4_7_8_18/Statistics_Plate_inCell_transfer_20230624_HA_4_badplate_plate7_HA_4_rep1_PercentAggregatePosCells.txt"
#file6 = "../results_plates_HA_4_7_8_18/Statistics_Plate_inCell_transfer_20230624_HA_4_badplate_plate8_HA_4_rep2_PercentAggregatePosCells.txt"
#plates = "HA_4_rep1and2"

#file5 = "../RESULTS/results_plates_HA_4_NEWPARAMETERS/Statistics_Plate_plate7_HA_4_rep1_data_PercentAggregatePosCells.txt"
#file6 = "../RESULTS/results_plates_HA_4_NEWPARAMETERS/Statistics_Plate_plate8_HA_4_rep2_data_PercentAggregatePosCells.txt"
#plates = "HA_4"

#file5 = "../Statistics_Plate_Controls_Col5_Col13_Plate5_PercentAggregatePosCells.txt"
#file6 = "../Statistics_Plate_Controls_Col5_Col13_Plate6_PercentAggregatePosCells.txt"
#plates = "HA_3"


# 2023, November 05
#file5 = "../RESULTS/results_2023Nov5/Statistics_Plate_Controls_Col5_Col13_Plate5_PercentAggregatePosCells.txt"
#file6 = "../RESULTS/results_2023Nov5/Statistics_Plate_Controls_Col5_Col13_Plate6_PercentAggregatePosCells.txt"
#plates = "HA_3"

file5 = "../RESULTS/results_2023Nov5/Statistics_Plate_plate7_HA_4_rep1_data_PercentAggregatePosCells.txt"
file6 = "../RESULTS/results_2023Nov5/Statistics_Plate_plate8_HA_4_rep2_data_PercentAggregatePosCells.txt"
plates = "HA_4"

#file5 = "../RESULTS/results_2023Nov5/Statistics_Plate_inCell_transfer_20230930_HA_7-HA_8-HA_13_goodplates_plate1_HA_7_rep1_PercentAggregatePosCells.txt"
#file6 = "../RESULTS/results_2023Nov5/Statistics_Plate_inCell_transfer_20230930_HA_7-HA_8-HA_13_goodplates_plate2_HA_7_rep2_PercentAggregatePosCells.txt"
#plates = "HA_7"

#file5 = "../RESULTS/results_2023Nov5/Statistics_Plate_inCell_transfer_20230930_HA_7-HA_8-HA_13_goodplates_plate3_HA_8_rep1_PercentAggregatePosCells.txt"
#file6 = "../RESULTS/results_2023Nov5/Statistics_Plate_inCell_transfer_20230930_HA_7-HA_8-HA_13_goodplates_plate4_HA_8_rep2_PercentAggregatePosCells.txt"
#plates = "HA_8"

#file5 = "../RESULTS/results_2023Nov5/Statistics_Plate_inCell_transfer_20230930_HA_7-HA_8-HA_13_goodplates_plate5_HA_13_rep1_PercentAggregatePosCells.txt"
#file6 = "../RESULTS/results_2023Nov5/Statistics_Plate_inCell_transfer_20230930_HA_7-HA_8-HA_13_goodplates_plate6_HA_13_rep2_PercentAggregatePosCells.txt"
#plates = "HA_13"





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
plt.errorbar(1, np.nanmean(col_NT1), yerr=np.nanstd(col_NT1), ecolor='k', elinewidth=2, capthick=2, capsize=4)
plt.errorbar(2, np.nanmean(col_RP1), yerr=np.nanstd(col_RP1), ecolor='k', elinewidth=2, capthick=2, capsize=4)
plt.errorbar(3, np.nanmean(col_NT2), yerr=np.nanstd(col_NT2), ecolor='k', elinewidth=2, capthick=2, capsize=4)
plt.errorbar(4, np.nanmean(col_RP2), yerr=np.nanstd(col_RP2), ecolor='k', elinewidth=2, capthick=2, capsize=4)
# means
plt.scatter(np.linspace(1,4,4), [np.mean(col_NT1), np.mean(col_RP1), np.mean(col_NT2), np.mean(col_RP2)], marker='s', facecolors='k', edgecolors='k' )

# axis
axis = plt.gca()
axis.set_xticks( np.linspace(1, Ncases, Ncases ) )
axis.set_xticklabels( ["NT_1", "Rab13_1", "NT_2", "Rab13_2"] , fontsize=8)
axis.set_ylabel("% positive cells", fontsize=14)

Ymax = 60
plt.ylim([0,Ymax])
axis.set_yticks( np.linspace(0, Ymax, 4 ) )

plt.title(plates)

# SSMD annotations
m1 = np.nanmean(col_NT1)
m2 = np.nanmean(col_RP1)
m3 = np.nanmean(col_NT2)
m4 = np.nanmean(col_RP2)
s1 = np.nanstd(col_NT1)
s2 = np.nanstd(col_RP1)
s3 = np.nanstd(col_NT2)
s4 = np.nanstd(col_RP2)
SSMD1 = (m1-m2)/(math.sqrt(s1*s1 + s2*s2))
SSMD2 = (m3-m4)/(math.sqrt(s3*s3 + s4*s4))
#axis.annotate(("SSMD=%.2f" % SSMD1), xy=(1, 80))
#axis.annotate(("SSMD=%.2f" % SSMD2), xy=(3, 80))
#axis.text(1, np.max(col_NT1)+10, ("SSMD=%.2f" % SSMD1), color='black', bbox=dict(facecolor='none', edgecolor='black', boxstyle='round,pad=1'))
#axis.text(3, np.max(col_NT2)+10, ("SSMD=%.2f" % SSMD2), color='black', bbox=dict(facecolor='none', edgecolor='black', boxstyle='round,pad=1'))
#axis.text(1, 5, ("SSMD=%.2f" % SSMD1), color='black', bbox=dict(facecolor='none', edgecolor='black', boxstyle='round,pad=1'))
#axis.text(3, 5, ("SSMD=%.2f" % SSMD2), color='black', bbox=dict(facecolor='none', edgecolor='black', boxstyle='round,pad=1'))
axis.text(0.5, -18/80*Ymax, ("SSMD=%.2f" % SSMD1), color='black')
axis.text(2.5, -18/80*Ymax, ("SSMD=%.2f" % SSMD2), color='black')

axis.spines['top'].set_visible(False)
axis.spines['right'].set_visible(False)


plt.tight_layout()


plt.savefig("Statistics_Plates_%s.png" % plates, transparent=True)
#plt.show()
plt.close()

