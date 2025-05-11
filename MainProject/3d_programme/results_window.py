import tkinter as tk
from tkinter import ttk
from shared_params import shared_settings
import math
from scene_state import calculate_deformed_volume

results_window_instance = None
crater_count = 0

def calculate_crater_volume(diameter, depth):
    return math.pi * diameter**2 * depth / 8

def reset_crater_count():
    global crater_count
    crater_count = 0

def refresh_labels(frame):
    for widget in frame.winfo_children():
        widget.destroy()

    Dt = shared_settings["Диаметр кратера (Dₜ), м:"]
    ht = shared_settings["Глубина кратера (hₜ), м:"]
    v = calculate_crater_volume(Dt, ht)
    Ds = shared_settings["Радиус поражённой зоны (rₛ), м:"] * 2
    hs = shared_settings["Глубина проникновения (hₛ), м:"]
    vs = calculate_crater_volume(Ds, hs)
    v_total = calculate_deformed_volume()

    ttk.Label(frame, text="Характеристики одного кратера:", font=("TkDefaultFont", 10, "bold")).pack(anchor="w", padx=10, pady=(0, 5))
    ttk.Label(frame, text=f"Диаметр гидродинамической фазы: {Dt:.2f} м").pack(anchor="w", padx=10, pady=2)
    ttk.Label(frame, text=f"Глубина гидродинамической фазы: {ht:.2f} м").pack(anchor="w", padx=10, pady=2)
    ttk.Label(frame, text=f"Диаметр твердой фазы: {Ds:.2f} м").pack(anchor="w", padx=10, pady=2)
    ttk.Label(frame, text=f"Глубина твердой фазы: {hs:.2f} м").pack(anchor="w", padx=10, pady=2)
    ttk.Label(frame, text=f"Общая глубина проникновения: {ht + hs:.2f} м").pack(anchor="w", padx=10, pady=2)
    ttk.Label(frame, text=f"Объем гидродинамической фазы: {v:.2f} м³").pack(anchor="w", padx=10, pady=2)
    ttk.Label(frame, text=f"Объем твердой фазы: {vs:.2f} м³").pack(anchor="w", padx=10, pady=2)
    ttk.Label(frame, text=f"Суммарный объем: {v + vs:.2f} м³").pack(anchor="w", padx=10, pady=2)
    ttk.Separator(frame, orient="horizontal").pack(fill="x", padx=5, pady=10)
    ttk.Label(frame, text=f"Общий объем пораженной зоны: {v_total:.2f} м³").pack(anchor="w", padx=10, pady=2)
    ttk.Label(frame, text=f"Количество кратеров: {crater_count}").pack(anchor="w", padx=10, pady=2)

def create_results_window(root):
    global results_window_instance
    if results_window_instance is not None:
        try:
            results_window_instance.lift()
            return results_window_instance
        except tk.TclError:
            results_window_instance = None

    win = tk.Toplevel(root)
    win.title("Результаты")
    win.geometry("380x350")
    results_window_instance = win

    content_frame = ttk.Frame(win)
    content_frame.pack(fill="both", expand=False, padx=10, pady=10)

    refresh_labels(content_frame)

    update_button = tk.Button(
        win,
        text="Update",
        command=lambda: refresh_labels(content_frame),
        bg="green",
        fg="white",
        activebackground="darkgreen",
        activeforeground="white"
    )
    update_button.pack(fill="both", expand=True, padx=15, pady=(0, 10))

    def on_close():
        global results_window_instance
        results_window_instance = None
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", on_close)
    return win

def show_results_window(root):
    global results_window_instance
    if results_window_instance is None or not results_window_instance.winfo_exists():
        results_window_instance = create_results_window(root)
    else:
        results_window_instance.lift()

def increment_crater_count():
    global crater_count
    crater_count += 1