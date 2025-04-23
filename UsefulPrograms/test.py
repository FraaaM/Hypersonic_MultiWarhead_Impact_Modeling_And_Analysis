import math

L = D = 0.7              # Диаметр тела, м (около 1 м — для гиперзвукового блока)
rho_p = 8000             # Плотность тела, кг/м³ (типичный металл, например, титан/сталь)
v = 5000                 # Скорость тела, м/с (7 км/с — гиперзвуковая скорость при входе в атмосферу)
rho_t = 1600             # Плотность мишени, кг/м³ (например, плотный бетон или скальная порода)
tau_0 = 5e6              # Прочность мишени, Па (типичное значение для прочных материалов)
Y = 45e6                 # Динамическая прочность мишени, Па (среднее значение)
sigma_t = 5e7            # Статическая прочность мишени, Па (можно оставить как есть)
c = 4000                 # Скорость звука в мишени, м/с (приблизительно для твёрдого бетона или породы)
g = 9.81                 # Ускорение свободного падения, м/с²

m = 0.52 * rho_p * L**3                                     # Вычисляем массу тела
E = 0.5 * m * v**2                                          # Вычисляем энергию тела
tau_s = tau_0 + 0.5 * L * math.sqrt(rho_p * rho_t)          # Вычисляем эффективную прочность мишени(на глубине)
I = m * v                                                   # Вычисляем импульс тела

def crater_diameter_3_1(rho_p, rho_t, g, E):
    return 1.63e-2 * (rho_p)**(1/6) * (rho_t)**(-1/2) * (g)**(-0.165) * (E)**(0.37)

def crater_diameter_3_2(rho_p, rho_t, g, E):
    return 2.94e-1 * (rho_p)**(1/6) * (rho_t)**(-1/2) * (g)**(-0.165) * (E)**(0.28)

def crater_diameter_3_3(E, rho_p, rho_t, L):
    return 0.0133 * (E)**(0.294) + 1.51 * math.sqrt(rho_p / rho_t) * L

def crater_diameter_3_4(rho_p, rho_t, g, E, L):
    return 1.8 * (rho_p)**(0.11) * (rho_t)**(-1/3) * (g)**(-0.22) * (E)**(0.22) * (L)**(0.13)

def crater_diameter_and_depth_2_2(E, tau_s, I, rho_t, c, rho_p, L):
    Dt = (E / tau_s)**0.255 * (I / (rho_t * c))**0.078 + 1.20 * math.sqrt(rho_p / rho_t) * L
    ht = 0.14 * (E / tau_s)**0.255 * (I / (rho_t * c))**0.078 + 0.60 * math.sqrt(rho_p / rho_t) * L
    return Dt, ht

def crater_diameter_and_depth_2_3(rho_p, rho_t, g, v, L, k=1.0):

    RG = math.sqrt(rho_p * rho_t) * g * L / tau_0
    Fr = v**2 / (g * L)
    M = v / c

    common_term = ((math.sqrt(rho_p / rho_t) * (k + 1 / (math.sqrt(rho_p / rho_t) * RG)))**(-1) * Fr)**0.255 * (rho_p / rho_t * M)**0.078
    Dt = L * (0.675 * common_term + 1.12 * math.sqrt(rho_p / rho_t))
    ht = L * (9.45e-2 * common_term + 0.74 * math.sqrt(rho_p / rho_t))
    return Dt, ht

def crater_diameter_and_depth_2_4(E, tau_s, I, rho_t, c, rho_p, L):
    Dt = (E / tau_s)**0.22 * (I / (rho_t * c))**0.09 + 1.10 * math.sqrt(rho_p / rho_t) * L
    ht = 0.12 * (E / tau_s)**0.22 * (I / (rho_t * c))**0.09 + 0.55 * math.sqrt(rho_p / rho_t) * L
    return Dt, ht

def crater_penetration(D, rho_p, v, m, rho_t, Y, sigma_t, c):
    A0 = math.pi * (D / 2) ** 2             # Площадь поперечного сечения, м²
    L_char = 4 / 3 * D / 2
    h_hydro = (math.sqrt(rho_p / rho_t) * L_char * (v ** 2) / (2 * Y) * math.log(1 + (rho_t * v ** 2) / sigma_t))
    alpha = 0.4 + 0.05 * (v / 1000 - 5)
    m_eff = m * (1 - alpha)                 # Эффективная масса после потери, кг  
    r_crater = ((m * v ** 2 * rho_p) / (rho_t * Y)) ** (1 / 3)
    h_solid = (m_eff * (2000) ** 2) / (A0 * (rho_t * (2000) ** 2 + sigma_t))
    r_solid = math.sqrt((A0 * (1 + 2000 / c)) / math.pi)
    h_total = h_hydro + h_solid
    return h_hydro, r_crater, m_eff, h_solid, r_solid, h_total


Dt_3_1 = crater_diameter_3_1(rho_p, rho_t, g, E)
Dt_3_2 = crater_diameter_3_2(rho_p, rho_t, g, E)
Dt_3_3 = crater_diameter_3_3(E, rho_p, rho_t, L)
Dt_3_4 = crater_diameter_3_4(rho_p, rho_t, g, E, L)
Dt_2_2, ht_2_2 = crater_diameter_and_depth_2_2(E, tau_s, I, rho_t, c, rho_p, L)
Dt_2_3, ht_2_3 = crater_diameter_and_depth_2_3(rho_p, rho_t, g, v, L)
Dt_2_4, ht_2_4 = crater_diameter_and_depth_2_4(E, tau_s, I, rho_t, c, rho_p, L)
h_hydro, r_crater, m_eff, h_solid, r_solid, h_total = crater_penetration(D, rho_p, v, m, rho_t, Y, sigma_t, c)


print("Входные параметры:")
print(f"Диаметр тела L = {L} м, плотность тела ρₚ = {rho_p} кг/м³, скорость v = {v} м/с")
print(f"Плотность мишени ρₜ = {rho_t} кг/м³, g = {g} м/с², τ₀ = {tau_0} Па, c = {c} м/с")

print("\nВычисленные параметры:")
print(f"Масса тела m = {m:.3e} кг")
print(f"Кинетическая энергия E = {E:.3e} Дж")
print(f"Импульс I = {I:.3e} кг·м/с")
print(f"Эффективная прочность мишени(на глубине) τₛ= {tau_s}")

print("\nРезультаты расчёта диаметра кратера:")
print(f"Формула (3.1): Dt = {Dt_3_1:.3f} м")
print(f"Формула (3.2): Dt = {Dt_3_2:.3f} м")
print(f"Формула (3.3): Dt = {Dt_3_3:.3f} м")
print(f"Формула (3.4): Dt = {Dt_3_4:.3f} м")
print(f"Формула (2.2): Dt = {Dt_2_2:.3f} м, глубина кратера ht = {ht_2_2:.3f} м")
print(f"Формула (2.3): Dt = {Dt_2_3:.3f} м, глубина кратера ht = {ht_2_3:.3f} м")
print(f"Формула (2.4): Dt = {Dt_2_4:.3f} м, глубина кратера ht = {ht_2_4:.3f} м")

print("\nРучной вывод:")
print(f"Глубина проникновения (гидродинамическая фаза): {h_hydro:.2f} м")
print(f"Радиус кратера: {r_crater:.2f} м")
print(f"Глубина проникновения (фаза твёрдого тела): {h_solid:.2f} м")
print(f"Радиус поражённой зоны: {r_solid:.2f} м")
print(f"Общая глубина проникновения: {h_total:.2f} м")