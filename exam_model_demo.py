from pyflowtool import *

constant_flux = 2
timescale = 10
rate_constant = 0.5

@pf_setup
def init():
	pf_make_inventory('System 1', value=0)
	pf_make_inventory('System 2', value=150)
	pf_make_display('Fluxes', fs=['Losses', 'New input', 'Process 1', 'Process 2'])
	pf_make_display('Inventories', invs=['System 1', 'System 2'])
	
@pf_flow(name='New input', sink='System 1')
def newin(t, m):
	return 100
	
@pf_flow(name='Process 1', source='System 2', sink='System 1')
def proc1(t, m):
	return constant_flux
	
@pf_flow(name='Process 2', source='System 1', sink='System 2')
def proc2(t, m):
	return m['System 1'] / timescale
	
@pf_flow(name='Losses', source='System 2')
def losses(t, m):
	return m['System 2'] * rate_constant
	
pf_run_model(start=0, stop=30, step=0.1)
