from typing import Mapping,Any
from warnings import warn
from pprint import pprint

from bliss_circuits.BagModules.bliss.scripts_meas import *

import os, sys, pdb, traceback
from bag.core import BagProject
from bag.io import load_sim_results, save_sim_results, load_sim_file

tb_lib = 'bliss'
tb_cell = 'delay_line_tb_delay'
impl_lib = 'span_ion_testbenches_inst'

data_dir = os.path.join('data', 'bag2_digital', 'delay_line_inv_starved', 'meas')
os.makedirs(data_dir, exist_ok=True)

def get_tb_name():
	return 'zz_delay_line_tb_delay'

def meas(prj, tb_params, vmid_in_r, vmid_out_r, vmid_in_f, vmid_out_f):
	meas_inv = tb_params['dut_params']['export_outb']

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

	# Set testbench parameters
	param_map = dict(CLOAD=tb_params['cload'],
		VN=tb_params['vn'],
		VP=tb_params['vp'],
		VDD=tb_params['vdd'],
		VSS=tb_params['vss'],
		VLOW=tb_params['vlow'],
		VHIGH=tb_params['vhigh'],
		TPER=tb_params['tper'],
		TSTOP=tb_params['tstop'])
	for var,val in param_map.items():
		tb_obj.set_parameter(var, val)

	# Update testbench changes and run simulation
	tb_obj.update_testbench()
	print(f'Simulating testbench {tb_name}')
	save_dir = tb_obj.run_simulation()

	# Load simulation results into Python
	print('Simulation done, loading results')
	results = load_sim_results(save_dir)

	# Return total propagation time from the input to the output(s)
	tprop_dict = dict()
	t_vec 		= results['time']
	in_vec 		= results['tran_in']

	out_vec 	= results['tran_out']
	tprop_r_out = calc_tprop(t_vec, in_vec, out_vec, 1, vmid_in_r, vmid_out_r, positive=True, inverted=False)
	tprop_f_out = calc_tprop(t_vec, in_vec, out_vec, 1, vmid_in_f, vmid_out_f, positive=False, inverted=False)
	tprop_dict['out_rise'] = tprop_r_out
	tprop_dict['out_fall'] = tprop_f_out

	if meas_inv:
		outb_vec 	= results['tran_outb']
		tprop_r_outb = calc_tprop(t_vec, in_vec, outb_vec, 1, vmid_in_f, vmid_out_r, positive=True, inverted=True)
		tprop_f_outb = calc_tprop(t_vec, in_vec, outb_vec, 1, vmid_in_r, vmid_out_f, positive=False, inverted=True)
		tprop_dict['outb_rise'] = tprop_r_outb
		tprop_dict['outb_fall'] = tprop_f_outb

	return tprop_dict

def run_main(bprj):
	# Testbench parameters
	vdd = 1.8
	tper = 1e-6

	tb_params = dict(cload=0,
		vn=vdd,
		vp=0,
		vdd=vdd,
		vss=0,
		vlow=vdd*0.1,
		vhigh=vdd*0.8,
		tper=1e-6,
		tstop=tper*10)

	# DUT parameters
	num_inv = 4
	export_outb = False
	nstack_params = dict(stack=2,
		lch_list=[500e-9, 500e-9],
		w_list=[500e-9, 500e-9],
		intent_list=['svt', 'svt'],
		seg_list=[1, 2],
		export_mid=False)
	pstack_params = dict(stack=2,
		lch_list=[500e-9, 500e-9],
		w_list=[500e-9, 500e-9],
		intent_list=['svt', 'svt'],
		seg_list=[1, 2],
		export_mid=False)

	dut_params = dict(num_inv=num_inv,
		export_outb=export_outb,
		inv_tristate_params=dict(nstack_params=nstack_params,
								pstack_params=pstack_params))
	tb_params['dut_params'] = dut_params

	pprint(meas(prj=bprj,
		tb_params=tb_params,
		vmid_in_r=vdd/3,
		vmid_out_r=vdd/3,
		vmid_in_f=vdd*2/3,
		vmid_out_f=vdd*2/3))

if __name__ == '__main__':
	local_dict = locals()
	if 'bprj' not in local_dict:
		print('Creating BAG project')
		bprj = BagProject()
	else:
		print('Loading BAG project')
		bprj = local_dict['bprj']

	try:
		run_main(bprj)
	except:
		extype, value, tb = sys.exc_info()
		traceback.print_exc()
		pdb.post_mortem(tb)