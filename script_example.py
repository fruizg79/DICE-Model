# -*- coding: utf-8 -*-
"""
script_example.py
-----------------
Example script for running the refactored DICE model.
Replaces the original version that depended on runfile() (Spyder-specific).
"""

import pandas as pd
import matplotlib.pyplot as plt

from cpydicemodel import cdicemodel

# ── Model inputs ───────────────────────────────────────────────────────────────
# These are the only values a user needs to change to define a scenario.

INITIAL_YEAR = 2023
END_YEAR     = 2100

# Emissions (GtCO2)
INDUSTRIAL_EMISSIONS_0 = 37.0
LAND_EMISSIONS_0       = 3.3

# Emission intensity (GtCO2 / trillion USD)
EMISSION_INTENSITY_0   = 0.27

# Population (billions)
POPULATION_0           = 7.8

# Initial capital stock (trillion USD 2010)
CAPITAL_0              = 318.773

# Total Factor Productivity
TFP_0                  = 5.276

# Abatement policy
ABATEMENT_RATE_0       = 0.001
ABATEMENT_RATE_GROWTH  = 0.25

# Saving rate
SAVING_RATE            = 0.20

# ── Model instance ─────────────────────────────────────────────────────────────
model = cdicemodel(
    initial_year                       = INITIAL_YEAR,
    end_year                           = END_YEAR,
    industrial_emissions_initial_value = INDUSTRIAL_EMISSIONS_0,
    land_emissions_initial_value       = LAND_EMISSIONS_0,
    emission_intensity_initial_value   = EMISSION_INTENSITY_0,
    population_initial_value           = POPULATION_0,
    capital_initial_value              = CAPITAL_0,
    tfp_initial_value                  = TFP_0,
    abatement_rate_initial_value       = ABATEMENT_RATE_0,
    abatement_rate_growth              = ABATEMENT_RATE_GROWTH,
    saving_rate                        = SAVING_RATE,
    # Example calibration override without editing dice_config.py:
    # config={"CALIBRATION_ECONOMIC": {"alpha": 0.35}},
)

# ── Run ────────────────────────────────────────────────────────────────────────
df    = model.run()
df_cc = model.df_carbon_concentration
df_t  = model.df_temperature

# ── Console summary ────────────────────────────────────────────────────────────
print(f"=== Summary — final year ({END_YEAR}) ===")
print(df[["Y", "Q", "T_AT", "total_emissions", "mu", "U"]].tail(5).to_string())

# ── Charts ─────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(14, 8))
fig.suptitle("DICE Model — Baseline results", fontsize=14)

axes[0, 0].plot(df.index, df["Y"], color="steelblue")
axes[0, 0].set_title("Gross output (Y)")
axes[0, 0].set_ylabel("Trillion USD")

axes[0, 1].plot(df.index, df["Q"], color="seagreen")
axes[0, 1].set_title("Net output (Q)")
axes[0, 1].set_ylabel("Trillion USD")

axes[0, 2].plot(df_cc.index, df_cc[["CC_AT", "CC_UP", "CC_LO"]])
axes[0, 2].set_title("Carbon concentration")
axes[0, 2].legend(["Atmosphere", "Upper ocean", "Deep ocean"])
axes[0, 2].set_ylabel("GtC")

axes[1, 0].plot(df.index, df["T_AT"], color="tomato")
axes[1, 0].set_title("Atmospheric temperature (T_AT)")
axes[1, 0].set_ylabel("°C above pre-industrial")

axes[1, 1].plot(df.index, df["total_emissions"], color="dimgray")
axes[1, 1].set_title("Total emissions")
axes[1, 1].set_ylabel("GtCO2")

axes[1, 2].plot(df.index, df["mu"], color="mediumpurple")
axes[1, 2].set_title("Abatement rate (μ)")
axes[1, 2].set_ylabel("Fraction")

plt.tight_layout()
plt.savefig("dice_results.png", dpi=150)
plt.show()
