import tkinter as tk
import math
from shared_params import shared_settings, save_settings
from calculate import calculate_penetration

entries = {}
sliders = {}

def create_settings_window(parent):
    win = tk.Toplevel(parent)
    win.title("Настройки параметров")
    win.geometry("400x600")
    win.resizable(True, True)

    def on_closing():
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", on_closing)

    frame_container = tk.Frame(win)
    frame_container.pack(fill="x", padx=15, pady=10)

    frame = tk.LabelFrame(frame_container, bd=2, relief="groove", labelanchor="n")
    frame.pack(fill="x")

    shape_frame = tk.Frame(frame)
    shape_frame.grid(row=0, column=0, sticky="w", padx=2, pady=6)

    shape_var = tk.StringVar(value="Сфера")

    def update_shape_colors_and_state():
        sphere_button.config(fg="black" if shape_var.get() == "Сфера" else "gray")
        cylinder_button.config(fg="black" if shape_var.get() == "Цилиндр" else "gray")
        update_parameter_state()
        update_from_mass()

    sphere_button = tk.Radiobutton(shape_frame, text="Сфера", variable=shape_var, value="Сфера", command=update_shape_colors_and_state)
    sphere_button.pack(side="left", padx=5)
    cylinder_button = tk.Radiobutton(shape_frame, text="Цилиндр", variable=shape_var, value="Цилиндр", command=update_shape_colors_and_state)
    cylinder_button.pack(side="left", padx=5)

    default_params = {
        "Скорость тела (v), м/с:": shared_settings["Скорость тела (v), м/с:"],
        "Плотность мишени (ρₜ), кг/м³:": shared_settings["Плотность мишени (ρₜ), кг/м³:"],
        "Прочность мишени (τ₀), Па:": shared_settings["Прочность мишени (τ₀), Па:"],
        "Скорость звука (c), м/с:": shared_settings["Скорость звука (c), м/с:"],
        "Коэффициент проницаемости (kₚᵣ):": shared_settings["Коэффициент проницаемости (kₚᵣ):"],
        "Коэффициент потери массы (α):": shared_settings["Коэффициент потери массы (α):"],
        "Критическая скорость (Vₖᵣ), м/с:": shared_settings["Критическая скорость (Vₖᵣ), м/с:"],
    }

    def update_parameter_state():
        is_sphere = shape_var.get() == "Сфера"
        slider = sliders["Длина цилиндра (N), м:"]["slider"]
        slider.config(state="disabled" if is_sphere else "normal", 
                     troughcolor="black" if is_sphere else "#c8c8c8")
        if is_sphere:
            update_N_from_mass()

    for i, (label_text, default_value) in enumerate(default_params.items()):
        tk.Label(frame, text=label_text, anchor="w").grid(row=i+1, column=0, sticky="w", padx=10, pady=6)
        entry = tk.Entry(frame)
        entry.insert(0, str(default_value))
        entry.grid(row=i+1, column=1, sticky="ew", padx=10, pady=6)
        entries[label_text] = entry

    slider_frame = tk.LabelFrame(frame_container, bd=2, relief="groove")
    slider_frame.pack(fill="x", pady=(10, 0))

    N_var = tk.DoubleVar(value=shared_settings["Длина цилиндра (N), м:"])
    L_var = tk.DoubleVar(value=shared_settings["Диаметр тела (L), м:"])
    rho_p_var = tk.DoubleVar(value=shared_settings["Плотность тела (ρₚ), кг/м³:"])
    m_var = tk.DoubleVar(value=shared_settings["Масса тела (m), кг:"])

    prev_values = {"L": L_var.get(), "ρₚ": rho_p_var.get(), "N": N_var.get()}

    def update_N_from_mass():
        m = m_var.get()
        rho_p = rho_p_var.get()
        L = L_var.get()
        if rho_p > 0 and L > 0:
            N = m / (math.pi * (L/2)**2 * rho_p)
            N_min = sliders["Длина цилиндра (N), м:"]["slider"].cget("from")
            N_max = sliders["Длина цилиндра (N), м:"]["slider"].cget("to")
            N = max(N_min, min(N_max, N))
            N_var.set(round(N, 6))

    def update_mass(*args):
        L = L_var.get()
        rho_p = rho_p_var.get()
        N = N_var.get()
        is_sphere = shape_var.get() == "Сфера"
        
        m = (4/3) * math.pi * (L/2)**3 * rho_p if is_sphere else math.pi * (L/2)**2 * N * rho_p
        m_min = sliders["Масса тела (m), кг:"]["slider"].cget("from")
        m_max = sliders["Масса тела (m), кг:"]["slider"].cget("to")
        
        if m < m_min or m > m_max:
            if L != prev_values["L"]:
                L_var.set(prev_values["L"])
            if rho_p != prev_values["ρₚ"]:
                rho_p_var.set(prev_values["ρₚ"])
            if N != prev_values["N"] and not is_sphere:
                N_var.set(prev_values["N"])
        else:
            m_var.set(round(m, 6))
            prev_values["L"] = L
            prev_values["ρₚ"] = rho_p
            prev_values["N"] = N
            if is_sphere:
                update_N_from_mass()

    def update_from_mass(*args):
        m = m_var.get()
        L_min = sliders["Диаметр тела (L), м:"]["slider"].cget("from")
        L_max = sliders["Диаметр тела (L), м:"]["slider"].cget("to")
        rho_min = sliders["Плотность тела (ρₚ), кг/м³:"]["slider"].cget("from")
        rho_max = sliders["Плотность тела (ρₚ), кг/м³:"]["slider"].cget("to")
        N_min = sliders["Длина цилиндра (N), м:"]["slider"].cget("from")
        N_max = sliders["Длина цилиндра (N), м:"]["slider"].cget("to")
        rho_p = rho_p_var.get()
        L = L_var.get()
        is_sphere = shape_var.get() == "Сфера"

        if is_sphere:
            L = (m / ((4/3) * math.pi * rho_p)) ** (1/3) * 2
            if L_min <= L <= L_max:
                L_var.set(round(L, 6))
            else:
                if L > L_max:
                    L = L_max
                elif L < L_min:
                    L = L_min
                L_var.set(round(L, 6))
                new_rho = m / ((4/3) * math.pi * (L/2)**3)
                if new_rho < rho_min:
                    new_rho = rho_min
                elif new_rho > rho_max:
                    new_rho = rho_max
                rho_p_var.set(round(new_rho, 6))
            update_N_from_mass()
        else:
            N = N_var.get()
            L = (m / (math.pi * rho_p * N)) ** 0.5 * 2
            if L_min <= L <= L_max:
                L_var.set(round(L, 6))
            else:
                if L > L_max:
                    L = L_max
                    if rho_p >= rho_max:
                        new_N = m / (math.pi * (L/2)**2 * rho_p)
                        if new_N <= N_max:
                            N_var.set(round(new_N, 6))
                    else:
                        new_rho = m / (math.pi * (L/2)**2 * N)
                        if new_rho <= rho_max:
                            rho_p_var.set(round(new_rho, 6))
                elif L < L_min:
                    L = L_min
                    new_rho = m / (math.pi * (L/2)**2 * N)
                    if new_rho >= rho_min:
                        rho_p_var.set(round(new_rho, 6))
                L_var.set(round(L, 6))
        update_mass()

    slider_params = [
        ("Длина цилиндра (N), м:", N_var, 0.5, 5.0, 0.01, update_mass),
        ("Диаметр тела (L), м:", L_var, 0.05, 2.0, 0.01, update_mass),
        ("Плотность тела (ρₚ), кг/м³:", rho_p_var, 2000, 15000, 100, update_mass),
        ("Масса тела (m), кг:", m_var, 10, 1000, 10, update_from_mass),
    ]

    for i, (label_text, var, min_val, max_val, resolution, callback) in enumerate(slider_params):
        tk.Label(slider_frame, text=label_text, anchor="w").grid(row=i, column=0, sticky="w", padx=10, pady=6)
        slider = tk.Scale(slider_frame, from_=min_val, to=max_val, resolution=resolution,
                         orient=tk.HORIZONTAL, variable=var, command=lambda x, c=callback: c())
        slider.grid(row=i, column=1, sticky="ew", padx=10, pady=6, columnspan=2)
        sliders[label_text] = {"slider": slider, "var": var}

    frame.columnconfigure(1, weight=1)
    slider_frame.columnconfigure(1, weight=1)
    slider_frame.columnconfigure(2, weight=1)

    apply_button = tk.Button(win, text="Apply", command=lambda: apply_values(win),
                            bg="green", fg="white", activebackground="darkgreen", activeforeground="white")
    apply_button.pack(side="bottom", fill="both", expand=True, padx=15, pady=(0, 10))

    def apply_values(win):
        updated = {k: float(e.get()) for k, e in entries.items()}
        updated.update({
            "Длина цилиндра (N), м:": N_var.get(),
            "Диаметр тела (L), м:": L_var.get(),
            "Плотность тела (ρₚ), кг/м³:": rho_p_var.get(),
            "Масса тела (m), кг:": m_var.get(),
        })
        v = updated["Скорость тела (v), м/с:"]
        rho_t = updated["Плотность мишени (ρₜ), кг/м³:"]
        tau_0 = updated["Прочность мишени (τ₀), Па:"]
        c = updated["Скорость звука (c), м/с:"]
        rho_p = updated["Плотность тела (ρₚ), кг/м³:"]
        L = updated["Диаметр тела (L), м:"]
        alpha = updated["Коэффициент потери массы (α):"]
        v_crit = updated["Критическая скорость (Vₖᵣ), м/с:"]
        k_pr = updated["Коэффициент проницаемости (kₚᵣ):"]
        shape = shape_var.get()

        if shape == "Сфера":
            N = L
        else:
            N = updated["Длина цилиндра (N), м:"]

        results = calculate_penetration(N, L, rho_p, v, rho_t, tau_0, c, alpha, k_pr, v_crit, shape)
        updated["Диаметр кратера (Dₜ), м:"] = round(results["d_crater_2"], 6)
        updated["Глубина кратера (hₜ), м:"] = round(results["h_hydro_2"], 6)
        updated["Глубина проникновения (hₛ), м:"] = round(results["h_solid"], 6)
        updated["Радиус поражённой зоны (rₛ), м:"] = round(results["r_solid"], 6)
        updated["Масса тела (m), кг:"] = round(results["m"], 6)

        shared_settings.update(updated)
        save_settings()
        print("Обновлённые параметры и результаты:", updated)

    update_shape_colors_and_state()
    return win

def update_settings_window(win):
    try:
        if win and win.winfo_exists():
            win.update()
            return win
    except tk.TclError:
        return None
    return None

def show_settings_window():
    return create_settings_window()