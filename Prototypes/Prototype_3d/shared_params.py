import json
import os

default_settings = {
    "Скорость тела (v), м/с:": 7000,
    "Плотность мишени (ρ_t), кг/м³:": 2500,
    "Прочность мишени (τ₀), Па:": 5000000,
    "Дин. прочность (Y), Па:": 45000000,
    "Стат. прочность (σ_t), Па:": 50000000,
    "Скорость звука (c), м/с:": 4000,
    "Ускорение свободного падения (g), м/с²:": 9.81,
    "Диаметр тела (L), м:": 0.29,
    "Плотность тела (ρ_p), кг/м³:": 8500,
    "Масса тела (m), кг:": 0.52 * 8500 * 0.29**3,
    "Диаметр кратера (Dt_2_2), м:": 4.712683,
    "Глубина кратера (ht_2_2), м:": 0.890781
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
        except (json.JSONDecodeError, IOError):
            pass

def save_settings():
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(shared_settings, f, indent=4, ensure_ascii=False)
    except IOError:
        pass

load_settings()