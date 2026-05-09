# -*- coding: utf-8 -*-
"""
dice_config.py
--------------
Configuration parameters for the DICE model, separated from the model code.
Three categories are distinguished:
  - INITIAL_CONDITIONS : initial states of the system
  - CALIBRATION_*      : structural parameters of the model
  - SCENARIO_*         : policy / external scenario assumptions
"""

# ── Initial conditions ───────────────────────────────────────────────────────
INITIAL_CONDITIONS = {
    # Temperature (°C above pre-industrial level)
    "T_AT": 0.8,
    "T_LO": 0.0068,

    # Carbon concentration (GtC): [atmosphere, upper ocean, deep ocean]
    "carbon_concentration": [830.4, 1527.0, 10010.0],

    # Initial capital stock (trillion USD 2010)
    "K0": 318.773,
}

# ── Economic module calibration ──────────────────────────────────────────────
CALIBRATION_ECONOMIC = {
    # Cobb-Douglas production function
    "alpha": 0.30,          # capital elasticity

    # Total Factor Productivity (TFP)
    "A_g": 0.0075,          # initial TFP growth rate
    "A_d": 0.0012,          # decay rate of A_g

    # Labor force / population
    "L_g": 0.01,            # initial labor force growth rate
    "L_d": 0.015,           # decay rate of L_g

    # Capital
    "K_d": 0.0625,          # capital depreciation rate

    # Preferences (CRRA utility function)
    "theta": 0.50,          # marginal elasticity of consumption utility
    "rho": 0.04,            # pure rate of time preference

    # Social welfare function
    "theta_welfare": 1.45,
    "discount_rate_utility": 0.015,
}

# ── Abatement and damage calibration ────────────────────────────────────────
CALIBRATION_ABATEMENT = {
    # Abatement cost function: Lambda = theta_1 * mu^theta_2
    "theta_1": 0.01,
    "theta_2": 2.60,

    # Emission intensity
    "emission_intensity_d": 0.00001,    # annual reduction rate

    # Land-use emissions
    "land_emissions_d": 0.01,           # annual reduction rate
}

CALIBRATION_DAMAGE = {
    # Damage function: omega = pi_1*T + pi_2*T^2
    "pi_1": 0.001,
    "pi_2": 2.67e-3,
}

# ── Climate module calibration ───────────────────────────────────────────────
CALIBRATION_CLIMATE = {
    # Carbon cycle (transition matrix phi and forcing vector b)
    "phi_matrix": [
        [0.912,  0.0383, 0.0   ],
        [0.088,  0.9592, 0.0003],
        [0.0,    0.0025, 0.9997],
    ],
    "b_matrix": [0.2727, 0.0, 0.0],

    # Temperature module (two-box model: atmosphere + ocean)
    "ep_1": 0.098,          # speed-of-adjustment parameter for atmospheric temperature
    "ep_hat_11": 0.8630,
    "ep_hat_12": 0.008624,
    "ep_hat_21": 0.025,
    "ep_hat_22": 0.975,

    # Radiative forcing
    "cc_at_1750": 588.0,    # atmospheric CO2 concentration in 1750 (GtC)
    "nu": 3.8,              # CO2 forcing parameter (W/m²)
}

# ── Exogenous forcing scenario ───────────────────────────────────────────────
SCENARIO_FORCING = {
    # Non-CO2 greenhouse gas forcing
    "f_ex_base_year_value": 0.25,   # W/m² in base year
    "f_ex_end_year_value":  0.70,   # W/m² in end year
    "f_ex_base_year": 2010,
    "f_ex_end_year":  2100,
}
