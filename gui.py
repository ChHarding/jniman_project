from tkinter import *

class CanvasBackupApp(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("Canvas Backup Tool")
        self.geometry("620x300")

if __name__ == "__main__":
    app = CanvasBackupApp()
    app.mainloop()