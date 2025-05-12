import sys
import matplotlib
matplotlib.use("TkAgg")
import numpy as np
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.path as mplPath
import matplotlib.patches as mplPatches
from scipy.interpolate import interp1d
from scipy.integrate import trapezoid
import shared_params
import calculate
import time
from tkinter import messagebox
import matplotlib.pyplot as plt
from settings_window import create_settings_window

# --- Rectangle Parameters ---
rect_width = 60
rect_height = 30
rect_x = 0
rect_y = 0
rect_facecolor = "lightgray"

# --- Fixed Plane Borders ---
PLANE_WIDTH = 100
PLANE_HEIGHT = 50
PLANE_X_CENTER = 50  # Center x coordinate of the plane
PLANE_Y_CENTER = 25   # Center y coordinate of the plane. Inverted as y increases downwards

# --- Global Variables ---
h_total = 0
h_hydro = 0
r_crater = 0
r_solid = 0
surface_x, surface_y = None, None
original_surface_y = None
background_color = 'white'
total_destroyed_percentage = 0
pan_start_x, pan_start_y, pan_cid = None, None, None
ax = None
fig = None
click_time = None
shape_type = None
settings_window_open = False  # Global flag to track settings window

def get_rectangle_dimensions():
    """Gets rectangle dimensions from the user in a single dialog."""
    global rect_width, rect_height

    root = tk.Tk()
    root.withdraw()

    dialog = tk.Toplevel(root)
    dialog.title("Enter Rectangle Dimensions")

    width_label = ttk.Label(dialog, text="Width:")
    width_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    width_entry = ttk.Entry(dialog)
    width_entry.grid(row=0, column=1, padx=5, pady=5)
    width_entry.insert(0, str(rect_width))  # Use string representation

    height_label = ttk.Label(dialog, text="Height:")
    height_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
    height_entry = ttk.Entry(dialog)
    height_entry.grid(row=1, column=1, padx=5, pady=5)
    height_entry.insert(0, str(rect_height)) # Use string representation

    def ok_button_clicked():
        global rect_width, rect_height
        try:
            new_width = float(width_entry.get())
            new_height = float(height_entry.get())
            rect_width = new_width
            rect_height = new_height
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter numbers for width and height.")
            return  # This will prevent to continue if there's invalid inputs

        dialog.destroy()
        root.destroy()

    ok_button = ttk.Button(dialog, text="OK", command=ok_button_clicked)
    ok_button.grid(row=2, column=0, columnspan=2, pady=10)

    root.wait_window(dialog)


rect_edgecolor = "lightgray"


def calculate_destroyed_percentage():
    global surface_x, surface_y, original_surface_y, rect_width, rect_height

    original_y_copy = original_surface_y.copy()
    surface_y_copy = surface_y.copy()

    surface_y_copy[surface_y_copy > rect_y + rect_height] = rect_y + rect_height
    surface_y_copy[surface_y_copy < rect_y] = rect_y

    original_y_copy[original_y_copy > rect_y + rect_height] = rect_y + rect_height
    original_y_copy[original_y_copy < rect_y] = rect_y

    original_area = trapezoid(original_y_copy, surface_x)
    current_area = trapezoid(surface_y_copy, surface_x)
    destroyed_area = current_area - original_area
    total_area = rect_width * rect_height
    destroyed_percentage = (destroyed_area / total_area) * 100

    return destroyed_percentage

def update_destroyed_bar():
    global destroyed_area_bar, ax_destroyed, total_destroyed_percentage, total_destroyed_text
    total_destroyed_percentage = calculate_destroyed_percentage()

    # Clear the previous bar
    for bar in ax_destroyed.patches:
        bar.remove()

    destroyed_area_bar = ax_destroyed.barh(0, total_destroyed_percentage, color='red', alpha=0.6)
    ax_destroyed.set_xlim(0, 100)
    total_destroyed_text.set_text(f"Total Destroyed: {total_destroyed_percentage:.4f}%")
    fig.canvas.draw_idle()

def calculate_crater_depth(center_x):
    global h_total, h_hydro, r_crater, r_solid
    num_points = 3000
    x = np.linspace(-r_crater, r_crater, num_points)
    r = np.abs(x)
    depth = np.zeros_like(r)
    central_zone = r <= r_solid
    depth[central_zone] = h_total - (h_total - h_hydro) * (r[central_zone] ** 2 / r_solid ** 2)
    outer_zone = (r > r_solid) & (r <= r_crater)
    depth[outer_zone] = h_hydro * (1 - (r[outer_zone] ** 2 / r_crater ** 2))
    return x, depth

