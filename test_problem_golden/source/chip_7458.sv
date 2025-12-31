module chip_7458 ( 
    input p1a, p1b, p1c, p1d, p1e, p1f,
    output p1y,
    input p2a, p2b, p2c, p2d,
    output p2y );




wire w1, w2, w3, w4;

assign w1 = p1a & p1b & p1c & p1d;
assign w2 = p1e & p1f;
assign w3 = p2a & p2b & p2c & p2d;
assign w4 = p2e & p2f;

assign p1y = w1 | w2;
assign p2y = w3 | w4;

endmodule