from typing import Mapping,Any
from warnings import warn

import os

tb_lib = 'bliss'
tb_cell = 'delay_line_tb_delay'
impl_lib = 'span_ion_testbenches_inst'

data_dir = os.path.join('data', 'bag2_digital', 'delay_line_inv_starved', 'meas')
os.makedirs(data_dir, exist_ok=True)

def get_tb_name():
	return 'zz_delay_line_tb_delay'

def meas(prj, **tb_params) -> Mapping[str,Any]:
	# Generate testbench
	tb_name = get_tb_name()
	fname = os.path.join(data_dir, f'{tb_name}.data')
	if os.path.isfile(fname):
		print(f'File {fname} exists, skipping.')
		return
	print(f'Creating testbench {tb_name}')

	# Generate schematic
	tb_sch = prj.create_design_module(tb_lib, tb_cell)
	tb_sch.design(**tb_params)
	tb_sch.implement_design(impl_lib, top_cell_name=tb_name)
	tb_obj = prj.configure_testbench(impl_lib, tb_name)

	# Update testbench changes and run simulation
	tb_obj.update_testbench()
	print(f'Simulating testbench {tb_name}')
	save_dir = tb_obj.run_simulation()

	# load simulation results into Python
	print('Simulation done, loading results')
	results = load_sim_results(save_dir)

def calc_tf(t_vec, out_vec, vlow=0.08, vhigh=0.72) -> float:
	'''
	Measures the fall time of the falling edge from vhigh to vlow.
	Inputs:
		t_vec:
		out_vec:
		num_edge:
		vlow:
		vhigh:
	Returns:
		Float. The fall time (in the same units as t_vec) of falling
		edge of out_vec from vhigh to vlow.
	'''

def calc_tp_neg(t_vec, in_vec, out_vec, vmid_in, vmid_out, inverted=False):
	'''
	Measures the propagation delay of a falling edge in out_vec 
	from its trigger in in_vec.
	Inputs:
		t_vec:
		in_vec:
		out_vec:
		vmid_in: 
		vmid_out:
		inverted: True if the input and output are inverted relative to one another.
			False if they share the same polarity.
	'''
	in_pos = inverted
	
	# Get the edge time for the input