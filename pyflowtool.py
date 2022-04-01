import functools
import matplotlib.pyplot as plt
import numpy as np

"""
	TODO
	- use rk4 instead of whatever this mess is
	- add support for variables
	- allow fullnames (for when plotting)
	- allow clamping of flows to positive rates
	- allow clamping of inventories to positive values
"""

# dummy function
def _empty_func():
	return 0.0

# model state infornmation
_m_model = {'flows' : {}, 'inventories' : {}, 'vars' : {}, 'setup' : _empty_func, 'd' : {}}
	
# fixes flow and inventory definitions
def _compile_inputs():
	# make sure all flows have sensible properties
	to_del = []
	for n, f in _m_model['flows'].items():
		# make sure we have at least a source or a sink
		if (f['source'] is not None) and (f['source'] not in _m_model['inventories']):
			print('Warning: Unknown source for flow: ' + n + ' [' + f['source'] + ']')
			f['source'] = None
		if (f['sink'] is not None) and (f['sink'] not in _m_model['inventories']):
			print('Warning: Unknown sink for flow: ' + n + ' [' + f['sink'] + ']')
			f['sink'] = None
		if (f['source'] is None) and (f['sink'] is None):
			print('Warning: Flow has neither source nor sink: ' + n)
			to_del.append(n)
			continue
		# make sure that the flow doesnt share a name with an inventory
		if n in _m_model['inventories']:
			print('Warning: Flow shares name with an inventory: ' + n)
			to_del.append(n)
			continue
		if n in _m_model['vars']:
			print('Warning: Flow shares name with a variable: ' + n)
			to_del.append(n)
			continue
		# make sure we have a valid function
		if (f['f'] is None):
			print('Warning: Flow had missing function: ' + n)
			f['f'] = _empty_func
		# find source and associate with the flow
		if (f['source']):
			_m_model['inventories'][f['source']]['out'].append(n)
		# find sink and associate with the flow
		if (f['sink']):
			_m_model['inventories'][f['sink']]['in'].append(n)
	# delete bad items
	for k in to_del:
		_m_model['flows'].pop(k, None)
	# check variables
	to_del = []
	for n, v in _m_model['vars'].items():
		if n in _m_model['inventories']:
			print('Warning: Variable shares name with an inventory: ' + n)
			to_del.append(n)
			continue
		if n in _m_model['flows']:
			print('Warning: Variable shares name with a flow: ' + n)
			to_del.append(n)
			continue	
	# delete bad items
	for k in to_del:
		_m_model['vars'].pop(k, None)

# initializes the model
def pf_reset_model():
	_m_model = {'flows' : {}, 'inventories' : {}, 'vars' : {}, 'setup' : _empty_func, 'd' : {}}
	
# makes the value dicts for the model
def _make_model_dict(itr, Is, Fs, Vs):
	model = {}
	for n, i in _m_model['inventories'].items():
		model[n] = Is[n][itr]
	for n, f in _m_model['flows'].items():
		model[n] = Fs[n][itr]
	for n, v in _m_model['vars'].items():
		model[n] = Vs[n][itr]
	return model

def pf_make_display(name : str, invs=[], fs=[], vs=[], label=None):
	# check if name is already a display
	if name in _m_model['d']:
		raise ValueError('Display names must be unique!')
	# make sure invs and fs and vs are both lists
	if type(invs) is not list:
		raise ValueError('invs must be a list')
	if type(fs) is not list:
		raise ValueError('fs must be a list')
	if type(vs) is not list:
		raise ValueError('vs must be a list')
	# make sure all inv names are strs
	for i in invs:
		if type(i) is not str:
			raise ValueError('All elements of invs must be a string')
	# make sure all f names are strs
	for i in fs:
		if type(i) is not str:
			raise ValueError('All elements of fs must be a string')
	# make sure all vs names are strs
	for i in vs:
		if type(i) is not str:
			raise ValueError('All elements of vs must be a string')
	# make sure label is a string
	if label is not None:
		if type(label) is not str:
			raise ValueError('label must be a string')
	# make sure that the displau actually displays something
	if (invs is None) and (fs is None):
		return
	# save display 
	# TODO: impl variables for display
	_m_model['d'][name] = {'is' : invs, 'fs' : fs, 'vs' : vs, 'label' : label}
	
# makes and shows all registered displays
def _display_results(Is, Fs, Vs):
	for n, d in _m_model['d'].items():
		plt.title(n)
		for f in d['fs']:
			if f not in Fs:
				print('Warning: Invalid flux for display: ' + n + ' (' + f + ')')
				continue
			plt.plot(Fs[f], label=f)
		for i in d['is']:
			if i not in Is:
				print('Warning: Invalid inventory for display: ' + n + ' (' + i + ')')
				continue
			plt.plot(Is[i], label=i)
		for v in d['vs']:
			if v not in Vs:
				print('Warning: Invalid variable for display: ' + n + ' (' + v + ')')
				continue
			plt.plot(Vs[v], label=v)
		if d['label'] is not None:
			plt.ylabel(d['label'])
		plt.xlabel('Time')
		plt.legend()
		plt.show()
	
