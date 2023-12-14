"""
Paths to the currently processed data:
- a signle nuclei file
- a corresponding cells file
- a corresponding aggregates file
"""

class Data:
    def __init__(self, file_nuclei, file_cells, file_aggregates):
        # inputs
        self.n = file_nuclei
        self.c = file_cells
        self.a = file_aggregates
