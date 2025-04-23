import json
import os

default_settings = {
    "Скорость тела (v), м/с:": 7000,
    "Плотность мишени (ρₜ), кг/м³:": 2500,
    "Прочность мишени (τ₀), Па:": 5000000,
    "Скорость звука (c), м/с:": 4000,
    "Диаметр тела (L), м:": 0.29,
    "Плотность тела (ρₚ), кг/м³:": 8500,
    "Масса тела (m), кг:": 0.52 * 8500 * 0.29**3,
    "Коэффициент проницаемости (kₚᵣ):": 0.0000007,
    "Коэффициент потери массы (α):": 0.40,
    "Критическая скорость (Vₖᵣ), м/с:": 2000,
    "Длина цилиндра (N), м:": 0.19,
    "Диаметр кратера (Dₜ), м:": 4.712683,
    "Глубина кратера (hₜ), м:": 0.890781,
    "Глубина проникновения (hₛ), м:": 1.098692,
    "Радиус поражённой зоны (rₛ), м:": 0.177588
}

SETTINGS_FILE = "settings.json"

shared_settings = default_settings.copy()

def load_settings():
    global shared_settings
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                loaded_settings = json.load(f)
                shared_settings.update({k: v for k, v in loaded_settings.items() if k in default_settings})
                for key in default_settings:
                    if key not in shared_settings:
                        shared_settings[key] = default_settings[key]
        except (json.JSONDecodeError, IOError):
            shared_settings = default_settings.copy()

def save_settings():
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(shared_settings, f, indent=4, ensure_ascii=False)
    except IOError:
        pass

load_settings()