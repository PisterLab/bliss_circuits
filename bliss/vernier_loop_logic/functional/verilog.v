//Verilog HDL for "bliss", "vernier_loop_logic" "functional"


module vernier_loop_logic #(
	parameter DELAY = 1) (
	input 	wire line_out_i,
	output 	wire mux_loop_o;
);

assign mux_loop_o = #(DELAY) line_out_i;

endmodule
