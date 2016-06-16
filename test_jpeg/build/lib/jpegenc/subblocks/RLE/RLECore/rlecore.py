""" core of the run length encoder module """

from myhdl import always_comb, always_seq, block
from myhdl import intbv, ResetSignal, Signal
from myhdl.conversion import analyze
from jpegenc.subblocks.RLE.RLECore.entropycoder import entropycoder


WIDTH_RAM_ADDRESS = 6
WIDTH_RAM_DATA = 12
SIZE = 4


class DataStream(object):
    """ Input data streams into Rle Core """
    def __init__(self, width=WIDTH_RAM_DATA):
        self.start = Signal(bool(0))
        self.input_val = Signal(intbv(0)[width:].signed())


class RLESymbols(object):
    """RLE symbols generatred by RLE Core"""
    def __init__(self, width=WIDTH_RAM_DATA, size=SIZE):
        self.runlength = Signal(intbv(0)[size:])
        self.size = Signal(intbv(0)[size:])
        self.amplitude = Signal(intbv(0)[width:].signed())
        self.dovalid = Signal(bool(0))


class RLEConfig(object):
    """RLE configuration Signals are added here"""
    def __init__(self):
        self.color_component = Signal(intbv(0)[3:])
        self.read_addr = Signal(intbv(0)[6:])
        self.sof = Signal(bool(0))


def sub(num1, num2):
    """subtractor for Difference Encoder"""
    return num1 - num2


@block
def rle(reset, clock, datastream, rlesymbols, rleconfig):
    """ Input and start Signal send using datastream
        and rle symbols are captured
    """
    rlesymbols_temp = RLESymbols()

    prev_dc_0, prev_dc_1, prev_dc_2, zrl_di = [Signal(intbv(0)[
        (WIDTH_RAM_DATA):].signed()) for _ in range(4)]

    accumulator = Signal(intbv(0)[(WIDTH_RAM_DATA + 1):].signed())

    read_en, divalid, divalid_en, zrl_proc = [
        Signal(bool(0)) for _ in range(4)]

    zero_cnt, read_cnt = [Signal(intbv(0)[6:]) for _ in range(2)]

    write_cnt = Signal(intbv(0)[7:])

    @always_comb
    def assign():
        """Assign outputs"""
        rlesymbols.size.next = rlesymbols_temp.size
        rlesymbols.amplitude.next = rlesymbols_temp.amplitude
        rleconfig.read_addr.next = read_cnt

    @always_seq(clock.posedge, reset=reset)
    def mainprocessing():
        """main processing"""
        rlesymbols_temp.dovalid.next = 0
        rlesymbols_temp.runlength.next = 0
        rlesymbols.runlength.next = rlesymbols_temp.runlength
        rlesymbols.dovalid.next = rlesymbols_temp.dovalid
        divalid.next = read_en

        if datastream.start == 1:
            read_cnt.next = 0
            read_en.next = 1
            divalid_en.next = 1

        if divalid == 1 and write_cnt == 63:
            divalid_en.next = 0

        if read_en == 1:
            if read_cnt == 63:
                read_cnt.next = 0
                read_en.next = 0
            else:
                read_cnt.next = read_cnt + 1

        if divalid == 1:
            write_cnt.next = write_cnt + 1

            if write_cnt == 0:

                if (rleconfig.color_component == 0) or (
                        rleconfig.color_component == 1):

                    accumulator.next = sub(
                        datastream.input_val.signed(), prev_dc_0)

                    prev_dc_0.next = datastream.input_val.signed()

                elif rleconfig.color_component == 2:
                    accumulator.next = sub(
                        datastream.input_val.signed(), prev_dc_1)

                    prev_dc_1.next = datastream.input_val.signed()

                elif rleconfig.color_component == 3:
                    accumulator.next = sub(
                        datastream.input_val.signed(), prev_dc_2)

                    prev_dc_2.next = datastream.input_val.signed()

                else:
                    pass

                rlesymbols_temp.runlength.next = 0
                rlesymbols_temp.dovalid.next = 1

            else:
                if datastream.input_val.signed() == 0:
                    if write_cnt == 63:
                        accumulator.next = 0
                        rlesymbols_temp.runlength.next = 0
                        rlesymbols_temp.dovalid.next = 1

                    else:
                        zero_cnt.next = zero_cnt + 1

                else:

                    if write_cnt == 63:
                        write_cnt.next = 0

                    if zero_cnt <= 15:
                        accumulator.next = datastream.input_val
                        rlesymbols_temp.runlength.next = zero_cnt
                        zero_cnt.next = 0
                        rlesymbols_temp.dovalid.next = 1

                    else:
                        accumulator.next = 0
                        rlesymbols_temp.runlength.next = 15
                        zero_cnt.next = zero_cnt - 16
                        rlesymbols_temp.dovalid.next = 1

                        zrl_proc.next = 1
                        zrl_di.next = datastream.input_val
                        divalid.next = 0
                        read_cnt.next = read_cnt

        if zrl_proc == 1:
            if zero_cnt <= 15:

                accumulator.next = zrl_di
                rlesymbols_temp.runlength.next = zero_cnt

                if zrl_di.signed() == 0:
                    zero_cnt.next = 1
                else:
                    zero_cnt.next = 0

                rlesymbols_temp.dovalid.next = 1
                divalid.next = divalid_en
                zrl_proc.next = 0

            else:
                accumulator.next = 0
                rlesymbols_temp.runlength.next = 15
                zero_cnt.next = zero_cnt - 16
                rlesymbols_temp.dovalid.next = 1
                divalid.next = 0
                read_cnt.next = read_cnt

        if datastream.start == 1:
            zero_cnt.next = 0
            write_cnt.next = 0

        if rleconfig.sof == 1:
            prev_dc_0.next = 0
            prev_dc_1.next = 0
            prev_dc_2.next = 0

    encoder_inst = entropycoder(
        clock, reset, accumulator, rlesymbols_temp.size, rlesymbols_temp.amplitude)

    return assign, mainprocessing, encoder_inst


def convert():
    """convert to verilog"""
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=1, async=True)

    datastream = DataStream()
    rlesymbols = RLESymbols()
    rleconfig = RLEConfig()

    inst = rle(reset, clock, datastream, rlesymbols, rleconfig)
    inst.convert = 'verilog'

    analyze.simulator = 'iverilog'
    # assert rle(
    #  reset, clock, datastream, rlesymbols, rleconfig).analyze_convert() == 0

if __name__ == '__main__':
    convert()
