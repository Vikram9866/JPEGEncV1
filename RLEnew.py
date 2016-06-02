from myhdl import always_comb, always_seq, block, delay
from myhdl import instance, intbv, ResetSignal, Signal
from EntropyCoder import entropycoder
from myhdl.conversion import analyze


WIDTH_RAM_ADDRESS = 6
WIDTH_RAM_DATA = 12
SIZE = 4


def sub(a, b):
    return (a - b)



@block
def rle(reset, clock, di, start, sof, color_component, 
        runlength, size, amplitude, dovalid, read_addr):

    prev_dc_0, prev_dc_1, prev_dc_2, zrl_di = [
                            Signal(intbv(0)[WIDTH_RAM_DATA:].signed()) for _ in range(4)]

    accumulator, amplitude_temp = [
                            Signal(intbv(0)[(WIDTH_RAM_DATA + 1):].signed()) for _ in range(2)]

    size_temp, runlength_temp = [
                            Signal(intbv(0)[SIZE:]) for _ in range(2)]

    dovalid_temp, read_en, divalid, divalid_en, zrl_proc = [
                            Signal(bool(0)) for _ in range(5)]

    zero_cnt, read_cnt = [Signal(intbv(0)[6:]) for _ in range(2)]
    write_cnt = Signal(intbv(0)[7:])
    

    @always_comb
    def assign():   
        size.next = size_temp
        amplitude.next = amplitude_temp
        read_addr.next = read_cnt
    
   

    @always_seq(clock.posedge, reset = reset)
    def mainprocessing():

        dovalid_temp.next = 0
        runlength_temp.next = 0
        runlength.next = runlength_temp
        dovalid.next = dovalid_temp
        divalid.next = read_en
        
        if start == 1:
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
                
                if (color_component == 0) or (color_component == 1):
                    accumulator.next = sub(di.signed(), prev_dc_0)
                    prev_dc_0.next = di.signed()        
                
                elif color_component == 2:
                    accumulator.next =  sub(di.signed(), prev_dc_1)
                    prev_dc_1.next = di.signed()        
                
                elif color_component == 3:
                    accumulator.next =  sub(di.signed(), prev_dc_2)
                    prev_dc_2.next = di.signed() 
                
                else:
                    pass
            

                runlength_temp.next = 0
                dovalid_temp.next = 1
           

            else :
                
                if di.signed() == 0:
                    if write_cnt == 63:
                        accumulator.next = 0
                        runlength_temp.next = 0
                        dovalid_temp.next = 1

                    else:
                        zero_cnt.next = zero_cnt + 1
            
                else:

                    if write_cnt == 63:
                        write_cnt.next = 0

                    if zero_cnt <= 15:
                        accumulator.next = di
                        runlength_temp.next = zero_cnt
                        zero_cnt.next = 0
                        dovalid_temp.next = 1

                    else:
                        accumulator.next = 0 
                        runlength_temp.next = 15 
                        zero_cnt.next = zero_cnt - 16
                        dovalid_temp.next = 1
                        
                        zrl_proc.next = 1
                        zrl_di.next = di
                        divalid.next = 0
                        read_cnt.next = read_cnt


        if zrl_proc == 1:
            if zero_cnt <= 15:
                
                accumulator.next = zrl_di
                runlength_temp.next = zero_cnt

                if zrl_di.signed() == 0:
                    zero_cnt.next = 1
                else:
                    zero_cnt.next = 0

                dovalid_temp.next = 1
                divalid.next = divalid_en
                zrl_proc.next = 0

            else:
                accumulator.next = 0 
                runlength_temp.next = 15 
                zero_cnt.next = zero_cnt - 16
                dovalid_temp.next = 1
                divalid.next = 0
                read_cnt.next = read_cnt

        if start == 1:
            zero_cnt.next = 0
            write_cnt.next = 0

        if sof == 1:
            prev_dc_0.next = 0 
            prev_dc_1.next = 0
            prev_dc_2.next = 0

    encoder_inst = entropycoder(clock, reset, accumulator, size_temp, amplitude_temp)



    return assign, mainprocessing, encoder_inst





def convert():

    clock = Signal(bool(0))
    reset = ResetSignal(0, active=1, async=True)

    
    di = Signal(intbv(0)[WIDTH_RAM_DATA:])
    start = Signal(bool(0))
    color_component = Signal(intbv(0)[3:])


    runlength = Signal(intbv(0)[4:])
    size = Signal(intbv(0)[4:])
    amplitude = Signal(intbv(0)[WIDTH_RAM_DATA:])
    
    dovalid = Signal(bool(0))
    sof = Signal(bool(0))

    read_addr = Signal(intbv(0)[6:])
    wr_addr = Signal(intbv(0)[7:])

    inst = rle(reset, clock, di, start, sof, color_component, 
        runlength, size, amplitude, dovalid, read_addr)
   
    analyze.simulator = 'iverilog'
    assert rle(reset, clock, di, start, sof, color_component, 
        runlength, size, amplitude, dovalid, read_addr).analyze_convert() == 0

if __name__ == '__main__':
    convert()
