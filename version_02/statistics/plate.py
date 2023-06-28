
class Plate:

    def __init__(self, name):
        self.name = name
        self.Ncolumns = 24
        self.Nrows = 16
        self.Nfields = 9
        self.Nwells = 384
        self.ControlColumns = ["05", "13"]
        self.wells = [None] * self.Nwells


    def get_global_well_number(self, row, column):
        k = self.Ncolumns*row + column
        return k


    def get_row_letter(self, row):
        assert(row>=0 and row <self.Nrows)
        letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P"]
        return letters[row]


