from pyflowtool import *

# define constants
max_growth_rate = 0.2
n_half_sat = 1000.0
lifespan = 10
decay_timescale = 30
denitr_frac = 0.05
leaching_frac = 0.05
regrowth_time = 50

@pf_setup
def init_model():
	# define inventories
	pf_make_inventory('B', value=30000)
	pf_make_inventory(['S', 'N'], value=[90000, 1000])
	# make displays
	pf_make_display('Inventories', invs=['B', 'S', 'N'], label='Inventories (TgN)')
	
@pf_flow(name='Assimilation', source='N', sink='B')
def assimilation(t, m):
	return max_growth_rate * m['B'] * ( 1 / ( n_half_sat + m['N'] ) ) * m['N']
	
@pf_flow(name='Mortality', source='B', sink='S')
def mortality_flow(t, m):
	return m['B'] / lifespan
	
@pf_flow(name='Mobilization', source='S', sink='N')
def flow_mobil(t, asdf):
	return asdf['S'] / decay_timescale
	
@pf_flow(name='Fixation', source=None, sink='B')
def fixation(t, m):
	return 200
	
@pf_flow(name='Denitrification', source='S')
def denitr(t ,m):
	return m['Mobilization'] * denitr_frac
	
@pf_flow(name='Leaching', source='N')
def leaching(t, m):
	return m['N'] * leaching_frac
	
@pf_flow(name='Clearcutting', source='B')
def clearcut(t, m):
	if (t > 1800) and (t < 1801):
		return m['B'] * 0.5 * 0.1
	else:
		return 0
	
@pf_flow(name='Erosion', source='S')
def erosion(t, m):
	if (t > 1800) and (t < 1800 + regrowth_time):
		return 100 / 0.1
	else:
		return 0
		
@pf_flow(name='Fertilizer', sink='N')
def fertilize(t, m):
	if (t > 1950):
		return 100
	else:
		return 0
	
#actually run the model
Is, Fs, Vs = pf_run_model(start=1700, stop=2000, step=0.1)

