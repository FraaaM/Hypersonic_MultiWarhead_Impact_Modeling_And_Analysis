import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.path as mplPath
import matplotlib.patches as mplPatches
from scipy.interpolate import interp1d
from scipy.integrate import trapezoid
import shared_params
import calculate
import time

# --- Rectangle Parameters ---
rect_width = 60
rect_height = 30
rect_x = 0
rect_y = 0
rect_facecolor = "lightgray"
rect_edgecolor = "lightgray"

# --- Global Variables ---
h_total = 0
h_hydro = 0
r_crater = 0
r_solid = 0
surface_x, surface_y = None, None
original_surface_y = None
background_color = 'white'
total_destroyed_percentage = 0
pan_start_x, pan_start_y, pan_cid = None, None, None  # Initialize pan_cid
ax = None  # Initialize ax
fig = None  # Initialize fig
click_time = None
shape_type = None

# --- Function to Calculate Destroyed Area Percentage ---
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

# --- Function to Update Destroyed Area Bar ---
def update_destroyed_bar():
    global destroyed_area_bar, ax_destroyed, total_destroyed_percentage, total_destroyed_text
    total_destroyed_percentage = calculate_destroyed_percentage()
    destroyed_area_bar[0].remove()
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
    global click_time, h_total, h_hydro, r_crater, r_solid, shape_type
    if event.button == 1 and click_time is not None and (time.time() - click_time) < 0.2:  #Check if less than 0.2 seconds
        create_crater_at(event.xdata)

def onclick(event):
    global click_time, h_total, h_hydro, r_crater, r_solid, shape_type
    if event.button == 1:
        click_time = time.time()
        calculated_values = calculate_values()
        h_total = calculated_values['h_total']
        h_hydro = calculated_values['h_hydro_2']
        r_crater = calculated_values['d_crater_2'] / 2
        r_solid = calculated_values['r_solid']

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

    calculated_data = calculate.calculate_penetration(
        N=N,
        L=L,
        rho_p=rho_p,
        v0=v0,
        rho_t=rho_t,
        tau_0=tau_0,
        c=c,
        alpha=alpha,
        k_pr=k_pr,
        v_crit=v_crit,
        shape=shape_type.get(),  # Pass the selected shape
    )
    return calculated_data

def reset_rectangle():
    global surface_x, surface_y, original_surface_y, ax, fig
    surface_x = np.linspace(rect_x, rect_x + rect_width, 3000)
    surface_y = np.full_like(surface_x, rect_y, dtype=float)
    original_surface_y = surface_y.copy()

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

# --- Panning and Zooming Functions ---
def zoom(event):
    cur_xlim = ax.get_xlim()
    cur_ylim = ax.get_ylim()
    xdata = event.xdata
    ydata = event.ydata

    if event.button == 'up':
        scale_factor = 1/1.2
    elif event.button == 'down':
        scale_factor = 1.2
    else:
        scale_factor = 1

    new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
    new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
    relx = (xdata - cur_xlim[0]) / (cur_xlim[1] - cur_xlim[0])
    rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])
    ax.set_xlim([xdata - new_width * relx, xdata + new_width * (1 - relx)])
    ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
    fig.canvas.draw_idle()

def pan(event):
    global pan_start_x, pan_start_y, pan_cid
    if event.button == 1:  # Left mouse button
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

def update_values():
    global h_total, h_hydro, r_crater, r_solid
    calculated_values = calculate_values()
    h_total = calculated_values['h_total']
    h_hydro = calculated_values['h_hydro_2']
    r_crater = calculated_values['d_crater_2'] / 2
    r_solid = calculated_values['r_solid']

# --- Main Tkinter Window ---
root = tk.Tk()
root.title("Crater Simulation")

# move after root
shape_type = tk.StringVar(value="Цилиндр")

# --- PanedWindow for Left/Right Layout ---
paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
paned_window.pack(fill=tk.BOTH, expand=True)

# --- Parameter Frame (Left Side) ---
parameter_frame = ttk.Frame(paned_window, padding=10)
paned_window.add(parameter_frame)

# --- Shape Selection ---
shape_label = ttk.Label(parameter_frame, text="Форма тела:")
shape_label.grid(row=0, column=0, sticky=tk.W)
shape_combobox = ttk.Combobox(
    parameter_frame, textvariable=shape_type, values=["Сфера", "Цилиндр"], state="readonly"
)
shape_combobox.grid(row=0, column=1, sticky=tk.E)

