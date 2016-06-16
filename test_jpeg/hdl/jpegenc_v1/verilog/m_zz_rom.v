// File: m_zz_rom.v
// Generated by MyHDL 0.9dev
// Date: Sat Dec  6 21:22:28 2014


`timescale 1ns/10ps

module m_zz_rom (
    rd_addr,
    zz_rd_addr
);


input [5:0] rd_addr;
output [5:0] zz_rd_addr;
reg [5:0] zz_rd_addr;






always @(rd_addr) begin: M_ZZ_ROM_RTL
    case (rd_addr)
        0: zz_rd_addr = 0;
        1: zz_rd_addr = 1;
        2: zz_rd_addr = 8;
        3: zz_rd_addr = 16;
        4: zz_rd_addr = 9;
        5: zz_rd_addr = 2;
        6: zz_rd_addr = 3;
        7: zz_rd_addr = 10;
        8: zz_rd_addr = 17;
        9: zz_rd_addr = 24;
        10: zz_rd_addr = 32;
        11: zz_rd_addr = 25;
        12: zz_rd_addr = 18;
        13: zz_rd_addr = 11;
        14: zz_rd_addr = 4;
        15: zz_rd_addr = 5;
        16: zz_rd_addr = 12;
        17: zz_rd_addr = 19;
        18: zz_rd_addr = 26;
        19: zz_rd_addr = 33;
        20: zz_rd_addr = 40;
        21: zz_rd_addr = 48;
        22: zz_rd_addr = 41;
        23: zz_rd_addr = 34;
        24: zz_rd_addr = 27;
        25: zz_rd_addr = 20;
        26: zz_rd_addr = 13;
        27: zz_rd_addr = 6;
        28: zz_rd_addr = 7;
        29: zz_rd_addr = 14;
        30: zz_rd_addr = 21;
        31: zz_rd_addr = 28;
        32: zz_rd_addr = 35;
        33: zz_rd_addr = 42;
        34: zz_rd_addr = 49;
        35: zz_rd_addr = 56;
        36: zz_rd_addr = 57;
        37: zz_rd_addr = 50;
        38: zz_rd_addr = 43;
        39: zz_rd_addr = 36;
        40: zz_rd_addr = 29;
        41: zz_rd_addr = 22;
        42: zz_rd_addr = 15;
        43: zz_rd_addr = 23;
        44: zz_rd_addr = 30;
        45: zz_rd_addr = 37;
        46: zz_rd_addr = 44;
        47: zz_rd_addr = 51;
        48: zz_rd_addr = 58;
        49: zz_rd_addr = 59;
        50: zz_rd_addr = 52;
        51: zz_rd_addr = 45;
        52: zz_rd_addr = 38;
        53: zz_rd_addr = 31;
        54: zz_rd_addr = 39;
        55: zz_rd_addr = 46;
        56: zz_rd_addr = 53;
        57: zz_rd_addr = 60;
        58: zz_rd_addr = 61;
        59: zz_rd_addr = 54;
        60: zz_rd_addr = 47;
        61: zz_rd_addr = 55;
        62: zz_rd_addr = 62;
        default: zz_rd_addr = 63;
    endcase
end

endmodule
