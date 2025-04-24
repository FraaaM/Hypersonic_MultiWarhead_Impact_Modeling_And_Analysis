import matplotlib.pyplot as plt
import numpy as np
import matplotlib.path as mplPath
import matplotlib.patches as mplPatches
from scipy.interpolate import interp1d
from scipy.integrate import trapezoid

# --- Rectangle Parameters ---
rect_width = 60
rect_height = 30
rect_x = 0
rect_y = 0
rect_facecolor = "lightgray"
rect_edgecolor = "lightgray"

# --- Indent Parameters ---
indent_depth = 2
curve_equation = "quadratic"
border_tolerance = 1

# --- Initial crater parameters ---
h_total = 10
h_hydro = 4
r_crater = 14
r_solid = 2

# --- Plane Parameters ---
x_padding = 5
y_padding = 3
mousedown_x, mousedown_y = None, None

# --- Initial View Limits ---
x_min_initial = rect_x - x_padding
x_max_initial = rect_x + rect_width + x_padding
y_min_initial = rect_y - y_padding
y_max_initial = rect_y + rect_height + y_padding

# --- Global Variables ---
panning = False
last_x, last_y = None, None
surface_x, surface_y = None, None
original_surface_y = None
total_destroyed_percentage = 0  # Track total destroyed percentage

# --- Background Color ---
background_color = 'white'

# --- Function to Calculate Destroyed Area Percentage ---
def calculate_destroyed_percentage():
    global surface_x, surface_y, original_surface_y, rect_width, rect_height

    # Make copies to avoid modifying the originals
    original_y_copy = original_surface_y.copy()
    surface_y_copy = surface_y.copy()

    # Clip surface to within rectangle bounds (y values) to avoid over-counting
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
    global destroyed_area_bar, calculate_destroyed_percentage, ax_destroyed, total_destroyed_percentage, total_destroyed_text
    total_destroyed_percentage = calculate_destroyed_percentage()
    destroyed_area_bar[0].remove()
    destroyed_area_bar = ax_destroyed.barh(0, total_destroyed_percentage, color='red', alpha=0.6)
    ax_destroyed.set_xlim(0, 100)

    total_destroyed_text.set_text(f"Total Destroyed: {total_destroyed_percentage:.4f}%")

    fig.canvas.draw_idle()

def calculate_crater_depth(center_x, num_points=3000):
    x = np.linspace(-r_crater, r_crater, num_points)
    r = np.abs(x)

    depth = np.zeros_like(r)

    central_zone = r <= r_solid
    depth[central_zone] = h_total - (h_total - h_hydro) * (r[central_zone] ** 2 / r_solid ** 2)

    outer_zone = (r > r_solid) & (r <= r_crater)
    depth[outer_zone] = h_hydro * (1 - (r[outer_zone] ** 2 / r_crater ** 2))

    return x, depth

def start_pan(event):
    global panning, last_x, last_y, mousedown_x, mousedown_y
    if event.button == 1:
        panning = True
        last_x, last_y = event.xdata, event.ydata
        mousedown_x, mousedown_y = event.xdata, event.ydata
        fig.canvas.grab_mouse(ax=ax)

def end_pan(event):
    global panning, mousedown_x, mousedown_y
    if event.button == 1 and panning:
        panning = False
        fig.canvas.release_mouse(ax=ax)

        if mousedown_x is not None and mousedown_y is not None and event.xdata is not None and event.ydata is not None:
            dx = abs(event.xdata - mousedown_x)
            dy = abs(event.ydata - mousedown_y)
            if dx < 0.5 and dy < 0.5:  # Treat it as a click
                create_crater_at(event.xdata)

        mousedown_x, mousedown_y = None, None

