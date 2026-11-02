import os
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askdirectory, askopenfilename
from main import run_backup_process

class CanvasBackupApp(Tk):
    """Tkinter GUI app class"""
    def __init__(self):
        Tk.__init__(self)
        self.title("Canvas Backup Tool")
        self.geometry("620x300")

        #Tkinter state variables
        self.imscc_path_var = StringVar(value="No file selected")
        self.output_dir_var = StringVar(value="No folder selected")
        self.status_var = StringVar(value="Ready")

        self.create_widgets()

    def create_widgets(self):
        """Sets up window layout using grid manager"""
        font_bold = ("Helvetica", 11, "bold")
        font_norm = ("Helvetica", 10)

        #title for app
        title_label = Label(
            self, text="Canvas Backup Tool", font=("Helvetica", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(15, 15))

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

        #Row 2= Destination folder selector
        btn_dir = Button(
        self, text="Select output folder", font=font_bold, command=self.select_dir
        )
        btn_dir.grid(row=2, column=0, padx=15, pady=10, sticky="w")

        lbl_dir = Label(
            self,
            textvariable=self.output_dir_var,
            font=font_norm,
            fg="blue",
            anchor="w",
            width=45,
        )
        lbl_dir.grid(row=2, column=1, padx=10, sticky="w")

        #Row 3 = Run backup button
        btn_run = Button(
            self,
            text="Run Backup",
            font=("Helvetica", 12, "bold"),
            padx=15,
            pady=5,
            command=self.run_backup,
        )
        btn_run.grid(row=3, column=0, columnspan=3, pady=20)

        #Row 4 = Status label (link to status_var)
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

    def select_dir(self):
        """Opens a folder dialog for selecting destination directory"""
        dirpath = askdirectory(title="Select destination folder")
        if dirpath:
            self.output_dir_var.set(dirpath)
            self.status_var.set("Destination selected! Ready for backup.")

    def run_backup(self):
        """Validates inputs and invokes run_backup_process funct from main.py"""
        imscc_file = self.imscc_path_var.get()
        output_folder =  self.output_dir_var.get()

        #safety checks
        if not os.path.exists(imscc_file) or imscc_file == "No file selected":
            messagebox.showerror(
                "Input Error", "Please select a valid .imscc course file."
            )
            return

        if not output_folder or output_folder == "No folder selected":
            messagebox.showerror(
            "Input Error", "Please select an output destination folder."
            )
            return
        
        #update status and force visual refresh
        self.status_var.set("Processing course backup... Please wait.")
        self.update()

        try:
            #invoke backend funct from main.py
            results = run_backup_process(imscc_file, output_folder)

            #update status label
            self.status_var.set(
                f"Complete! Extracted {results['modules_count']} modules."
            )

            #Display completion popup box
            messagebox.showinfo(
                "Backup complete",
                f"Canvas backup finished successfully!\n\n"
                f"Extracted {results['modules_count']} modules.\n"
                f"Copied {results['files_copied']} files.\n"
                f"Summary log: {results['report_file']}",    
            )

        except Exception as e:
            self.status_var.set("Error occured during extraction.")
            messagebox.showerror("Extraction error", f"An error occured:\n{str(e)}")


if __name__ == "__main__":
    app = CanvasBackupApp()
    app.mainloop()