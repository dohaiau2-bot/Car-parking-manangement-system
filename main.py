import tkinter as tk
from views.main_windows import ParkingGUI

def entry_point():
    root = tk.Tk()
    app = ParkingGUI(root)
    root.mainloop()

if __name__ == "__main__":
    entry_point()