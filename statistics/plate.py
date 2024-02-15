class Plate:


    def __init__(self, name):
        self.name = name
        self.Ncolumns = 24
        self.Nrows = 16
        self.Nfields = 9
        self.Nwells = 384
        self.ControlColumns = ["05", "13"]
        self.NumberOfControlRows = 8

        self.wells = [None] * self.Nwells
        self.wells_total_agg_pos_cells = [None] * self.Nwells
        self.wells_Ncells = [None] * self.Nwells
        self.wells_percent_area_aggregates_over_cells = [None] * self.Nwells


    def get_global_well_number(self, row, column):
        k = self.Ncolumns*row + column
        return k


    def get_row_letter(self, row):
        assert(row>=0 and row<self.Nrows)
        letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P"]
        return letters[row]


    def get_column_number(self, col):
        assert(col>=0 and col<self.Ncolumns)
        columns = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24"]
        return columns[col]

