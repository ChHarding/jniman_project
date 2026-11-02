import os
from tkinter import *
from tkinter.filedialog import askopenfilename

class CanvasBackupApp(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("Canvas Backup Tool")
        self.geometry("620x300")

        #Tkinter state variables
        self.imscc_path_var = StringVar(value="No file selected")
        self.status_var = StringVar(value="Ready")

        self.create_widgets()

    def create_widgets(self):
        font_bold = ("Helvetica", 11, "bold")
        font_norm = ("Helvetica", 10)

        #Row 1 = file selector
        btn_file = Button(
            self,
            text="Select .imscc file",
            font=font_bold,
            command=self.select_file,
        )
        btn_file.grid(row=1, column=0, padx=15, pady=8, sticky="w")
    
        lbl_file = Label(
            self,
            textvariable=self.imscc_path_var,
            font=font_norm,
            fg="blue",
            anchor="w",
            width=45,
        )
        lbl_file.grid(row=1, column=1, columnspan=2, padx=10, sticky="w")

        #Status label (link to status_var)
        lbl_status = Label(
            self,
            textvariable=self.status_var,
            font=font_norm,
            fg="green",
            anchor="w",
        )
        lbl_status.grid(row=4, column=1, columnspan=2, padx=10, sticky="w")

    ##Callback
    def select_file(self):
        """Opens a file dialog for selecting the Canvas .imscc file"""
        filepath = askopenfilename(
        title="Select Canvas course export file",
        filetypes=[("Canvas Course Export", "*.imscc"), ("All Files", "*.*")],
        )
        if filepath:
            self.imscc_path_var.set(filepath)
            self.status_var.set("File selected. Next, select an output folder.")    

if __name__ == "__main__":
    app = CanvasBackupApp()
    app.mainloop()