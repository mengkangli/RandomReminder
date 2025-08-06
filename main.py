# main.py

import tkinter as tk
from src.reminder import ReminderApp

if __name__ == "__main__":
    root = tk.Tk()
    app = ReminderApp(root)
    root.mainloop()