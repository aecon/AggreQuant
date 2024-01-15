#!/bin/bash


## Validation dataset Nov 03, 2023
#python3 main_test.py -validation -overwrite_output_folder -i paths_ValidationNov2023.txt
## Validation dataset Oct 2023 (the first, 20image validation dataset)
#python3 main_test.py -validation -overwrite_output_folder -i paths_validation20.txt


## HA_3: Relatively good plates
python3 main_test.py -validation -overwrite_output_folder -i paths/paths_test_Controls_Plate5.txt
python3 main_test.py -validation -overwrite_output_folder -i paths/paths_test_Controls_Plate6.txt
## HA_4: Terrible plates: rep1 has very few cells, rep2 has too many
python3 main_test.py -validation -overwrite_output_folder -i paths/paths_test_Controls_Plate7_HA4rep1.txt
python3 main_test.py -validation -overwrite_output_folder -i paths/paths_test_Controls_Plate8_HA4rep2.txt
## HA_7: Good plate
python3 main_test.py -validation -overwrite_output_folder -i paths/paths_test_Controls_HA7_rep1.txt
python3 main_test.py -validation -overwrite_output_folder -i paths/paths_test_Controls_HA7_rep2.txt
## HA_8: Good plate
python3 main_test.py -validation -overwrite_output_folder -i paths/paths_test_Controls_HA8_rep1.txt
python3 main_test.py -validation -overwrite_output_folder -i paths/paths_test_Controls_HA8_rep2.txt
## HA_13: Good plate
python3 main_test.py -validation -overwrite_output_folder -i paths/paths_test_Controls_HA13_rep1.txt
python3 main_test.py -validation -overwrite_output_folder -i paths/paths_test_Controls_HA13_rep2.txt

# HA_10: Good plate
# Not great results, probably underdetecting everything

