//Verilog HDL for "bliss", "vernier_loop_logic" "functional"


module vernier_loop_logic #(
	parameter B_COUNT) (
	input 	wire line_out_i,
	input 	wire rst,
	output 	wire mux_loop_o,
	output 	reg [B_COUNT-1:0] loop_count_o,
);

always @(posedge rst) begin
	mux_loop_o = 1'b0;
	loop_count_o = 0;
end

always @(line_out_i) begin
	loop_count_o <= loop_count_o + 1;
end

always @(posedge line_out_i) begin
	mux_loop_o = 1'b1;
end

endmodule
