import tkinter as tk
import threading

def _open_window():
    win = tk.Tk()
    win.title("Results")
    win.geometry("300x200")

    win.mainloop()

def show_results_window():
    threading.Thread(target=_open_window, daemon=True).start()