def create_crater_at(x_coord):
    global surface_x, surface_y, h_total, h_hydro, r_crater, r_solid

    dx, depth = calculate_crater_depth(x_coord)
    crater_x = x_coord + dx
    depth_interp = interp1d(crater_x, depth, bounds_error=False, fill_value=0)
    depth_values = depth_interp(surface_x)
    surface_y += depth_values

    for patch in ax.patches:
        if not isinstance(patch, mplPatches.Rectangle):
            patch.remove()

    mask_offset = 0.1
    polygon_x = np.concatenate([[rect_x - mask_offset], surface_x, [rect_x + rect_width + mask_offset]])
    polygon_y = np.concatenate([[rect_y - mask_offset], surface_y, [rect_y - mask_offset]])
    path = mplPath.Path(np.column_stack([polygon_x, polygon_y]))
    patch = mplPatches.PathPatch(path, facecolor=background_color, lw=0, transform=ax.transData, zorder=6)
    ax.add_patch(patch)

    update_destroyed_bar()
    fig.canvas.draw_idle()

def onrelease(event):
    global click_time
    if event.button == 1 and click_time is not None and (time.time() - click_time) < 0.2:
        create_crater_at(event.xdata)

def onclick(event):
    global click_time
    if event.button == 1:
        click_time = time.time()
        calculated_values = calculate_values()
        update_globals(calculated_values)

def calculate_values():
    v0 = shared_params.shared_settings["Скорость тела (v), м/с:"]
    rho_t = shared_params.shared_settings["Плотность мишени (ρₜ), кг/м³:"]
    tau_0 = shared_params.shared_settings["Прочность мишени (τ₀), Па:"]
    c = shared_params.shared_settings["Скорость звука (c), м/с:"]
    L = shared_params.shared_settings["Диаметр тела (L), м:"]
    rho_p = shared_params.shared_settings["Плотность тела (ρₚ), кг/м³:"]
    k_pr = shared_params.shared_settings["Коэффициент проницаемости (kₚᵣ):"]
    alpha = shared_params.shared_settings["Коэффициент потери массы (α):"]
    v_crit = shared_params.shared_settings["Критическая скорость (Vₖᵣ), м/с:"]
    N = shared_params.shared_settings["Длина цилиндра (N), м:"]
    shape = shared_params.shared_settings.get("Форма тела", "Цилиндр")
    return calculate.calculate_penetration(N, L, rho_p, v0, rho_t, tau_0, c, alpha, k_pr, v_crit, shape)

def update_globals(values):
    global h_total, h_hydro, r_crater, r_solid
    h_total = values['h_total']
    h_hydro = values['h_hydro_2']
    r_crater = values['d_crater_2'] / 2
    r_solid = values['r_solid']

def reset_rectangle():
    global surface_x, surface_y, original_surface_y, ax, fig, total_destroyed_percentage, rect_width, rect_height, rect_x, rect_y

    ax.clear()
    ax.set_aspect('equal')
    ax.set_xlabel("width, meters")
    ax.set_ylabel("depth, meters")
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')

    # Set fixed plane limits based on the PLANE_CENTER values
    ax.set_xlim(PLANE_X_CENTER - PLANE_WIDTH/2, PLANE_X_CENTER + PLANE_WIDTH/2)
    ax.set_ylim(PLANE_Y_CENTER + PLANE_HEIGHT/2, PLANE_Y_CENTER - PLANE_HEIGHT/2)

    ax.tick_params(axis='y', direction='in')
    fig.patch.set_facecolor(background_color)
    ax.set_facecolor(background_color)

    # Recalculate surface data based on new rectangle dimensions
    surface_x = np.linspace(rect_x, rect_x + rect_width, 3000)
    surface_y = np.full_like(surface_x, rect_y, dtype=float)
    original_surface_y = surface_y.copy()

    # Create and add the rectangle patch
    rectangle = plt.Rectangle((rect_x, rect_y), rect_width, rect_height,
                              facecolor=rect_facecolor, edgecolor=rect_edgecolor, zorder=5)
    ax.add_patch(rectangle)

    # Create and add the outline
    outline = plt.Rectangle((rect_x, rect_y), rect_width, rect_height,
                            facecolor='none', edgecolor='black', linewidth=1.5, linestyle='--', zorder=10)
    ax.add_patch(outline)

    mask_offset = 0.1
    polygon_x = np.concatenate([[rect_x - mask_offset], surface_x, [rect_x + rect_width + mask_offset]])
    polygon_y = np.concatenate([[rect_y - mask_offset], surface_y, [rect_y - mask_offset]])
    path = mplPath.Path(np.column_stack([polygon_x, polygon_y]))
    patch = mplPatches.PathPatch(path, facecolor=background_color, lw=0, transform=ax.transData, zorder=6)
    ax.add_patch(patch)

    # Reset the destroyed percentage
    total_destroyed_percentage = 0

    # Update the destroyed bar
    update_destroyed_bar()

    fig.canvas.draw_idle()

def zoom(event):
    cur_xlim = ax.get_xlim()
    cur_ylim = ax.get_ylim()
    xdata = event.xdata
    ydata = event.ydata
    scale_factor = 1/1.2 if event.button == 'up' else 1.2 if event.button == 'down' else 1
    new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
    new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
    relx = (xdata - cur_xlim[0]) / (cur_xlim[1] - cur_xlim[0])
    rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])
    ax.set_xlim([xdata - new_width * relx, xdata + new_width * (1 - relx)])
    ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
    fig.canvas.draw_idle()

