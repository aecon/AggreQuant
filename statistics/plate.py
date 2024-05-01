from utils import printer as p


class Plate:


    def __init__(self, name, Ncolumns, Nrows, Nfields, control_types, control_wells):
        self.name = name
        self.Ncolumns = Ncolumns
        self.Nrows = Nrows
        self.Nfields = Nfields
        self.Nwells = self.Ncolumns * self.Nrows   # elements are in global index

        self.control_types = control_types   # ["NT", "Rab13"]
        self.control_wells = control_wells   # [ ["", "", ... control wells type 1], ["", "", ... control wells type 2], ... ]
        self.Nctypes = len(self.control_types)  # number of control types

        self.wells = [None] * self.Nwells
        self.wells_total_agg_pos_cells = [None] * self.Nwells
        self.wells_Ncells = [None] * self.Nwells
        self.wells_percent_area_aggregates_over_cells = [None] * self.Nwells

        self.alphabet = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        self.columns = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24"]


    def get_global_well_number(self, row, column):
        k = self.Ncolumns*row + column
        return k


    def get_row_letter(self, row):
        assert(row>=0 and row<self.Nrows)
        return self.alphabet[row]

    def get_row_number(self, row_letter):
        me = "Plate: get_row_number()"
        if row_letter in self.alphabet:
            return self.alphabet.index(row_letter)
        else:
            p.err("Row letter %s does not exist in the alphabet list." % row_letter, me)
            sys.exit()

    def get_column_number(self, col):
        me = "Plate: get_column_number()"
        assert(col>=0 and col<self.Ncolumns)
        if len(self.columns) <= col:
            p.err("Column number [%d] is larger than the list of column number IDs [0-%d]" % (col, len(self.columns)-1), me)
            sys.exit()
        else:
            return self.columns[col]

