# -*- coding: utf-8 -*-
"""
cpydicemodel.py
---------------
Modelo DICE (Dynamic Integrated Climate-Economy) — versión refactorizada.

Cambios respecto a la versión original:
  1. Todos los parámetros hardcodeados se leen de dice_config.py.
  2. Corregido el exponente en get_abatement_cost (mu**theta_2, no mu*theta_2**2).
  3. get_one_step devuelve un dict con métricas en lugar de una cadena fija.
  4. capital_initial_value del constructor se usa realmente (antes ignorado).
  5. Eliminada dependencia de runfile() (específico de Spyder).
  6. Pequeñas mejoras de robustez en get_temperature_vector y get_carbon_concentration.
"""

import numpy as np
import pandas as pd

from dice_config import (
    INITIAL_CONDITIONS,
    CALIBRATION_ECONOMIC,
    CALIBRATION_ABATEMENT,
    CALIBRATION_DAMAGE,
    CALIBRATION_CLIMATE,
    SCENARIO_FORCING,
)


class cdicemodel:
    """Modelo DICE en Python.

    Parameters
    ----------
    initial_year : int
    end_year : int
    industrial_emissions_initial_value : float   (GtCO2)
    land_emissions_initial_value : float         (GtCO2)
    emission_intensity_initial_value : float
    population_initial_value : float             (miles de millones)
    capital_initial_value : float                (billones USD 2010)
    tfp_initial_value : float
    abatement_rate_initial_value : float         (fracción, 0-1)
    abatement_rate_growth : float
    saving_rate : float                          (fracción, 0-1)
    config : dict, optional
        Permite sobreescribir cualquier subconjunto de parámetros de calibración
        sin editar dice_config.py. Ejemplo:
            config={"CALIBRATION_ECONOMIC": {"alpha": 0.35}}
    """

    def __init__(
        self,
        initial_year,
        end_year,
        industrial_emissions_initial_value,
        land_emissions_initial_value,
        emission_intensity_initial_value,
        population_initial_value,
        capital_initial_value,
        tfp_initial_value,
        abatement_rate_initial_value,
        abatement_rate_growth,
        saving_rate,
        config: dict = None,
    ):
        # ── Horizonte temporal ───────────────────────────────────────────────
        self.initial_year = initial_year
        self.end_year = end_year
        self._years = range(initial_year, end_year + 1)

        # ── Parámetros de configuración (con posible override) ───────────────
        cfg = {
            "INITIAL_CONDITIONS": dict(INITIAL_CONDITIONS),
            "CALIBRATION_ECONOMIC": dict(CALIBRATION_ECONOMIC),
            "CALIBRATION_ABATEMENT": dict(CALIBRATION_ABATEMENT),
            "CALIBRATION_DAMAGE": dict(CALIBRATION_DAMAGE),
            "CALIBRATION_CLIMATE": dict(CALIBRATION_CLIMATE),
            "SCENARIO_FORCING": dict(SCENARIO_FORCING),
        }
        if config:
            for section, overrides in config.items():
                cfg[section].update(overrides)

        ic  = cfg["INITIAL_CONDITIONS"]
        eco = cfg["CALIBRATION_ECONOMIC"]
        aba = cfg["CALIBRATION_ABATEMENT"]
        dmg = cfg["CALIBRATION_DAMAGE"]
        cli = cfg["CALIBRATION_CLIMATE"]
        frc = cfg["SCENARIO_FORCING"]

        # ── Condiciones iniciales ────────────────────────────────────────────
        self.T_AT = ic["T_AT"]
        self.T_LO = ic["T_LO"]
        self.carbon_concentration_initial_value = np.array(ic["carbon_concentration"], dtype=float)
        self.K0 = capital_initial_value  # usa el parámetro del constructor ✅

        # ── Emisiones ────────────────────────────────────────────────────────
        self.industrial_emissions_initial_value = industrial_emissions_initial_value
        self.land_emissions_initial_value = land_emissions_initial_value
        self.emission_intensity_initial_value = emission_intensity_initial_value
        self.total_emissions_initial_value = (
            industrial_emissions_initial_value + land_emissions_initial_value
        )

        self.emission_intensity_d = aba["emission_intensity_d"]
        self.land_emissions_d = aba["land_emissions_d"]

        # ── Abatimiento ──────────────────────────────────────────────────────
        self.abatement_rate_initial_value = abatement_rate_initial_value
        self.abatement_rate_g = abatement_rate_growth
        self.theta_1 = aba["theta_1"]
        self.theta_2 = aba["theta_2"]

        # ── Daños ────────────────────────────────────────────────────────────
        self.pi_1 = dmg["pi_1"]
        self.pi_2 = dmg["pi_2"]

        # ── Economía ─────────────────────────────────────────────────────────
        self.s = saving_rate
        self.theta = eco["theta"]
        self.rho = eco["rho"]
        self.alpha = eco["alpha"]
        self.A0 = tfp_initial_value
        self.A_g = eco["A_g"]
        self.A_d = eco["A_d"]
        self.L0 = population_initial_value
        self.L_g = eco["L_g"]
        self.L_d = eco["L_d"]
        self.K_d = eco["K_d"]

        # ── Bienestar ────────────────────────────────────────────────────────
        self.theta_welfare = eco["theta_welfare"]
        self.discount_rate_utility = eco["discount_rate_utility"]

        # ── Clima ────────────────────────────────────────────────────────────
        self.phi_matrix = np.array(cli["phi_matrix"])
        self.b_matrix = np.array(cli["b_matrix"])
        self.ep_1 = cli["ep_1"]
        self.P_temp = np.array([
            [cli["ep_hat_11"], cli["ep_hat_12"]],
            [cli["ep_hat_21"], cli["ep_hat_22"]],
        ])
        self.cc_at_1750 = cli["cc_at_1750"]
        self.nu = cli["nu"]

        # ── Forzamiento exógeno ──────────────────────────────────────────────
        self.f_ex_base_year_value = frc["f_ex_base_year_value"]
        self.f_ex_end_year_value = frc["f_ex_end_year_value"]
        self.f_ex_base_year = frc["f_ex_base_year"]
        self.f_ex_end_year = frc["f_ex_end_year"]

        # ── Inicialización de DataFrames ─────────────────────────────────────
        self.temperature_vector_initial_value = np.array([self.T_AT, self.T_LO])
        self.df_output = self._init_df_output()
        self.df_temperature = self._init_df_temperature()
        self.df_carbon_concentration = self._init_df_carbon()

    # ── Inicialización de DataFrames ─────────────────────────────────────────

    def _init_df_output(self) -> pd.DataFrame:
        cols = [
            "Y", "K", "I", "L", "A", "U", "T_AT", "T_LO",
            "mu", "total_emissions", "industrial_emissions",
            "land_emissions", "Q", "emission_intensity",
        ]
        return pd.DataFrame(index=self._years, columns=cols, dtype=float)

    def _init_df_temperature(self) -> pd.DataFrame:
        df = pd.DataFrame(index=self._years, columns=["T_AT", "T_LO"], dtype=float)
        df.loc[self.initial_year, "T_AT"] = self.T_AT
        df.loc[self.initial_year, "T_LO"] = self.T_LO
        return df

    def _init_df_carbon(self) -> pd.DataFrame:
        df = pd.DataFrame(index=self._years, columns=["CC_AT", "CC_UP", "CC_LO"], dtype=float)
        df.loc[self.initial_year] = self.carbon_concentration_initial_value
        return df

    # ── Módulo económico ──────────────────────────────────────────────────────

    def get_gross_production(self, year: int) -> float:
        tau = year - self.initial_year
        A_g = self.A_g * (1 + self.A_d) ** -tau
        L_g = self.L_g * (1 + self.L_d) ** -tau
        A = self.A0 * (1 + A_g) ** tau
        L = self.L0 * (1 + L_g) ** tau
        K = self.get_capital(year)
        Y = A * K ** self.alpha * L ** (1 - self.alpha)
        self.df_output.loc[year, ["Y", "L", "K", "A"]] = [Y, L, K, A]
        return Y

    def get_net_production(self, year: int, abatement_cost: float, damage_cost: float, Y: float) -> float:
        Q = (1 - abatement_cost) / (1 + damage_cost) * Y
        self.df_output.loc[year, "Q"] = Q
        return Q

    def get_capital(self, year: int) -> float:
        if year == self.initial_year:
            K = self.K0
        else:
            I = self.get_investment(year)
            K = self.df_output.loc[year - 1, "K"] * (1 - self.K_d) + I
        self.df_output.loc[year, "K"] = K
        return K

    def get_investment(self, year: int) -> float:
        if year == self.initial_year:
            I = 0.0
        else:
            Q_prev = self.df_output.loc[year - 1, "Q"]
            I = self.s * Q_prev
        self.df_output.loc[year, "I"] = I
        return I

    def get_utility_function(self, consumption_per_cap: float) -> float:
        C = consumption_per_cap
        return (C ** (1 - self.theta) - 1) / (1 - self.theta)

    def get_discount_factor_utility(self, year: int) -> float:
        tau = year - self.initial_year
        return (1 + self.discount_rate_utility) ** -tau

    def get_discounted_utility(self, total_consumption: float, population: float, year: int) -> float:
        consumption_per_cap = total_consumption / population
        discount_factor = self.get_discount_factor_utility(year)
        U_prev = self.df_output.loc[year - 1, "U"] if year > self.initial_year else 0.0
        U_prev = 0.0 if pd.isna(U_prev) else U_prev
        U = U_prev + self.get_utility_function(consumption_per_cap) * population * discount_factor
        self.df_output.loc[year, "U"] = U
        return U

    # ── Módulo de emisiones ───────────────────────────────────────────────────

    def get_emission_intensity(self, year: int) -> float:
        tau = year - self.initial_year
        ei = self.emission_intensity_initial_value * (1 + self.emission_intensity_d) ** -tau
        self.df_output.loc[year, "emission_intensity"] = ei
        return ei

    def get_abatement_rate(self, year: int) -> float:
        if year == self.initial_year:
            mu = 0.0
        else:
            tau = year - self.initial_year - 1
            mu = self.abatement_rate_initial_value * (1 + self.abatement_rate_g) ** tau
            mu = min(1.0, mu)
        self.df_output.loc[year, "mu"] = mu
        return mu

    def get_land_emissions(self, year: int) -> float:
        tau = year - self.initial_year
        le = self.land_emissions_initial_value * (1 + self.land_emissions_d) ** -tau
        self.df_output.loc[year, "land_emissions"] = le
        return le

    def get_industrial_emissions(self, year: int, Y: float) -> float:
        ei = self.get_emission_intensity(year)
        mu = self.get_abatement_rate(year)
        ie = ei * (1 - mu) * Y
        self.df_output.loc[year, "industrial_emissions"] = ie
        return ie

    def get_total_emissions(self, year: int, Y: float) -> float:
        ie = self.get_industrial_emissions(year, Y)
        le = self.get_land_emissions(year)
        te = ie + le
        self.df_output.loc[year, "total_emissions"] = te
        return te

    # ── Módulo de costes ──────────────────────────────────────────────────────

    def get_abatement_cost(self, mu: float) -> float:
        # CORRECCIÓN: exponente sobre mu, no sobre theta_2 ✅
        return self.theta_1 * mu ** self.theta_2

    def get_damage_cost(self, temperature_at: float) -> float:
        return self.pi_1 * temperature_at + self.pi_2 * temperature_at ** 2

    # ── Módulo climático ──────────────────────────────────────────────────────

    def get_carbon_concentration(self, year: int, carbon_emissions: np.ndarray) -> np.ndarray:
        if year == self.initial_year:
            return self.carbon_concentration_initial_value
        prior = self.df_carbon_concentration.loc[year - 1].values.astype(float)
        new_cc = self.phi_matrix @ prior + self.b_matrix * carbon_emissions[0]
        self.df_carbon_concentration.loc[year] = new_cc
        return new_cc

    def get_exogenous_forcing(self, year: int) -> float:
        f0 = self.f_ex_base_year_value
        f1 = self.f_ex_end_year_value
        y0 = self.f_ex_base_year
        y1 = self.f_ex_end_year
        if year <= y1:
            return f0 + (year - y0) / (y1 - y0) * (f1 - f0)
        return f1

    def get_radiative_forcing(self, cc_at: float, F_ex: float) -> float:
        return self.nu / np.log(2) * np.log(cc_at / self.cc_at_1750) + F_ex

    def get_temperature_vector(self, year: int, radiative_forcing: float) -> np.ndarray:
        if year == self.initial_year:
            tv = self.temperature_vector_initial_value.copy()
        else:
            prior = self.df_temperature.loc[year - 1].values.astype(float)
            B_temp = np.array([self.ep_1, 0.0])
            tv = self.P_temp @ prior + B_temp * radiative_forcing
        self.df_temperature.loc[year] = tv
        self.df_output.loc[year, ["T_AT", "T_LO"]] = tv
        return tv

    # ── Paso del modelo ───────────────────────────────────────────────────────

    def get_one_step(self, year: int) -> dict:
        """Avanza el modelo un año.

        Returns
        -------
        dict con las métricas principales del período.
        """
        Y = self.get_gross_production(year)
        mu = self.get_abatement_rate(year)
        total_emissions = self.get_total_emissions(year, Y)

        carbon_emissions = np.array([total_emissions, 0.0, 0.0])
        cc = self.get_carbon_concentration(year, carbon_emissions)
        F_ex = self.get_exogenous_forcing(year)
        F_rad = self.get_radiative_forcing(cc[0], F_ex)
        tv = self.get_temperature_vector(year, F_rad)

        T_AT = tv[0]
        abatement_cost = self.get_abatement_cost(mu)
        damage_cost = self.get_damage_cost(T_AT)
        Q = self.get_net_production(year, abatement_cost, damage_cost, Y)

        total_consumption = (1 - self.s) * Q
        L = self.df_output.loc[year, "L"]
        U = self.get_discounted_utility(total_consumption, L, year)

        return {
            "year": year,
            "Y": Y,
            "Q": Q,
            "T_AT": T_AT,
            "CC_AT": cc[0],
            "total_emissions": total_emissions,
            "mu": mu,
            "U": U,
        }

    # ── Ejecución completa ────────────────────────────────────────────────────

    def run(self) -> pd.DataFrame:
        """Ejecuta el modelo para todo el horizonte temporal."""
        for year in self._years:
            self.get_one_step(year)
        return self.df_output
