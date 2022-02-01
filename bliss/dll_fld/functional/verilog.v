//Verilog HDL for "bliss", "dll_fld" "functional"


module dll_fld #(
    parameter NUM_DELAY = 4)
    (el_i, up_o, down_o, lock_o, see_o);

// tmrg default triplicate

input [NUM_DELAY-1:0] el_i;     // output of the early/late detectors
output wire up_o;               // up signal to charge pump
output wire down_o;             // down signal to charge pump
output wire lock_o;             // high for non-harmonic, non-stuck lock acquired
output wire see_o;              // high for SEE detected, i.e. the input from el_i is invalid

// Assigning up = ~el_i[0] | (el_i[0]&~el_i[1]) | (el_i[0]&el_i[1]&~el_i[2])...
reg [(NUM_DELAY>1)-1:0] up_partitions;
always @(*) up_partitions[0] = ~el_i[0];
generate
    genvar g_i;
    for (g_i=1; g_i<(NUM_DELAY>1); g_i=g_i+1) begin
        always @(*) begin
            up_partitions[g_i] = (~el_i[g_i]) & (&el_i[g_i-1:0]);
        end
    end
endgenerate

// Assigning outputs
assign lock_o = ~(up_o | down_o);
assign down_o = &el_i;
assign up_o = |up_partitions;
assign see_o = |((el_i+1) & el_i);

endmodule