def create_crater_at(x):
    global surface_x, surface_y

    dx, depth = calculate_crater_depth(x, num_points=1000)
    crater_x = x + dx
    depth_interp = interp1d(crater_x, depth, bounds_error=False, fill_value=0)
    depth_values = depth_interp(surface_x)

    surface_y += depth_values  # Add depth because y increases downward

    # Clear old crater patches (not the rectangle)
    for patch in ax.patches:
        if not isinstance(patch, mplPatches.Rectangle):
            patch.remove()

    # Draw updated crater
    mask_offset = 0.1
    polygon_x = np.concatenate([[rect_x - mask_offset], surface_x, [rect_x + rect_width + mask_offset]])
    polygon_y = np.concatenate([[rect_y - mask_offset], surface_y, [rect_y - mask_offset]])
    path = mplPath.Path(np.column_stack([polygon_x, polygon_y]))
    patch = mplPatches.PathPatch(path, facecolor=background_color, lw=0, transform=ax.transData, zorder=6)
    ax.add_patch(patch)

    update_destroyed_bar()
    fig.canvas.draw_idle()

def do_pan(event):
    global ax, panning, last_x, last_y
    if not panning:
        return
    x, y = event.xdata, event.ydata
    dx = x - last_x
    dy = y - last_y
    cur_xlim = ax.get_xlim()
    cur_ylim = ax.get_ylim()
    new_xlim = [cur_xlim[0] - dx, cur_xlim[1] - dx]
    new_ylim = [cur_ylim[0] - dy, cur_ylim[1] - dy]
    ax.set_xlim(new_xlim)
    ax.set_ylim(new_ylim)
    last_x, last_y = x, y
    fig.canvas.draw_idle()

def zoom(event):
    cur_xlim = ax.get_xlim()
    cur_ylim = ax.get_ylim()
    xdata = event.xdata  # get event x location
    ydata = event.ydata  # get event y location
    if event.button == 'up':  # Scroll up => Zoom in
        scale_factor = 1 / 1.2
    elif event.button == 'down':  # Scroll down => Zoom out
        scale_factor = 1.2
    else:
        # deal with something that should never happen
        scale_factor = 1
        print(event.button)
    new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
    new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor  # Correct height calculation
    relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
    rely = (ydata - cur_ylim[0]) / (cur_ylim[1] - cur_ylim[0])  # Correct relative position
    ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * (relx)])
    ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * (rely)])
    fig.canvas.draw_idle()

# --- Create Figure and Axes ---
fig, ax = plt.subplots()

# Set the window title
fig.canvas.manager.set_window_title("2D Visualisation")

# Set axis labels
ax.set_xlabel("width, meters")  # x axis label
ax.set_ylabel("depth, meters") # y axis label changed to "depth"


# Put the x axis on top
ax.xaxis.tick_top()
ax.xaxis.set_label_position('top')

# Set the Y-axis limits and direction - now positive downward
ax.set_ylim(rect_y, rect_y + rect_height + y_padding)  # Starts at 0 at top

# Set the Y-axis ticks to face inwards
ax.tick_params(axis='y', direction='in')

# Initialize surface (flat before craters) - now starts at rect_y (0) at top
surface_x = np.linspace(rect_x, rect_x + rect_width, 3000)
surface_y = np.full_like(surface_x, rect_y, dtype=float)  # Starts at 0 (top)
original_surface_y = surface_y.copy()

# Make everything above the plot white
fig.patch.set_facecolor(background_color)
ax.set_facecolor(background_color)

# Adjust subplots
fig.subplots_adjust(left=0.1, bottom=0.30)

x_min = rect_x - x_padding
x_max = rect_x + rect_width + x_padding
y_min = rect_y - y_padding
y_max = rect_y + rect_height + y_padding

ax.set_xlim(x_min, x_max)
ax.set_ylim(y_max, y_min)

# --- Draw the Initial Rectangle ---
# The rectangle now starts at (0,0) at top-left
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
total_destroyed_text = fig.text(0.1, 0.12, f"Total Destroyed: {total_destroyed_percentage:.4f}%")

# Connect panning events
fig.canvas.mpl_connect('button_press_event', start_pan)
fig.canvas.mpl_connect('button_release_event', end_pan)
fig.canvas.mpl_connect('motion_notify_event', do_pan)

# Add zoom functionality
fig.canvas.mpl_connect('scroll_event', zoom)

# --- Display the Plot ---
plt.show()