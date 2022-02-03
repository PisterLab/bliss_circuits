//Verilog HDL for "bliss", "dll_lock_sel" "functional"


module dll_lock_sel (
	input up_pfd_i,		// UP from PFD
	input down_pfd_i,	// DOWN from PFD
	input up_fld_i,		// UP from false lock detector (for edge cases)
	input down_fld_i,	// DOWN from false lock detector (for edge cases)
	input lock_fld_i,	// ~(up_fld+down_fld)
	input el_validb_i,	// 1=input from early-late detectors invalid

	output reg up_o,
	output reg down_o
);

always @(*) begin
	if (el_validb_i) begin
		up_o = 1'b0;
		down_o = 1'b0;
	end else begin
		up_o = lock_fld_i ? up_pfd_i : up_fld_i;
		down_o = lock_fld_i ? down_pfd_i : down_fld_i;
	end
end

endmodule
