from pyflowtool import *
import numpy as np

# constant variables
tau_respiration = 20
tau_circulation = 800

# macros
sK0 = 10**(-1.6)
sK1 = 10**(-5.9)
sK2 = 10**(-9)
sKs = 10**(-6.4)
dK0 = 10**(-1.3)
dK1 = 10**(-6.1)
dK2 = 10**(-9.3)
dKs = 10**(-6.15)
Natm = 1.773e20
mpg = 1/12
Msurf = 2.7e19
Mdeep = 1.3e21
mixing = 1.3e21/800

def log(x):
	return np.log(x)

def CO3(DIC, ALK):
	return ALK - DIC
	
def HCO3(DIC, ALK):
	return (2 * DIC) - ALK

def pH(DIC, ALK, K2):
	return -log(K2 * ((2 * DIC) - ALK) / (ALK - DIC))
	
def CO2(DIC, ALK, K0, K1, K2):
	return (K2 / K0 / K1) * ((2 * DIC) - ALK) * ((2 * DIC) - ALK) / (ALK - DIC)
	
def O(DIC, ALK, Ks):
	return (ALK - DIC) * 1e-2 / Ks
	
def CSH(CO3, Ks):
	return (log(CO3) - 2 - log(Ks)) / 0.08

@pf_setup
def init():
	# define inventories
	pf_make_inventory('Land biomass', 2000e15/12.0)
	pf_make_inventory('atmosphere', 280e-6*Natm)
	pf_make_inventory('Surface ocean C', 1950e-6*Msurf)
	pf_make_inventory('deep ocean C', 2200e-6*Mdeep)
	pf_make_inventory('deep ocean sediments C', 0)
	pf_make_inventory('surface ocean alkalinity', 2250e-6*Msurf)
	pf_make_inventory('deep ocean A', 2350e-6*Mdeep)
	pf_make_inventory('sediments A', 0)
	#define displays
	pf_make_display('Conc.', vs=['ALKdeep', 'ALKsurf', 'DICdeep', 'DICsurf'])
	pf_make_display('pH & CSH', vs=['surfpH', 'deeppH', 'CSH'])
	
@pf_flow(name='Respiration', source='Land biomass', sink='atmosphere')
def respiration(t, m):
	return m['Land biomass'] / tau_respiration
	
@pf_flow(name='Photosynthesis', sink='Land biomass', source='atmosphere')
def photosynthesis(t, m):
	return 100e15*mpg

@pf_flow(name='CO2 exchange', source='atmosphere', sink='Surface ocean C', clamp=False)
def co2exch(t, m):
	return 1 * (m['atmCO2'] - m['surfCO2']) * 0.06e6 * 3.49e14
	
@pf_flow(name='CaRainC', source='deep ocean sediments C', sink='Surface ocean C')
def carain(t, m):
	return 1e15*mpg
	
@pf_flow(name='EP', source='Surface ocean C', sink='deep ocean C')
def ep(t, m):
	return 4e15*mpg
	
@pf_flow(name='CirculationC', source='Surface ocean C', sink='deep ocean C', clamp=False)
def circulation(t, m):
	return (m['DICsurf'] - m['DICdeep'])*Mdeep/tau_circulation
	
@pf_flow(name='CaCO3 dissolutionC', source='deep ocean sediments C', sink='deep ocean C')
def caco3disol(t, m):
	return m['CaRainC'] * (1 - m['F preserved'])

@pf_var(name='anthroC')
def anthroC(t, m):
	return m['Business As Usual']*12/(1e15)
	
@pf_var(name='atm_growth')
def atmgrowth(t, m):
	return (m['Respiration']-m['Photosynthesis']-m['CO2 exchange'])*12/(1e15)
	
@pf_var(name='ocean_carbon')
def oceancarbon(t, m):
	return (m['CO2 exchange']+m['Business As Usual'])*12/(1e15)
		
@pf_var(name='F preserved')
def fpreserved(t, m):
	return 0.0

@pf_var(name='CSH')
def csh(t, m):
	return CSH(m['deepCO3'], dKs)
	
@pf_var(name='deepCO3')
def deepco3(t, m):
	return CO3(m['DICdeep'], m['ALKdeep'])
	
@pf_var(name='deeppH')
def deepph(t, m):
	return pH(m['DICdeep'], m['ALKdeep'], dK2)
	
@pf_var(name='DICdeep')
def dicdeep(t, m):
	return m['deep ocean C']/Mdeep
	
@pf_var(name='ALKdeep')
def alkdeep(t, m):
	return m['deep ocean A']/Mdeep
	
@pf_var(name='surfO')
def surfo(t, m):
	return O(m['DICsurf'], m['ALKsurf'], sKs)
	
@pf_var(name='surfpH')
def surfph(t, m):
	return pH(m['DICsurf'], m['ALKsurf'], sK2)
	
@pf_var(name='surfCO2')
def surfco2(t, m):
	return CO2(m['DICsurf'], m['ALKsurf'], sK0, sK1, sK2)
	
@pf_var(name='DICsurf')
def dicsurf(t, m):
	return m['Surface ocean C']/Msurf
	
@pf_var(name='ALKsurf')
def alksurf(t, m):
	return m['surface ocean alkalinity']/Msurf
	
@pf_var(name='atmCO2')
def atmCO2(t, m):
	return m['atmosphere'] / Natm
	
@pf_flow(name='CaRainA', source='surface ocean alkalinity', sink='sediments A')
def caraina(t, m):
	return 2e15*mpg
	
@pf_flow(name='CaCO3 dissolutionA', source='sediments A', sink='deep ocean A')
def caco3disolA(t, m):
	return m['CaRainA'] * (1 - m['F preserved'])
	
@pf_flow(name='CirculationA', source='surface ocean alkalinity', sink='deep ocean A', clamp=False)
def circulationA(t, m):
	return (m['ALKsurf'] - m['ALKdeep'])*Mdeep/tau_circulation
	
@pf_flow(name='Business As Usual', sink='Surface ocean C')
def bau(t, m):
	if (t > 1750) and (t < 2075):
		return (5.8e-7*(t - 1750)**3 + 1e-4*(t - 1750)**2 + 9.5e-3*(t - 1750) + 8e-2)*1e15/12
	else:
		return 0.0
		
Is, Fs, Vs = pf_run_model(start=0, stop=5500, step=0.15)