# --- Entries for Parameters ---
entries = {}
calculated_entry_values = {}  # Store the calculated values

# Parameters to exclude from the input fields, because we calculate them
excluded_params = [
    "Полная глубина кратера (htotal), м:",
    "Глубина гидродинамической зоны (hhydro), м:",
    "Радиус кратера (rcrater), м:",
    "Радиус зоны разрушения (rsolid), м:",
]

shared_params_keys = list(shared_params.shared_settings.keys())
shared_params_keys = shared_params_keys[:-4]

for i, key in enumerate(shared_params_keys, start=1):  # start at row 1
    label = ttk.Label(parameter_frame, text=key)
    label.grid(row=i, column=0, sticky=tk.W)
    entry = ttk.Entry(parameter_frame)
    entry.insert(0, str(shared_params.shared_settings[key]))  # Set initial value from shared_params
    entry.grid(row=i, column=1, sticky=tk.E)
    entries[key] = entry

# --- Update Button ---
def update_parameters():
    global h_total, h_hydro, r_crater, r_solid  # Declare as global to modify them
    try:
        # Update shared_params with values from the entries
        for key, entry in entries.items():
            try:
                shared_params.shared_settings[key] = float(entry.get())
            except ValueError:
                shared_params.shared_settings[key] = entry.get()

        shared_params.save_settings()
        # Update global variables after parameters are updated
        calculated_values = calculate_values()
        h_total = calculated_values['h_total']
        h_hydro = calculated_values['h_hydro_2']
        r_crater = calculated_values['d_crater_2'] / 2
        r_solid = calculated_values['r_solid']

    except ValueError as e:
        tk.messagebox.showerror("Error", str(e))

update_button = ttk.Button(parameter_frame, text="Update", command=update_parameters)
update_button.grid(row=len(shared_params_keys) + 1, column=0, columnspan=2, pady=10)

# --- Reset Rectangle Button ---
reset_button = ttk.Button(parameter_frame, text="Reset Rectangle", command=reset_rectangle)
reset_button.grid(row=len(shared_params_keys) + 2, column=0, columnspan=2, pady=10)  # Place below Update button

# --- Matplotlib Figure and Canvas (Right Side) ---
fig, ax = plt.subplots()

# Initialize surface (flat before craters)
surface_x = np.linspace(rect_x, rect_x + rect_width, 3000)
surface_y = np.full_like(surface_x, rect_y, dtype=float)
original_surface_y = surface_y.copy()

# Set axis labels
ax.set_xlabel("width, meters")
ax.set_ylabel("depth, meters")

# Put the x axis on top
ax.xaxis.tick_top()
ax.xaxis.set_label_position('top')

# Set the Y-axis limits and direction
ax.set_ylim(rect_y + rect_height, rect_y)  # Invert the axis on creation

# Set the Y-axis ticks to face inwards
ax.tick_params(axis='y', direction='in')

# Make everything above the plot white
fig.patch.set_facecolor(background_color)
ax.set_facecolor(background_color)

ax.set_xlim(rect_x, rect_x + rect_width)
ax.set_ylim(rect_y + rect_height, rect_y)  # Adjust limits

# Draw the Initial Rectangle
rectangle = plt.Rectangle((rect_x, rect_y), rect_width, rect_height,
                         facecolor=rect_facecolor, edgecolor=rect_edgecolor, zorder=5)
ax.add_patch(rectangle)

# --- Create destroyed area bar ---
ax_destroyed = fig.add_axes([0.1, 0.1, 0.8, 0.05])
ax_destroyed.set_xlim(0, 100)
ax_destroyed.set_ylim(-1, 1)
ax_destroyed.tick_params(axis='y', which='both', left=False, right=False, labelleft=False)
ax_destroyed.set_xlabel("Destroyed Area (%)")
destroyed_area_bar = ax_destroyed.barh(0, 0, color='red', alpha=0.6)

# Add text label under the bar
total_destroyed_text = fig.text(0.1, 0.12, f"Total Destroyed: {0:.4f}%")

# --- Matplotlib Canvas Embedding ---
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
paned_window.add(canvas_widget)

# --- Event Handling ---
fig.canvas.mpl_connect('button_press_event', onclick)
fig.canvas.mpl_connect('button_release_event', onrelease)
fig.canvas.mpl_connect('scroll_event', zoom)
fig.canvas.mpl_connect('button_press_event', pan)  # Bind pan start
fig.canvas.mpl_connect('button_release_event', release_pan)  # Bind pan release

# --- Mainloop ---
root.mainloop()