# runs the model
def pf_run_model(start=0, stop=10, step=1):
	# call the setup function
	_m_model['setup']()
	# validate model
	_compile_inputs()
	# calculate size
	N = int((stop - start) / step) + 1
	# make arrays
	Is = {}; Fs = {}; Vs = {}
	for n, i in _m_model['inventories'].items():
		Is[n] = np.full((N,), i['value'], dtype=np.float64)
	for n, f in _m_model['flows'].items():
		Fs[n] = np.full((N,), 0.0, dtype=np.float64)
	for n, v in _m_model['vars'].items():
		Vs[n] = np.full((N,), 0.0, dtype=np.float64)
	# run adaptive rk4
	for T in range(N - 1):
		t = start + T * step # actual time
		# prepare properties dict
		model = _make_model_dict(T, Is, Fs, Vs)
		# calculate variables
		for n, v in _m_model['vars'].items():
			# TODO: make sure this runs in the "dependency" order...
			r = v(t, model)
			Vs[n][T + 1] = r
			model[n] = r
		# add time to the model
		# calculate all Fs
		results = {}
		for n, f in _m_model['flows'].items():
			r = f['f'](t, model)
			if r is None:
				r = 0
			results[n] = r
			Fs[n][T + 1] = results[n]
		# compute fluxes for each inventory
		for n, i in _m_model['inventories'].items():
			dI = 0.0
			# find all out
			for f in i['out']:
				dI -= results[f]
			# find all in
			for f in i['in']:
				dI += results[f]
			Is[n][T + 1] = Is[n][T] + dI * step
	# handle displays
	_display_results(Is, Fs, Vs)
	#return data
	return Is, Fs, Vs
			
def _build_inven(name : str, nickname=None, value=0.0):
	# make sure nickname is a string or none
	if nickname:
		if type(nickname) is not str:
			raise ValueError('Nickname must be a string!')
	# check if inventory exists
	if name in _m_model['inventories']:
		raise ValueError('Duplicate inventory: ' + name)
	else:
		_m_model['inventories'][name] = {'name' : name, 
																		 'nickname' : nickname,
																		 'value' : value,
																		 'out' : [],
																		 'in' : []}

# instantiates an inventory
def pf_make_inventory(name, value=0.0, nickname=None):
	if (type(name) is list):
		if (type(value) is not list):
			raise ValueError('If name is of type list, value must also be of type list')
		if (len(value) is not len(name)):
			raise ValueError('name and value must have same length')
		for i, n in enumerate(name):
			if type(n) is not str:
				raise ValueError('name must be either string or list of strings.')
			_build_inven(n, nickname=nickname, value=value[i])
	elif type(name) is str:
		_build_inven(name, nickname=nickname, value=value)

# flow builder helper function
def _build_flow(func, name=None, source=None, sink=None):
	# make sure we actually got a name
	if name is None:
		raise ValueError('Missing name parameter for flow definition!')
	# make sure source and sink are both strings
	if source is not None:
		if type(source) is not str:
			raise ValueError('Source must be a string!')
	if sink is not None:
		if type(sink) is not str:
			raise ValueError('Sink must be a string!')
	# save function to dictionary
	if name in _m_model['flows']:
		# check that sources and sinks are the same
		if _m_model['flows'][name]['source'] is not source:
			raise ValueError('Warning: Conflicting source for flow: ' + source + \
				'got ' + source + ' but expected ' + _m_model['flows'][name]['source'])
		if _m_model['flows'][name]['sink'] is not sink:
			raise ValueError('Warning: Conflicting sink for flow: ' + sink + \
				'got ' + sink + ' but expected ' + _m_model['flows'][name]['sink'])
		# since were still here, add the function
		_m_model['flows'][name]['f'] = func
	else:
		# new flow defined, add it
		_m_model['flows'][name] = {'name' : name, 
															 'source' : source, 
															 'sink' : sink, 
															 'f' : func}

# decorator for handling flows
def pf_flow(name=None, source=None, sink=None, clamp=True):
	# return the original function
	def decorator(func):
		_build_flow(func, name=name, source=source, sink=sink)
		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			return func(*args, **kwargs)
		return wrapper
	return decorator
	
def _build_var(func, name):
	if func is None:
		raise ValueError('Function can not be None for variable declaration')
	if name is None:
		raise ValueError('Missing name parameter for variable declaration')
	if name in _m_model['vars']:
		raise ValueError('Redeclaration of variable')
	_m_model['vars'][name] = func
	
def pf_var(name=None):
	# return the original function
	def decorator(func):
		_build_var(func, name)
		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			return func(*args, **kwargs)
		return wrapper
	return decorator
	
# decorator for setup
def pf_setup(_func):
	_m_model['setup'] = _func
	
