# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 08:01:41 2024

@author: fruiz
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
""" Initial Values"""


initial_year = 2017
end_year     = 2100

# Climate variables - JUST FYI
industrial_emissions               = 33.61 #gtCO2
land_emissions_initial_value       = 3.3
land_emissions_d                   = 0.01
total_emissions                    =  industrial_emissions + land_emissions_initial_value

carbon_concentration_initial_value = np.array([830.4,1527,10010 ])
carbon_emissions                   = np.array([36.91,0,0])
T_AT = 0.8
T_LO = 0.0068
temperature_vector_initial_value = np.array([T_AT,T_LO])
emission_intensity = industrial_emissions/124.41655945341294
emission_intensity_d = 0
# Abatement Cost:
abatement_rate_initial_value       = 0.25
abatement_rate_d                   = 0.01
emission_intensity_d               = 0.0
theta_1 = 0.01 # TBC
theta_2 = 2.6





# economic variables
s                 = 0.15 # Saving rate


theta =  0.5
rho   =  0.04

# Production 
alpha = 0.3
A0   = 5.276
A_g = 0.0075
A_d = 0.0012


L0   = 7.725
L_g = 0.01
L_d = 0.015

K0 = 318.773
K_d = 0.0625

# Welfare function paramenters
theta = 1.45
discount_rate_utility = 0.015 


dicemodel1 = cdicemodel(initial_year,
                 end_year,
                 industrial_emissions_initial_value,
                 land_emissions_initial_value,
                 emission_intenisity_initial_value,
                 population_initial_value,
                 capital_initial_value,
                 tfp_initial_value,
                 abatement_rate_initial_value)


