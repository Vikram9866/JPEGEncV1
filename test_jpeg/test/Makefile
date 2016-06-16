# for entropy coder

def convert():
    """ block used for converting MyHDL to verilog """
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=True, async=True)

    # input for the entropy coder
    input_value = Signal(intbv(0)[(WIDTH_REG+1):].signed())

    # output for the entropy coder
    size = Signal(intbv(0)[SIZE:])
    amplitude = Signal(intbv(0)[(WIDTH_REG+1):].signed())

    # instantiation of entropy coder
    inst = entropycoder(clock, reset, input_value, size, amplitude)
    inst.convert(hdl='verilog')

    # analysis of converted verilog code
    analyze.simulator = 'iverilog'
    assert entropycoder(
        clock, reset, input_value, size, amplitude).analyze_convert() == 0

if __name__ == '__main__':
    convert()

#rlecore

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
