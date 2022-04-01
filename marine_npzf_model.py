from pyflowtool import *

vmax = 1.4
Kn = 1.0
export_fraction_P = 0.01
P_life_expectancy = 7.0
deep_N = 30
renewal_time = 40*365
gammaZ = 0.1
export_fraction_Z = 0.1
Kp = 1
vmaxZ = 1
Z_life_expectancy = 60
Kz = 2
vmaxF = 0.1
gammaF = 0.18
F_life_expectancy = 15*365

@pf_setup
def init():
	pf_make_inventory(['N', 'P', 'Z', 'F'], [0.3, 0.3, 0.1, 0.3])
	pf_make_display('Inventories', invs=['N', 'P', 'Z', 'F'], label='Inventories')
	pf_make_display('N fluxes', fs=['Upwelling', 'exudation', 'recycling, regeneration', 'NPP'])
	pf_make_display('P fluxes', fs=['NPP', 'recycling, regeneration', 'exportF', 'exportP', 'grazing'])
	pf_make_display('Z fluxes', fs=['grazing', 'exudation', 'sinking fecal pellets', 'mortalityZ', 'foraging, predation'])
	pf_make_display('F fluxes', fs=['foraging, predation', 'exportF', 'mortalityF', 'Harvest'])
	pf_make_display('In/Out Fluxes', fs=['Upwelling', 'exportP', 'exportF', 'mortalityZ', 'sinking fecal pellets', 'mortalityF'])
	
@pf_flow(name='NPP', source='N', sink='P')
def npp(t, m):
	return vmax * m['P'] * m['N'] / (Kn + m['N'])
	
@pf_flow(name='recycling, regeneration', source='P', sink='N')
def recyl_regen(t, m):
	return (1 - export_fraction_P) * m['P'] / P_life_expectancy
	
@pf_flow(name='Upwelling', sink='N')
def upwelling(t, m):
	return (deep_N - m['N']) / renewal_time
	
@pf_flow(name='exudation', source='Z', sink='N')
def exudation(t, m):
	return m['grazing'] * (1 - gammaZ) * (1 - export_fraction_Z)
	
@pf_flow(name='grazing', source='P', sink='Z')
def grazing(t, m):
	return vmaxZ * m['Z'] * (m['P'] / (Kp + m['P']))
	
@pf_flow(name='exportP', source='P')
def exportP(t, m):
	return export_fraction_P * m['P'] / P_life_expectancy
	
@pf_flow(name='sinking fecal pellets', source='Z')
def sfp(t, m):
	return m['grazing'] * (1 - gammaZ) * export_fraction_Z
	
@pf_flow(name='mortalityZ', source='Z')
def mortz(t, m):
	return m['Z'] / Z_life_expectancy
	
@pf_flow(name='foraging, predation', source='Z', sink='F')
def fora_pred(t, m):
	return m['F'] * vmaxF * m['Z'] / (Kz + m['Z'])
	
@pf_flow(name='exportF', source='F')
def exportF(t, m):
	return m['foraging, predation'] * (1 - gammaF)
	
@pf_flow(name='mortalityF', source='F')
def mortalityF(t, m):
	return m['F'] / F_life_expectancy
	
@pf_flow(name='Harvest', source='F')
def harvest(t, m):
	if t > 4000:
		return 0.003 / 365
	else:
		return 0
	
Is, Fs, Vs = pf_run_model(start=0, stop=6000, step=0.25)
