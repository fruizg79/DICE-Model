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
runfile('C:/Users/fruiz/Documents/GitHub/pydicemodel/cpydicemodel.py',
        wdir='C:/Users/fruiz/Documents/GitHub/pydicemodel')

initial_year = 2017
end_year     = 2100
industrial_emissions_initial_value  = 33.61 #gtCO2
land_emissions_initial_value        = 3.3
emission_intenisity_initial_value   = 0.29
population_initial_value            = 7.8
capital_initial_value               = 318.773
tfp_initial_value                   = 5.276
abatement_rate_initial_value        = 0.99





dicemodel1 = cdicemodel(initial_year,
                 end_year,
                 industrial_emissions_initial_value,
                 land_emissions_initial_value,
                 emission_intenisity_initial_value,
                 population_initial_value,
                 capital_initial_value,
                 tfp_initial_value,
                 abatement_rate_initial_value)

for y in range(2017,2101):
    dicemodel1.get_one_step(y)

df = dicemodel1.df_output
