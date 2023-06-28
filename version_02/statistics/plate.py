
class Plate:

    def __init__(self, name):
        self.name = name
        self.Ncolumns = 24
        self.Nrows = 16
        self.Nwells = 384
        self.ControlColumns = ["05", "13"]
        self.wells = [None] * self.Nwells


    def get_global_well_number(self, row, column):
        k = self.Ncolumns*row + column
        return k