def pan(event):
    global pan_start_x, pan_start_y, pan_cid
    if event.button == 1:
        pan_start_x = event.xdata
        pan_start_y = event.ydata
        pan_cid = fig.canvas.mpl_connect('motion_notify_event', do_pan)

def do_pan(event):
    global pan_start_x, pan_start_y
    if pan_start_x is None or pan_start_y is None:
        return
    dx = event.xdata - pan_start_x
    dy = event.ydata - pan_start_y
    cur_xlim = ax.get_xlim()
    cur_ylim = ax.get_ylim()
    ax.set_xlim([cur_xlim[0] - dx, cur_xlim[1] - dx])
    ax.set_ylim([cur_ylim[0] - dy, cur_ylim[1] - dy])
    fig.canvas.draw_idle()

def release_pan(event):
    global pan_start_x, pan_start_y, pan_cid
    if pan_cid is not None:
        fig.canvas.mpl_disconnect(pan_cid)
        pan_cid = None
    pan_start_x = None
    pan_start_y = None

def open_settings():
    global settings_window_open
    if not settings_window_open:
        settings_window_open = True
        win = create_settings_window(root)

        def on_close():
            global settings_window_open
            settings_window_open = False  # Reset the flag when the window is closed
            update_globals(calculate_values())  # Recalculate everything after changes
            reset_rectangle()


        win.protocol("WM_DELETE_WINDOW", on_close)
    else:
        messagebox.showinfo("Info", "Settings window is already open.")

# --- Main Tkinter Window ---
get_rectangle_dimensions()

root = tk.Tk()
root.title("Crater Simulation")

# --- PanedWindow ---
paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
paned_window.pack(fill=tk.BOTH, expand=True)

# --- Parameter Frame (Left Side) ---
parameter_frame = ttk.Frame(paned_window, padding=10)
paned_window.add(parameter_frame)

# --- Settings Button ---
settings_button = ttk.Button(parameter_frame, text="Settings", command=open_settings)
settings_button.grid(row=1, column=0, columnspan=2, pady=10)

reset_button = ttk.Button(parameter_frame, text="Reset Surface", command=reset_rectangle)
reset_button.grid(row=2, column=0, columnspan=2, pady=10)

# --- Matplotlib Setup ---
fig, ax = plt.subplots()

surface_x = np.linspace(rect_x, rect_x + rect_width, 3000)
surface_y = np.full_like(surface_x, rect_y, dtype=float)
original_surface_y = surface_y.copy()

ax.set_aspect('equal')
ax.set_xlabel("width, meters")
ax.set_ylabel("depth, meters")
ax.xaxis.tick_top()
ax.xaxis.set_label_position('top')

# Set fixed plane limits based on the PLANE_CENTER values
ax.set_xlim(PLANE_X_CENTER - PLANE_WIDTH / 2, PLANE_X_CENTER + PLANE_WIDTH / 2)
ax.set_ylim(PLANE_Y_CENTER + PLANE_HEIGHT / 2, PLANE_Y_CENTER - PLANE_HEIGHT / 2)  # Inverted

ax.tick_params(axis='y', direction='in')
fig.patch.set_facecolor(background_color)
ax.set_facecolor(background_color)

rectangle = plt.Rectangle((rect_x, rect_y), rect_width, rect_height,
                          facecolor=rect_facecolor, edgecolor=rect_edgecolor, zorder=5)
ax.add_patch(rectangle)

outline = plt.Rectangle((rect_x, rect_y), rect_width, rect_height,
                        facecolor='none', edgecolor='black', linewidth=1.5, linestyle='--', zorder=10)
ax.add_patch(outline)

ax_destroyed = fig.add_axes([0.1, 0.1, 0.8, 0.05])
ax_destroyed.set_xlim(0, 100)
ax_destroyed.set_ylim(-1, 1)
ax_destroyed.tick_params(axis='y', which='both', left=False, right=False, labelleft=False)
ax_destroyed.set_xlabel("Destroyed Area (%)")
destroyed_area_bar = ax_destroyed.barh(0, 0, color='red', alpha=0.6)
total_destroyed_text = fig.text(0.1, 0.12, f"Total Destroyed: {0:.4f}%")

canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
paned_window.add(canvas_widget)

# --- Event Binding ---
fig.canvas.mpl_connect('button_press_event', onclick)
fig.canvas.mpl_connect('button_release_event', onrelease)
fig.canvas.mpl_connect('scroll_event', zoom)
fig.canvas.mpl_connect('button_press_event', pan)
fig.canvas.mpl_connect('button_release_event', release_pan)

# --- Mainloop ---
def on_closing():
    plt.close(fig)
    root.destroy()
    sys.exit(0)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()