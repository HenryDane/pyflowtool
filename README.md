# Py Flow Tool

Provides a simple framework for simulating flows between abstract containers using python. Written as practice for using Python's decorator syntax.

Define an inventory with:
```python
pf_make_inventory(name)
```
Define a flow with:
```python
@pf_flow(name='Flow Name', source='Inventory 1', sink='Inventory 2')
def function(t, m):
	return m['Inventory 1'] / some_constant
```
Define a display with:
```python
pf_make_display('Name', invs=['Inventory 1', 'Inventory 2'], fs=['Flow Name'])
```

Still currently under development. Inspired by the Insight Maker tool and Prof Hain's ESCI100A class in W2022. 

Requires `matplotlib`, `numpy`, and `functools`
