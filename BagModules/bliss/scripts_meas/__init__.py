import numpy as np
from scipy.interpolate import interp1d

from warnings import warn

def get_edge_time(t_vec, data_vec, val_cross, num_edge=0, positive=True) -> float:
	'''
	Inputs:
		t_vec: 1D array of time.
		data_vec: 1D array of data. Should be index-matched to time.
		val_cross: Float. The value that constitutes a rising or falling edge.
		num_edge: Float. The number of the edge whose timing you want. For example,
			if you want the first falling edge, positive=False and num_edge=0.
		positive: Boolean. True if the edge of interest is a rising edge.
	Returns:
		Float. The time (interpolated) of the num_edgeth rising/falling
		(for positive=True/False) edge as it crosses val_cross.
	Raise:
		AssertionError if the requested num_edge is greater than the available number
		of edges or less than 0.
	'''
	edge_count = 0

	# Get lower indices of crossing times
	idx_cross_vec = np.argwhere(np.diff(np.sign(data_vec-val_cross))).flatten()

	# Filter by type of edge
	idx_cross_vec_filtered = [i for i in idx_cross_vec if (data_vec[i+1] > data_vec[i])==positive]

	# Avoid double-counting times when the data hits the target value exactly
	idx_cross_vec_clean = np.array([i for i in idx_cross_vec_filtered \
		if i+1 not in idx_cross_vec_filtered])

	# Raise error if asking for an edge number that doesn't exist
	assert num_edge >= 0 and num_edge < len(idx_cross_vec_filtered), f'Requesting {"rising" if positive else "falling"} edge {num_edge}. Only edges 0 through {len(idx_cross_vec_filtered)} available.'

	# Linearly interpolate to get the time
	idx_cross = idx_cross_vec_clean[num_edge]
	data_interp = interp1d(data_vec[idx_cross:idx_cross+2], t_vec[idx_cross:idx_cross+2])
	t_cross = data_interp(val_cross)

	return t_cross

def calc_td(t_vec, out_vec, num_edge, vlow=0.08, vhigh=0.72, positive=True) -> float:
	'''
	Measures the rise/fall time of the rising/falling edge from vlow to vhigh.
	Inputs:
		t_vec: 
		out_vec:
		num_edge:
		vlow:
		vhigh:
	Returns:
		Float. The rise/fall time (in the same units as t_vec) of rising/falling
		edge of out_vec between vhigh and vlow.
	'''
	t_high 	= get_edge_time(t_vec, out_vec, vhigh, 	num_edge, positive)
	t_low 	= get_edge_time(t_vec, out_vec, vlow, 	num_edge, positive)

	return t_low-t_high if positive else t_high-t_low

def calc_tprop(t_vec, in_vec, out_vec, num_edge, vmid_in, vmid_out, positive=True, inverted=False) -> float:
	'''
	Inputs:
		t_vec: Vector of times.
		in_vec: Vector of input signal values, index matched to t_vec.
		out_vec: Vector of output signal value, index matched to t_vec.
		vmid_in: Float. Voltage used to determine the edge timing of the input.
		vmid_out: Float. Voltage used to determine the edge timing fo the output.
		positive: Boolean. True if measuring an output rising edge, False if measuring
			and output falling edge.
		inverted: Boolean. True if the input and output are inverted relative to one another.
	Returns:
		Float. The propagation delay of the input edge and its corresponding
		output edge, possibly in different voltage domains.
	'''
	tcross_in 	= get_edge_time(t_vec, in_vec,  vmid_in, 	num_edge, positive==(not inverted))
	tcross_out 	= get_edge_time(t_vec, out_vec,	vmid_out, 	num_edge, positive)

	return tcross_out - tcross_in

if __name__ == "__main__":
	data_vec = np.array([0, 0, .5, 1, 1, .75, 0, 1])
	t_vec = range(len(data_vec))
	print(t_vec)
	print(data_vec)
	print(get_edge_time(t_vec, data_vec, 0.75, num_edge=1, positive=True))