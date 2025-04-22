import tkinter as tk
import math
from shared_params import shared_settings, save_settings

entries = {}
sliders = {}

def crater_diameter_and_depth_2_2(E, tau_s, I, rho_t, c, rho_p, L):
    Dt = (E / tau_s)**0.255 * (I / (rho_t * c))**0.078 + 1.20 * math.sqrt(rho_p / rho_t) * L
    ht = 0.14 * (E / tau_s)**0.255 * (I / (rho_t * c))**0.078 + 0.60 * math.sqrt(rho_p / rho_t) * L
    return Dt, ht

def create_settings_window():
    win = tk.Tk()
    win.title("Настройки параметров")
    win.geometry("400x490")
    win.resizable(True, True)

    def on_closing():
        win.quit()  # Останавливаем цикл обработки событий Tkinter
        win.destroy()  # Уничтожаем окно

    win.protocol("WM_DELETE_WINDOW", on_closing)

    frame_container = tk.Frame(win)
    frame_container.pack(fill="x", padx=15, pady=10)

    frame = tk.LabelFrame(frame_container, bd=2, relief="groove", labelanchor="n")
    frame.pack(fill="x")

    default_params = {
        "Скорость тела (v), м/с:": shared_settings["Скорость тела (v), м/с:"],
        "Плотность мишени (ρ_t), кг/м³:": shared_settings["Плотность мишени (ρ_t), кг/м³:"],
        "Прочность мишени (τ₀), Па:": shared_settings["Прочность мишени (τ₀), Па:"],
        "Дин. прочность (Y), Па:": shared_settings["Дин. прочность (Y), Па:"],
        "Стат. прочность (σ_t), Па:": shared_settings["Стат. прочность (σ_t), Па:"],
        "Скорость звука (c), м/с:": shared_settings["Скорость звука (c), м/с:"],
        "Ускорение свободного падения (g), м/с²:": shared_settings["Ускорение свободного падения (g), м/с²:"]
    }

    for i, (label_text, default_value) in enumerate(default_params.items()):
        tk.Label(frame, text=label_text, anchor="w").grid(row=i, column=0, sticky="w", padx=10, pady=6)
        entry = tk.Entry(frame)
        entry.insert(0, str(default_value))
        entry.grid(row=i, column=1, sticky="ew", padx=10, pady=6)
        entries[label_text] = entry

    slider_frame = tk.LabelFrame(frame_container, bd=2, relief="groove")
    slider_frame.pack(fill="x", pady=(10, 0))

    L_var = tk.DoubleVar(value=shared_settings["Диаметр тела (L), м:"])
    rho_p_var = tk.DoubleVar(value=shared_settings["Плотность тела (ρ_p), кг/м³:"])
    m_var = tk.DoubleVar(value=shared_settings["Масса тела (m), кг:"])

    prev_values = {"L": L_var.get(), "rho_p": rho_p_var.get()}

    def update_mass(*args):
        L = L_var.get()
        rho_p = rho_p_var.get()
        m = 0.52 * rho_p * L**3

        m_min = sliders["Масса тела (m), кг:"]["slider"].cget("from")

        if m < m_min:
            if L != prev_values["L"]:
                L_var.set(prev_values["L"])
            if rho_p != prev_values["rho_p"]:
                rho_p_var.set(prev_values["rho_p"])
        else:
            m_var.set(round(m, 6))
            prev_values["L"] = L
            prev_values["rho_p"] = rho_p

    def update_from_mass(*args):
        m = m_var.get()
        L_min = sliders["Диаметр тела (L), м:"]["slider"].cget("from")
        L_max = sliders["Диаметр тела (L), м:"]["slider"].cget("to")
        rho_min = sliders["Плотность тела (ρ_p), кг/м³:"]["slider"].cget("from")
        rho_max = sliders["Плотность тела (ρ_p), кг/м³:"]["slider"].cget("to")

        rho_p = rho_p_var.get()
        L = (m / (0.52 * rho_p)) ** (1 / 3)

        if L_min <= L <= L_max:
            L_var.set(round(L, 6))
        else:
            if L > L_max:
                L = L_max
            elif L < L_min:
                L = L_min

            L_var.set(round(L, 6))
            new_rho = m / (0.52 * L**3)
            if new_rho < rho_min:
                new_rho = rho_min
            elif new_rho > rho_max:
                new_rho = rho_max
            rho_p_var.set(round(new_rho, 6))

        update_mass()

    slider_params = [
        ("Диаметр тела (L), м:", L_var, 0.01, 1, 0.01, update_mass),
        ("Плотность тела (ρ_p), кг/м³:", rho_p_var, 2000, 9000, 100, update_mass),
        ("Масса тела (m), кг:", m_var, 10, 5000, 10, update_from_mass)
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
            "Диаметр тела (L), м:": L_var.get(),
            "Плотность тела (ρ_p), кг/м³:": rho_p_var.get(),
            "Масса тела (m), кг:": m_var.get()
        })
        v = updated["Скорость тела (v), м/с:"]
        rho_t = updated["Плотность мишени (ρ_t), кг/м³:"]
        tau_s = updated["Прочность мишени (τ₀), Па:"]
        c = updated["Скорость звука (c), м/с:"]
        rho_p = updated["Плотность тела (ρ_p), кг/м³:"]
        L = updated["Диаметр тела (L), м:"]
        m = updated["Масса тела (m), кг:"]

        E = 0.5 * m * v**2
        I = m * v

        Dt_2_2, ht_2_2 = crater_diameter_and_depth_2_2(E, tau_s, I, rho_t, c, rho_p, L)

        updated["Диаметр кратера (Dt_2_2), м:"] = round(Dt_2_2, 6)
        updated["Глубина кратера (ht_2_2), м:"] = round(ht_2_2, 6)

        shared_settings.update(updated)
        save_settings()
        print("Обновлённые параметры и результаты:", updated)

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
