#!/home/neptun/.local/miniconda3/envs/tf/bin/python


import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import *


class GUI:

    def __init__(self):
        self.window = tk.Tk()
        self.input_folder = tk.StringVar(self.window, value="")
        self.entry_width = 30
        self.colour_nuc = tk.StringVar(self.window, value="")
        self.colour_cel = tk.StringVar(self.window, value="")
        self.colour_agg = tk.StringVar(self.window, value="")

        self._initialize()
        self._makelayout()


    def _initialize(self):
        self.window.title('aSynuclein processing')
        self.window.geometry('550x200')
        self.window.columnconfigure([0, 1, 2], minsize=100)
        self.window.rowconfigure([0, 1, 2, 3, 4], minsize=30)


    def _browse_button(self):
        # Allow user to select a directory and store it in global var
        # called folder_path
        filename = filedialog.askdirectory(parent = self.window,
            initialdir="/media/neptun/LocalDisk16TB", title="Dialog box")
        self.input_folder.set(filename)


    def _close(self):
        print("running _quit")
        self.colour_nuc.set(self.entry_nuc.get())
        self.colour_cel.set(self.entry_cel.get())
        self.colour_agg.set(self.entry_agg.get())
        self.window.quit()


    def _makelayout(self):

        row = 0

        # Directory selection
        label0 = tk.Label(text="Input directory containing all tif files:")
        label0.grid(row=row, column=0)

        label1 = tk.Label(textvariable=self.input_folder)
        label1.grid(row=row, column=1)

        button1 = ttk.Button(self.window, text="Browse", command=self._browse_button)
        row += 1
        button1.grid(row=1, column=0, sticky="ne")

        # Nuclei filename
        row += 1
        label_nuc = tk.Label(text="Filename label for nuclei")
        label_nuc.grid(row=row, column=0, sticky="nw", pady=10)

        self.entry_nuc = tk.Entry(width=self.entry_width)
        self.entry_nuc.grid(row=row, column=1, sticky="nw", pady=10)

        # Cells filename
        row += 1
        label_cel = tk.Label(text="Filename label for nuclei")
        label_cel.grid(row=row, column=0, sticky="nw")

        self.entry_cel = tk.Entry(width=self.entry_width)
        self.entry_cel.grid(row=row, column=1, sticky="nw")

        # Aggregates filename
        row += 1
        label_agg = tk.Label(text="Filename label for aggregates")
        label_agg.grid(row=row, column=0, sticky="nw")

        self.entry_agg = tk.Entry(width=self.entry_width)
        self.entry_agg.grid(row=row, column=1, sticky="nw")

        # Close the dialog when button is clicked
        button_OK = tk.Button(self.window, text="OK", command=self._close)
        button_OK.grid(sticky="se", pady=10)

        # run the tkinter event loop. It listens for 
        # events, such as button clicks or keypresses
        self.window.mainloop()
        self.window.destroy()




gui = GUI()

print("input folder:", gui.input_folder.get())
print("label nuclei:", gui.colour_nuc.get())
print("label cells:", gui.colour_cel.get())
print("label aggregates:", gui.colour_agg.get())


