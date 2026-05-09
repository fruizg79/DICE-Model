# -*- coding: utf-8 -*-
"""
dice_config.py
--------------
Parámetros de configuración del modelo DICE separados del código.
Se distinguen tres categorías:
  - INITIAL_CONDITIONS : estados iniciales del sistema
  - CALIBRATION        : parámetros estructurales del modelo
  - SCENARIO           : supuestos de política / escenario externo
"""

# ── Condiciones iniciales ────────────────────────────────────────────────────
INITIAL_CONDITIONS = {
    # Temperatura (°C sobre nivel preindustrial)
    "T_AT": 0.8,
    "T_LO": 0.0068,

    # Concentración de carbono (GtC): [atmósfera, océano superficial, océano profundo]
    "carbon_concentration": [830.4, 1527.0, 10010.0],

    # Capital inicial (billones USD 2010)
    "K0": 318.773,
}

# ── Calibración del módulo económico ────────────────────────────────────────
CALIBRATION_ECONOMIC = {
    # Función de producción Cobb-Douglas
    "alpha": 0.30,          # elasticidad del capital

    # Productividad Total de los Factores (TFP)
    "A_g": 0.0075,          # tasa de crecimiento inicial de A
    "A_d": 0.0012,          # tasa de decaimiento de A_g

    # Fuerza laboral / población
    "L_g": 0.01,            # tasa de crecimiento inicial de L
    "L_d": 0.015,           # tasa de decaimiento de L_g

    # Capital
    "K_d": 0.0625,          # tasa de depreciación del capital

    # Preferencias (función de utilidad CRRA)
    "theta": 0.50,          # elasticidad marginal de la utilidad del consumo
    "rho": 0.04,            # tasa de descuento pura

    # Función de bienestar social
    "theta_welfare": 1.45,
    "discount_rate_utility": 0.015,
}

# ── Calibración del módulo de abatimiento y daños ───────────────────────────
CALIBRATION_ABATEMENT = {
    # Costes de abatimiento: Lambda = theta_1 * mu^theta_2
    "theta_1": 0.01,
    "theta_2": 2.60,

    # Intensidad de emisiones
    "emission_intensity_d": 0.00001,    # tasa de reducción anual

    # Emisiones de uso de suelo
    "land_emissions_d": 0.01,           # tasa de reducción anual
}

CALIBRATION_DAMAGE = {
    # Función de daños: omega = pi_1*T + pi_2*T^2
    "pi_1": 0.001,
    "pi_2": 2.67e-3,
}

# ── Calibración del módulo climático ────────────────────────────────────────
CALIBRATION_CLIMATE = {
    # Ciclo de carbono (matriz de transición phi y vector b)
    "phi_matrix": [
        [0.912,  0.0383, 0.0   ],
        [0.088,  0.9592, 0.0003],
        [0.0,    0.0025, 0.9997],
    ],
    "b_matrix": [0.2727, 0.0, 0.0],

    # Módulo de temperatura (dos cajas: atmósfera + océano)
    "ep_1": 0.098,          # velocidad de ajuste de temperatura atmosférica
    "ep_hat_11": 0.8630,
    "ep_hat_12": 0.008624,
    "ep_hat_21": 0.025,
    "ep_hat_22": 0.975,

    # Forzamiento radiativo
    "cc_at_1750": 588.0,    # concentración CO2 en 1750 (GtC)
    "nu": 3.8,              # parámetro de forzamiento por CO2 (W/m²)
}

# ── Escenario de forzamiento exógeno ────────────────────────────────────────
SCENARIO_FORCING = {
    # Forzamiento no-CO2 (gases distintos al CO2)
    "f_ex_base_year_value": 0.25,   # W/m² en el año base
    "f_ex_end_year_value":  0.70,   # W/m² en el año final
    "f_ex_base_year": 2010,
    "f_ex_end_year":  2100,
}
