import math

def crater_diameter_and_depth_2_2(E, tau_s, I, rho_t, c, rho_p, L):
    Dt = (E / tau_s)**0.255 * (I / (rho_t * c))**0.078 + 1.20 * math.sqrt(rho_p / rho_t) * L
    ht = 0.14 * (E / tau_s)**0.255 * (I / (rho_t * c))**0.078 + 0.60 * math.sqrt(rho_p / rho_t) * L
    return Dt, ht

def calculate_penetration(N, L, rho_p, v0, rho_t, tau_0, c, alpha, k_pr, v_crit, shape="Цилиндр"):
    A0 = math.pi * (L/2)**2
    if shape == "Сфера":
        V = (4/3) * math.pi * (L/2)**3
    else:
        V = A0 * N
    m = rho_p * V
    E = 0.5 * m * v0**2
    I = m * v0

    if shape == "Сфера":
        tau_s = tau_0 + 0.3 * 9.81 * L * math.sqrt(rho_p * rho_t)
        Dt, ht = crater_diameter_and_depth_2_2(E, tau_s, I, rho_t, c, rho_p, L)
    else:
        tau_s = tau_0 + 0.3 * 9.81 * L * math.sqrt(rho_p * rho_t)
        Dt = (( (E / tau_s)**0.255 * (I / (rho_t * c))**0.078 + 1.20 * math.sqrt(rho_p / rho_t) * L ) * ((L / N)**(1/3)) )
        tau_s = tau_0 + 0.5 * N * math.sqrt(rho_p * rho_t)
        ht = (0.14 * (E / tau_s)**0.255 * (I / (rho_t * c))**0.078 + 0.60 * math.sqrt(rho_p / rho_t) * N ) *  ((N / (L))**(1/6))

    m_eff = m * (1 - alpha)
    h_solid = k_pr * (m_eff * v_crit) / (L**2)
    r_solid = math.sqrt((A0 * (1 + v_crit / c)) / math.pi)
    h_total = ht + h_solid

    return {
        'm': m,
        'E': E,
        'I': I,
        'h_hydro_2': ht,
        'd_crater_2': Dt,
        'h_solid': h_solid,
        'r_solid': r_solid,
        'h_total': h_total,
        'A0': A0
    }