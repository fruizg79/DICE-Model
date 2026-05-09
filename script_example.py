# -*- coding: utf-8 -*-
"""
script_example.py
-----------------
Script de ejemplo para ejecutar el modelo DICE refactorizado.
Sustituye a la versión original que dependía de runfile() (Spyder).
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from cpydicemodel import cdicemodel   # importación estándar ✅

# ── Inputs del modelo ──────────────────────────────────────────────────────
# Estos son los únicos valores que el usuario necesita tocar para un escenario.

INITIAL_YEAR = 2023
END_YEAR     = 2100

# Emisiones (GtCO2)
INDUSTRIAL_EMISSIONS_0 = 37.0
LAND_EMISSIONS_0       = 3.3

# Intensidad de emisiones (GtCO2 / billón USD)
EMISSION_INTENSITY_0   = 0.27

# Población (miles de millones de personas)
POPULATION_0           = 7.8

# Capital inicial (billones USD 2010)
CAPITAL_0              = 318.773

# Productividad Total de los Factores
TFP_0                  = 5.276

# Política de abatimiento
ABATEMENT_RATE_0       = 0.001
ABATEMENT_RATE_GROWTH  = 0.25

# Tasa de ahorro
SAVING_RATE            = 0.20

# ── Instancia del modelo ───────────────────────────────────────────────────
model = cdicemodel(
    initial_year                      = INITIAL_YEAR,
    end_year                          = END_YEAR,
    industrial_emissions_initial_value = INDUSTRIAL_EMISSIONS_0,
    land_emissions_initial_value       = LAND_EMISSIONS_0,
    emission_intensity_initial_value   = EMISSION_INTENSITY_0,
    population_initial_value           = POPULATION_0,
    capital_initial_value              = CAPITAL_0,
    tfp_initial_value                  = TFP_0,
    abatement_rate_initial_value       = ABATEMENT_RATE_0,
    abatement_rate_growth              = ABATEMENT_RATE_GROWTH,
    saving_rate                        = SAVING_RATE,
    # Ejemplo de override de calibración sin tocar dice_config.py:
    # config={"CALIBRATION_ECONOMIC": {"alpha": 0.35}},
)

# ── Ejecución ──────────────────────────────────────────────────────────────
df    = model.run()
df_cc = model.df_carbon_concentration
df_t  = model.df_temperature

# ── Resultados en consola ──────────────────────────────────────────────────
print("=== Resumen final (año {}) ===".format(END_YEAR))
print(df[["Y", "Q", "T_AT", "total_emissions", "mu", "U"]].tail(5).to_string())

# ── Gráficas ───────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(14, 8))
fig.suptitle("DICE Model — Resultados base", fontsize=14)

axes[0, 0].plot(df.index, df["Y"], color="steelblue")
axes[0, 0].set_title("Producción bruta (Y)")
axes[0, 0].set_ylabel("Billones USD")

axes[0, 1].plot(df.index, df["Q"], color="seagreen")
axes[0, 1].set_title("Producción neta (Q)")
axes[0, 1].set_ylabel("Billones USD")

axes[0, 2].plot(df_cc.index, df_cc[["CC_AT", "CC_UP", "CC_LO"]])
axes[0, 2].set_title("Concentración de carbono")
axes[0, 2].legend(["Atmósfera", "Océano superf.", "Océano prof."])
axes[0, 2].set_ylabel("GtC")

axes[1, 0].plot(df.index, df["T_AT"], color="tomato")
axes[1, 0].set_title("Temperatura atmosférica (T_AT)")
axes[1, 0].set_ylabel("°C sobre preindustrial")

axes[1, 1].plot(df.index, df["total_emissions"], color="dimgray")
axes[1, 1].set_title("Emisiones totales")
axes[1, 1].set_ylabel("GtCO2")

axes[1, 2].plot(df.index, df["mu"], color="mediumpurple")
axes[1, 2].set_title("Tasa de abatimiento (μ)")
axes[1, 2].set_ylabel("Fracción")

plt.tight_layout()
plt.savefig("dice_results.png", dpi=150)
plt.show()
