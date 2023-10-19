import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import *

window = tk.Tk()

window.title('aSynuclein processing')
window.geometry('600x200')

window.columnconfigure([0, 1, 2], minsize=100)
window.rowconfigure([0, 1, 2, 3], minsize=30)


# Directory selection
folder_path = StringVar(window, value="")

def browse_button():
    # Allow user to select a directory and store it in global var
    # called folder_path
    filename = filedialog.askdirectory(parent = window,
        initialdir="/media/neptun/LocalDisk16TB", title="Dialog box")
    folder_path.set(filename)

label0 = tk.Label(text="Input directory containing all tif files:")
label0.grid(row=0, column=0)
#entry0 = tk.Entry(width=30, textvariable=folder_path)
#entry0.grid(row=0, column=1)
label0 = tk.Label(textvariable=folder_path)
label0.grid(row=0, column=1)
button1 = ttk.Button(window, text="Browse", command=browse_button)
button1.grid(row=0, column=2)


#Create a label and a Button to Open the dialog
#dialog_btn = ttk.Button(window, text="select directory", command=directory)
#dialog_btn.grid(row=0, column=0)


entry_width = 30

# Nuclei filename
my_row = 1
label2 = tk.Label(text="Filename label for nuclei")
label2.grid(row=my_row, column=0, sticky="nw")
entry1 = tk.Entry(width=entry_width)
entry1.grid(row=my_row, column=1, sticky="nw")
colour_nuclei = entry1.get()

# Cells filename
my_row = 2
label3 = tk.Label(text="Filename label for nuclei")
label3.grid(row=my_row, column=0, sticky="nw")
entry3 = tk.Entry(width=entry_width)
entry3.grid(row=my_row, column=1, sticky="nw")
colour_cells = entry3.get()

# Aggregates filename
my_row = 3
label4 = tk.Label(text="Filename label for aggregates")
label4.grid(row=my_row, column=0, sticky="nw")
entry4 = tk.Entry(width=entry_width)
entry4.grid(row=my_row, column=1, sticky="nw")
colour_aggregates = entry4.get()


# Quits the program when certain button is clicked
button2 = tk.Button(window, text="OK", command=window.quit)
button2.grid()

print("\nSummary of user choices:'")
print("Nuclei label:", colour_nuclei)
print("Cell label:", colour_cells)
print("Aggregates label:", colour_aggregates)
print("Selected input folder:", folder_path.get())

# window.mainloop() tells Python to run the
# Tkinter event loop. This method listens for 
# events, such as button clicks or keypresses
window.mainloop()


