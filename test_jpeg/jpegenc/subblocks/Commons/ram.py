from myhdl import always_comb, always_seq, block
from myhdl import intbv, ResetSignal, Signal
from myhdl.conversion import analyze

# Data width and Address width

RAM_ADDRESS_WIDTH = 7
RAM_DATA_WIDTH = 12
MEM_WIDTH = 2**7


class RamPorts(object):
    def __init__(self, data_width=RAM_DATA_WIDTH, addr_width=RAM_ADDRESS_WIDTH):
        self.data_in = Signal(intbv(0)[data_width:])
        self.write_addr = Signal(intbv(0)[addr_width:])
        self.read_addr = Signal(intbv(0)[addr_width:])
        self.write_enable = Signal(bool(0))
        self.data_out = Signal(intbv(0)[data_width:])


@block
def ram(clock, reset, ramports):

    mem_array = [Signal(intbv(0)[RAM_DATA_WIDTH:]) for _ in range(MEM_WIDTH)]
    read_addr_temp = Signal(intbv(0)[RAM_ADDRESS_WIDTH:])

    @always_comb
    def ram_out():
        ramports.data_out.next = mem_array[int(read_addr_temp)]

    @always_seq(clock.posedge, reset=reset)
    def write_logic():
        if ramports.write_enable == 1:
            mem_array[int(
                ramports.write_addr)].next = ramports.data_in

    @always_seq(clock.posedge, reset=reset)
    def read_logic():
        read_addr_temp.next = ramports.read_addr

    return ram_out, write_logic, read_logic


def convert():

    clock = Signal(bool(0))
    reset = ResetSignal(0, active=1, async=True)
    ramports = RamPorts()

    inst = ram(clock, reset, ramports)
    inst.convert = 'verilog'
    analyze.simulator = 'iverilog'

    # assert ram(clock, reset, ramports).analyze_convert() == 0

if __name__ == '__main__':
    convert()
