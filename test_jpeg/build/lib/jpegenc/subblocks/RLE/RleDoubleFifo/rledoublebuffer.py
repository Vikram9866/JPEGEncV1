'''
The above module is a double buffer
to store runlength encoded outputs
'''

from myhdl import always_comb, always_seq, block
from myhdl import intbv, ResetSignal, Signal
from rhea import *
from rhea.cores.fifo.fifo_sync import fifo_sync

from rhea.system import FIFOBus
from myhdl.conversion import analyze

DEPTH = 64
WIDTH = 20

class DoubleFifoBus(object):
    """
        data_in        : input for double fifo
        write_enable   : write access to double fifo
        buffer_sel     : select a buffer
        read_req       : request to read fifo
        fifo_empty     : asserts if fifo is emtpy
        data_out       : data at the output port of fifo
    """
    def __init__(self, width=WIDTH):
        self.data_in = Signal(intbv(0)[width:])
        self.write_enable = Signal(bool(0))
        self.buffer_sel = Signal(bool(0))
        self.read_req = Signal(bool(0))
        self.fifo_empty = Signal(bool(1))
        self.data_out = Signal(intbv()[width:])


@block
def rledoublefifo(reset, clock, dfifo_bus):
    """double fifo core function"""

    fifo_data_in = Signal(intbv(0)[WIDTH:])

    fbus1 = FIFOBus(width=WIDTH, size=DEPTH)
    fbus2 = FIFOBus(width=WIDTH, size=DEPTH)

    fifo_sync1 = fifo_sync(clock, reset, fbus1)
    fifo_sync2 = fifo_sync(clock, reset, fbus2)

    @always_comb
    def assign():
        """write into fifo bus"""
        fbus1.write_data.next = fifo_data_in
        fbus2.write_data.next = fifo_data_in

    @always_seq(clock.posedge, reset=reset)
    def mux2_logic():
        """select which buffer to enable"""
        if dfifo_bus.buffer_sel == 0:
            fbus1.write.next = dfifo_bus.write_enable
        else:
            fbus2.write.next = dfifo_bus.write_enable

        fifo_data_in.next = dfifo_bus.data_in

    @always_comb
    def logic():
        """read or write into buffer"""
        fbus1.read.next = dfifo_bus.read_req if (
            dfifo_bus.buffer_sel == 1) else 0

        fbus2.read.next = dfifo_bus.read_req if (
            dfifo_bus.buffer_sel == 0) else 0

        dfifo_bus.data_out.next = fbus1.read_data if (
            dfifo_bus.buffer_sel == 1) else fbus2.read_data

        dfifo_bus.fifo_empty.next = fbus1.empty if (
            dfifo_bus.buffer_sel == 1) else fbus2.empty

    return (
        fifo_sync1, fifo_sync2, assign, mux2_logic, logic)


def convert():
    """conversion into verilog"""
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=1, async=True)
    dfifo_bus = DoubleFifoBus()
    inst = rledoublefifo(reset, clock, dfifo_bus)
    inst.convert = 'verilog'

    analyze.simulator = 'iverilog'
    assert rledoublefifo(reset, clock, dfifo_bus).analyze_convert() == 0


if __name__ == '__main__':
    convert()
