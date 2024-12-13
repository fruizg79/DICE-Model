# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 08:09:18 2024

@author: fruiz
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math

class cdicemodel:
    def __init__(self):
        self.params = []
    
    def get_utility_function(C,theta):
       # C     : Consumption per capita
       # theta : 
       # rho   : discount rate 
        U = (C**(1-theta)-1)/(1-theta)
        return U
    
    
    def get_gross_production(A,K,L,alpha):
        Y  = A*K**alpha*L**(1-alpha)
        return Y
    
    def get_damage_cost(temperature_at):
        pi_1 = 0
        pi_2 = 2.67*10**-3
        omega = pi_1*temperature_at+pi_2*temperature_at**2
        return omega
    
    def get_abatement_cost(theta_1,theta_2,mu):
        # theta_1 :
        # theta_2 :
        # mu      : price of backstop technologies
        abatement_cost = theta_1*mu*theta_2**2
        return abatement_cost
    
    def get_industrial_emissions(emission_intensity,
                                abatement_rate,Y):
        industrial_emissions = emission_intensity*(1-abatement_rate)*Y
        return industrial_emissions
    
    
    
    def get_discount_factor_utility(discount_rate_utility,
                                    initial_year,
                                    current_year):
        discount_factor_utility = (1+discount_rate_utility)**-(current_year-initial_year)
        return discount_factor_utility
    
    def get_discounted_utility(consumption,
                               population,
                               theta,
                                discount_rate_utility,
                               initial_year,
                               current_year):
            discount_factor_utility = (1+discount_rate_utility)**-(current_year-initial_year)
            discounted_utility      = get_utility_function(C/population,theta)*population*discount_factor_utility
            
            return discounted_utility
        
    def get_carbon_concentration(carbon_concentration,carbon_emissions):
        """ CC = (CC_AT, CC_UP, CC_LO)
        
            phi_matrix = [ phi_11,phi_12,0
                           phi_21,phi_22,phi_32
                           0, phi_32, phi_33]
            
            b_matrix = [phi_b1,0,0]
        """
        phi_matrix           = np.array([[0.912, 0.0383, 0],
                                     [0.088, 0.9592, 0.0003],
                                     [0,0.0025,0.9997]])
    
        b_matrix             = np.array([0.2727,0,0])
        new_carbon_concentration = np.dot(phi_matrix,carbon_concentration) + np.dot(b_matrix,carbon_emissions)
        
        return new_carbon_concentration
        
    def get_exogenous_forcing(year):
        base_year = 2010
        end_year  = 2100
        f_ex_base_year = 0.25 #w/m2
        f_ex_end_year  = 0.70 #w/m2
        if year <= end_year:
            F_ex = f_ex_base_year + (year-base_year)/(end_year-base_year)*(f_ex_end_year-f_ex_base_year)
        elif year>end_year:
            F_ex = f_ex_end_year
        else:
            print("error: year is not correct for exogenous forcing")
            
        return F_ex
    
        
    def get_radiative_forcing(cc_at,F_ex):
        # 
        # This function links accumulated carbon emissions in the atmosphere and global
        # warming at the Earth’s surface through increases in radiative forcing. 
        #
        # 
        # mu                 :  3.8 W/m2 is the temperature forcing parameter
        # cc_at              : 
        # cc_at1750          : 588
        # F_ex               : is the exogenous forcing
        # radiotive_forcing  :  the output is the change in total radiative forcing 
        #                        of GHG emissions since 1750 (expressed in W/m2).
        # 
        #
        #
        
        cc_at1750  = 588 
        nu         = 3.8
        
        radiative_forcing = nu/np.log(2)*np.log(cc_at/cc_at1750) + F_ex
        return radiative_forcing
        
    def get_temperature_vector(temperature_vector,radiative_forcing):
        """This system of equations means that “higher radiative forcing warms the atmospheric
         layer, which then warms the upper ocean, gradually warming the deep ocean
         
         Nordhaus simplifies the relationships by only considering a two-box model: the
         atmosphere and the upper ocean
         
         """
        # temperature_vector = [T_AT,T_LO]
        #
        # ep_1 is measures the speed of adjustment parameter for atmospheric temperature
        # ep_2 is the ratio of increased forcing from CO2 doubling to the climate sensitivity
        # ep_3 is the heat loss coefficient from atmosphere to oceans
        # ep_4   is the heat gain coefficient by deep ocean
        # T_AT_new = T_AT + ep_1*(radiative_forcing -ep_2*T_AT - ep_3*(T_AT-T_LO))
        # T_LO_new = T_LO + ep_4*(T_AT-T_LO)
        # 
        #  ep_hat_11 = 1-ep_1*(ep_2 + ep_3)
        #  ep_hat_12 = ep_1*ep_3
        #  ep_hat21  = ep_4
        #  ep_hat22  = 1 - ep_4
        
        ep_1     =  0.098
        ep_hat_11 = 86.30*10**-2
        ep_hat_12 = 0.8624*10**-2
        ep_hat_21 = 2.5*10**-2
        ep_hat_22 = 97.5*10**-2
        
        P  = np.array([[ep_hat_11,ep_hat_12],
                     [ep_hat_21,ep_hat_22]])
        
        B  = np.array([ep_1,0]) 
        # T_AT_new, T_LO_new
        temperature_vector_new = np.dot(P,temperature_vector)+np.dot(B,radiative_forcing)
        return temperature_vector_new 



if __name__ == "__main__":
    cdicemodel()