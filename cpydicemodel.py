# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 08:09:18 2024

@author: fruizg79@gmail.com
"""
import numpy as np
import pandas as pd



class cdicemodel:
    def __init__(self,initial_year,
                     end_year,
                     industrial_emissions_initial_value,
                     land_emissions_initial_value,
                     emission_intenisity_initial_value,
                     population_initial_value,
                     capital_initial_value,
                     tfp_initial_value,
                     abatement_rate_initial_value):
        
        self.initial_year = initial_year
        self.end_year = end_year
        self.industrial_emissions_initial_value = industrial_emissions_initial_value
        self.land_emissions_initial_value =land_emissions_initial_value
        self.emission_intensity_initial_value = emission_intenisity_initial_value
        self.land_emissions_d  = 0.01
        self.total_emissions_initial_value   =  industrial_emissions_initial_value \
                                                + land_emissions_initial_value
        self.carbon_concentration_initial_value = np.array([830.4,1527,10010 ])
        self.carbon_emissions  =  np.array([self.total_emissions,0,0])
        self.T_AT = 0.8
        self.T_LO = 0.0068
        self.temperature_vector_initial_value = self.get_temperature_vector_initial_value()
        self.emission_intensity_d = 0
        # Abatement Cost:
        self.abatement_rate_initial_value       = abatement_rate_initial_value
        self.abatement_rate_d                   = 0.01
        self.emission_intensity_d               = 0.0
        self.theta_1 = 0.01 # TBC
        self.theta_2 = 2.6
        # economic variables
        self.s   = 0.15 # Saving rate        
        self.theta =  0.5
        self.rho   =  0.04
        self.alpha = 0.3
        self.A0  = tfp_initial_value#~5.276 # initial value
        self.A_g =  0.0075 # initial_value
        self.A_d = 0.0012
        self.L0   = population_initial_value#~7.725 # Labor force = Population 
        self.L_g  = 0.01 # Labor force growth
        self.L_d  = 0.015 # Rate of variation of labor force growth
        self.K0 = 318.773 # Initial Capital Value
        self.K_d = 0.0625 # Capital Depreciation
        # Welfare function paramenters
        self.theta_welfare         = 1.45
        self.discount_rate_utility = 0.015 
        # Dataframe with outputs
        self.df_output = self.get_df_output()



    def get_df_output(self):
        df_output = pd.DataFrame(columns=["Y","K","I","L","A","U","T_AT",\
                                          "mu", "total_emissions","industrial_emissions",\
                                              "land_emissions"],
                                 index = range(self.initial_year,self.end_year+1))
        return df_output
        
    def get_emission_intensity(self,year):
        tau = year - self.initial_year
        emission_intensity = self.emission_intensity_initial*(1+self.emission_intensity_d)**-tau
        return emission_intensity
        
    def get_temperature_vector_initial_value(self):
        temperature_vector_initial_value = np.array([self.T_AT,self.T_LO])
        return temperature_vector_initial_value
    
    def get_utility_function(self,consumption_per_cap):
       # C     : Consumption per capita
       # theta : 
        C = consumption_per_cap
        U = (C**(1-self.theta)-1)/(1-self.theta)
        return U
    
    def get_gross_production(self,year):
        tau = (year-self.initial_year)
        A_g  = self.A_g*(1+self.A_d)**-tau
        L_g  = self.L_g*(1+self.L_d)**-tau
        A    = self.A0*(1 + A_g)**tau
        L    = self.L0*(1 +L_g)**tau
        K    = self.get_capital(self,year)
        Y  = A*K**self.alpha*L**(1-self.alpha)
        self.df_output.loc[year]["Y"] = Y
        self.df_output.loc[year]["L"] = L
        self.df_output.loc[year]["K"] = K
        return Y
    
    def get_net_production(self,year,abatement_cost,damage_cost,Y):
        Q = (1-abatement_cost)/(1-damage_cost)*Y
        self.df_output[year]["Q"] = Q
        return Q
    
    def get_abatement_rate(self,year):
        if year==self.initial_year:
            abatemenr_rate = 0            
        else:
            tau = year - self.initial_year-1
            abatemenr_rate = self.abatement_rate_initial_value*(1+self.abatement_rate_d)**-tau
        self.df_output.loc[year]["mu"] = abatemenr_rate
        return abatemenr_rate

    def get_damage_cost(temperature_at):
        pi_1 = 0
        pi_2 = 2.67*10**-3
        omega = pi_1*temperature_at+pi_2*temperature_at**2
        return omega
    
    def get_abatement_cost(self,mu):
        # theta_1 :
        # theta_2 :
        # mu      : price of backstop technologies
        abatement_cost = self.theta_1*mu*self.theta_2**2
        return abatement_cost
    
    def get_land_emissions(self,year):
        tau = year - self.initial_year
        land_emissions = self.land_emissions_initial_value*(1+self.and_emissions_d)**-tau
        self.df_output.loc[year]["land_emissions"] = land_emissions
        return land_emissions
    
    def get_industrial_emissions(self,year,Y):
        emission_intensity = self.get_emission_intensity(year)
        abatement_rate = self.get_abatement_rate(year)
        industrial_emissions = emission_intensity*(1-abatement_rate)*Y
        self.df_output.loc[year]["industrial_emissions"] = industrial_emissions
        return industrial_emissions
    
    def get_total_emissions(self,year,Y):
        industrial_emissions = self.get_industrial_emissions(year, Y)
        land_emissions       = self.get_land_emissions(year)
        total_emissions = industrial_emissions + land_emissions
        self.df_output.loc[year]["total_emissions"] = total_emissions
        return total_emissions
    
    def get_discount_factor_utility(self,year):
        discount_factor_utility = (1 +self.discount_rate_utility)**-(year \
                                - self.initial_year)
        return discount_factor_utility
    
    def get_discounted_utility(self,total_consumption,
                               population,
                               current_year):
            consumption_per_cap     = total_consumption/population
            discount_factor_utility = (1 + self.discount_rate_utility)**-(current_year-self.initial_year)
            discounted_utility      = self.get_utility_function(consumption_per_cap,self.theta)*population*discount_factor_utility
            self.df_output[current_year]["U"] = discounted_utility
            return discounted_utility
        
    def get_carbon_concentration(self,
                                 carbon_concentration,
                                 carbon_emissions):
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
        # cc_at              : carbon concentration
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
    def get_capital(self,year):
        if year==self.ininitial_year:
            K = self.K0
        else:
            
            K = self.df_output.loc[year-1]['K']*(1-self.K_d) \
                + self.df_output.loc[year-1]['I']*(1-self.K_d)
        self.df_output.loc[year]['K']=K
        return K
    def get_investment(self,year):
        if year==self.initial_year:
            I = 0
            self.out
        else:
            I = self.s*self.df_output.loc[year-1]["Q"] # check this
        self.df_output.loc[year]["I"] = I
        return I

    def get_one_step(self,year):
        try:
            Y                    = self.get_gross_production(year)
            abatement_rate       = self.get_abatement_rate(year)
            total_emissions      =  self.get_total_emissions(year, Y)
            carbon_emissions     =  np.array([total_emissions,0,0])
            
            
            F_ex                   = self.get_exogenous_forcing(year)
            if year == self.initial_year:
                carbon_concentration   = self.carbon_concentration_initial_value #
                temperature_vector     = self.temperature_vector_initial_value
            else:
                carbon_concentration = self.get_carbon_concentration(carbon_concentration,carbon_emissions)
                F_rad                  = self.get_radiative_forcing(carbon_concentration[0],F_ex)
                temperature_vector     = self.get_temperature_vector(temperature_vector,F_rad)
            
            temperature_at         = temperature_vector[0]
            abatement_cost =  self.get_abatement_cost(abatement_rate)
            damage_cost    =  self.get_damage_cost(temperature_at)
            
            Q = self.get_net_production(year, abatement_cost, damage_cost, Y)
            I = self.get_investment(year)
            total_consumption = (1-self.s)*Q
            population        = self.df_output[year]["L"]
            
            U = self.get_discounted_utility(total_consumption,population,year)
            output = "OK"
        except:
                output = "something wrong happened"

        return output
        
                

if __name__ == "__main__":
    cdicemodel()