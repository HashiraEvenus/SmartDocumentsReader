from tkinterdnd2 import TkinterDnD
from project_gui import DocxReaderGUI

def run_application():
    root = TkinterDnD.Tk()
    app = DocxReaderGUI(root)
    root.geometry("800x600")  # Set initial window size
    root.mainloop()

if __name__ == "__main__":
    run_application()