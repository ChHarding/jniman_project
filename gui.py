import os
from pathlib import Path
import subprocess
import sys
from tkinter import *
from tkinter import messagebox, ttk
from main import run_backup_process

class FileExplorer(ttk.Frame):
    """Embedded from example treeview.py to add file explorer and replace buttons in the CanvasBackupApp class"""
    def __init__(self, parent, start_path=None, **kwargs):
        super().__init__(parent, **kwargs)

        # Maps Treeview item IDs to filesystem paths.
        self.paths = {}

        self.tree = ttk.Treeview(
            self,
            columns=("type", "size"),
            show="tree headings"
        )

        self.tree.heading("#0", text="Name")
        self.tree.heading("type", text="Type")
        self.tree.heading("size", text="Size")

        self.tree.column("#0", width=300)
        self.tree.column("type", width=100)
        self.tree.column("size", width=100, anchor="e")

        scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewOpen>>", self._open_folder)
        self.tree.bind("<Double-1>", self._double_click)

        # Use the current working directory unless another path is supplied.
        start_path = Path(start_path or Path.cwd()).resolve()

        root_id = self._insert_path("", start_path)
        self.tree.item(root_id, open=True)
        self._load_children(root_id, start_path)

    def _insert_path(self, parent, path):
        if path.is_dir():
            file_type = "Folder"
            size = ""
        else:
            file_type = path.suffix[1:].upper() or "File"

            try:
                size = self._format_size(path.stat().st_size)
            except OSError:
                size = ""

        item_id = self.tree.insert(
            parent,
            "end",
            text=path.name or str(path),
            values=(file_type, size)
        )

        self.paths[item_id] = path

        # Add a placeholder so folders initially display an expand arrow.
        if path.is_dir():
            self.tree.insert(item_id, "end", text="Loading...")

        return item_id

    def _load_children(self, item_id, folder):
        # Remove any existing children, including the placeholder.
        self.tree.delete(*self.tree.get_children(item_id))

        try:
            children = sorted(
                folder.iterdir(),
                key=lambda path: (not path.is_dir(), path.name.lower())
            )
        except (PermissionError, OSError):
            return

        for path in children:
            self._insert_path(item_id, path)

    def _open_folder(self, event=None):
        item_id = self.tree.focus()
        path = self.paths.get(item_id)

        if path and path.is_dir():
            self._load_children(item_id, path)

    def _double_click(self, event=None):
        # Use the row under the cursor, not the focused row, so double-clicking
        # a header or empty space doesn't open the previously selected file.
        item_id = self.tree.identify_row(event.y) if event else self.tree.focus()
        path = self.paths.get(item_id)

        if path and path.is_file():
            self._open_file(path)

    @staticmethod
    def _open_file(path):
        # Launch the file with the OS's default application for its type.
        try:
            if sys.platform.startswith("win"):
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.run(["open", str(path)], check=True)
            else:
                subprocess.run(["xdg-open", str(path)], check=True)
        except (OSError, subprocess.SubprocessError) as error:
            messagebox.showerror("Cannot open file", f"{path}\n\n{error}")

    @staticmethod
    def _format_size(size):
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024

        return f"{size:.1f} PB"

class CanvasBackupApp(Tk):
    """Tkinter GUI app class"""
    def __init__(self):
        Tk.__init__(self)
        self.title("Canvas Backup Tool")
        self.geometry("700x550") #Bigger for treeview space
        self.resizable(True, True)

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
        title_label.grid(row=0, column=0, columnspan=2, pady=(15, 15))

        #Row 1 = added file explorer to the grid
        self.explorer = FileExplorer(self, start_path=Path.cwd())
        self.explorer.grid(
            row=1, column=0, columnspan=2, padx=15, pady=10, sticky="nsew"
        )
        #let treeview row stretch when window resizes
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        #attach selection
        self.explorer.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        #Row 2 = file selector
        lbl_file_title = Label(self, text="Selected File:", font=font_bold)
        lbl_file_title.grid(row=2, column=0, padx=15, sticky="w")
    
        lbl_file = Label(
            self,
            textvariable=self.imscc_path_var,
            font=font_norm,
            fg="blue",
        )
        lbl_file.grid(row=2, column=1, padx=10, sticky="w")

        #Row 3= Destination folder selector
        lbl_dir_title = Label(self, text="Output Folder:", font=font_bold)
        lbl_dir_title.grid(row=3, column=0, padx=15, sticky="w")

        lbl_dir = Label(
            self,
            textvariable=self.output_dir_var,
            font=font_norm,
            fg="blue",
        )
        lbl_dir.grid(row=3, column=1, padx=10, sticky="w")

        #Row 4 = Run backup button
        btn_run = Button(
            self,
            text="Run Backup",
            font=("Helvetica", 12, "bold"),
            padx=15,
            pady=5,
            command=self.run_backup,
        )
        btn_run.grid(row=4, column=0, columnspan=2, pady=15)

        #Row 5 = Status label (link to status_var)
        lbl_status_title = Label(self, text="Status:", font=font_bold)
        lbl_status_title.grid(row=5, column=0, padx=15, sticky="e")

        lbl_status = Label(
            self,
            textvariable=self.status_var,
            font=font_norm,
            fg="green",
        )
        lbl_status.grid(row=5, column=1, padx=10, sticky="w")

    ##Callback
    def on_tree_select(self, event):
        """Detects clicked item in treeview and routes path to input or output."""
        #find which item ID in tree was clicked
        selected_items = self.explorer.tree.selection()
        if not selected_items:
            return

        item_id = selected_items[0]
        #looks up the path object from self.explorer.paths dict
        path = self.explorer.paths.get(item_id)

        if not path:
            return

        #Check 1: if user clicks a folder, update output_dir_var
        if path.is_dir():
            self.output_dir_var.set(str(path))
            self.status_var.set("Folder selected. Next, select an .imscc file")

        #check 2: if user clicks an .imscc file, update imscc_path_var
        elif path.is_file() and path.suffix.lower() == ".imscc":
            self.imscc_path_var.set(str(path))
            self.status_var.set("File select. Run backup.")

        #Check 3: if user clicks any other file time, notify in status bar
        elif path.is_file():
            self.status_var.set(
                f"Note: '{path.name}' is not an .imscc file. Select a .imscc file or a"
                " destination folder."
            )

    def run_backup(self):
        pass       


if __name__ == "__main__":
    app = CanvasBackupApp()
    app.mainloop()