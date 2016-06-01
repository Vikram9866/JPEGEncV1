from myhdl import *
from commons import *

RAMADDR_W = 6
RAMDATA_W = 12
SIZE_REG_C = 4
ZEROS_32_C = intbv(0)[32:]


def rle(reset,clk,di,start_pb,sof,rss_cmp_idx,runlength,size,amplitude,dovalid,rd_addr):
   
    prev_dc_reg_0 = Signal(intbv(0)[RAMDATA_W:].signed())
    prev_dc_reg_1 = Signal(intbv(0)[RAMDATA_W:].signed())
    prev_dc_reg_2 = Signal(intbv(0)[RAMDATA_W:].signed())
    prev_dc_reg_3 = Signal(intbv(0)[RAMDATA_W:].signed())
    acc_reg = Signal(intbv(0)[(RAMDATA_W + 1):].signed())
    size_reg = Signal(intbv(0)[SIZE_REG_C:])
    ampli_vli_reg = Signal(intbv(0)[(RAMDATA_W + 1):].signed())
    runlength_reg = Signal(intbv(0)[4:])
    dovalid_reg = Signal(bool(0)) #bool
    zero_cnt = Signal(intbv(0)[6:])
    wr_cnt_d1 = Signal(intbv(0)[6:])
    wr_cnt = Signal(intbv(0)[6:])
    rd_cnt = Signal(intbv(0)[6:])
    rd_en = Signal(bool(0))
    divalid = Signal(bool(0))
    divalid_en = Signal(bool(0))
    zrl_proc = Signal(bool(0))
    zrl_di = Signal(intbv(0)[RAMDATA_W:])


    @always_comb
    def assign():
        size.next = size_reg
        amplitude.next = ampli_vli_reg[11:0]
        rd_addr.next = rd_cnt    

   

    @always_seq(clk.posedge,reset = reset)
    #main processing
    def mainprocessing():
        dovalid_reg.next = 0
        runlength_reg.next = 0
        wr_cnt_d1.next = wr_cnt
        runlength.next = runlength_reg
        dovalid.next = dovalid_reg
        divalid.next = rd_en
        if start_pb == 1:
            rd_cnt.next = 0
            rd_en.next = 1
            divalid_en.next = 1

        if divalid == 1 and wr_cnt == 63:
            divalid_en.next = 0 

        #input read enable
        if rd_en == 1:
            if rd_cnt == 63:
                rd_cnt.next = 0
                rd_en.next = 0
            else:
                rd_cnt.next = rd_cnt + 1

        #input data valid
        if divalid == 1:
            wr_cnt.next = wr_cnt + 1
            #first dct coefficient received , DC data
            if wr_cnt == 0:
                #differential coding of DC Data per component
                if (rss_cmp_idx == 0) or (rss_cmp_idx == 1):
                    acc_reg.next =  (di[0:RAMDATA_W].signed()) - (prev_dc_reg_0[0:RAMDATA_W])
                    prev_dc_reg_0.next = di.signed()

                if rss_cmp_idx == 2:
                    acc_reg.next =  di[0:RAMDATA_W].signed() - prev_dc_reg_1[0:RAMDATA_W] 
                    prev_dc_reg_1.next = di.signed()                  

                if rss_cmp_idx == 3:
                    acc_reg.next =  di[0:RAMDATA_W].signed() - prev_dc_reg_2[0:RAMDATA_W]
                    prev_dc_reg_2.next = di.signed()


                else:
                    pass

                #small fsm here

                runlength_reg.next = 0
                dovalid_reg.next = 0
            #AC Coefficients

            else :
                #Zero AC
                if di.signed() == 0:
                    #EOB
                    if wr_cnt == 63:
                        acc_reg.next = 0
                        runlength_reg.next = 0
                        dovalid_reg.next = 0
                    #no EOB

                    else:
                        zero_cnt.next = zero_cnt + 1

                #Non Zero AC
                else:
                    #Normal RLE Case
                    if zero_cnt <= 15:
                        # @todo: verify?  
                        #acc_reg <= RESIZE(SIGNED(di),RAMDATA_W+1)
                        acc_reg.next = di[0:RAMDATA_W].signed()
                        runlength_reg.next = zero_cnt[0:3] #check if it works
                        zero_cnt.next = 0
                        dovalid_reg.next = 1

                    #Zero count > 15
                    else:
                        #generate ZRL
                        acc_reg.next = 0 #check it later
                        runlength_reg.next = 15 #check it later
                        zero_cnt.next = zero_cnt - 16
                        dovalid_reg.next = 1
                        #stall input until ZRL is handled
                        zrl_proc.next = 1
                        zrl_di.next = di
                        divalid.next = 0
                        rd_cnt.next = rd_cnt

        #ZRL Processing
        if zrl_proc == 1:
            if zero_cnt <= 15:
                #@todo: verify
                #acc_reg <= RESIZE(SIGNED(zrl_di),RAMDATA_W+1);
                acc_reg.next = zrl_di[0:RAMDATA_W].signed() #check it later
                runlength_reg.next = zero_cnt[0:3] #check this out

                if zrl_di.signed() == 0:
                    #zero_cnt = to_unsigned(1,zero_cnt'length);
                    zero_cnt.next = 1
                else:
                    zero_cnt.next = 0

                dovalid_reg.next = 1
                divalid.next = divalid_en
                #continue input handling
                zrl_proc.next = 0

            else:
                #generate ZRL
                acc_reg.next = 0 #check it later
                runlength_reg.next = 15 #check it later
                zero_cnt.next = zero_cnt - 16
                dovalid_reg.next = 1
                divalid.next = 0
                rd_cnt.next = rd_cnt

        #start of 8x8 block processing
        if start_pb == 1:
            zero_cnt.next = 0
            wr_cnt.next = 0

        if sof == 1:
            prev_dc_reg_0.next = 0 #check them all
            prev_dc_reg_1.next = 0
            prev_dc_reg_2.next = 0
            prev_dc_reg_3.next = 0


    
    #Entropy coder
    @always_seq(clk.posedge,reset = reset)
    def entropycoder():
        #perform VLI (Variable Length integer) encoding for symbol-2 (Amplitude)
        #positive input
        if acc_reg >= 0:
            ampli_vli_reg.next = acc_reg
        else:
            ampli_vli_reg.next = acc_reg - 1

        #compute Symbol-1 Size
        #Clog2 implementation

        if acc_reg == -1:
            size_reg.next = 1

        elif (acc_reg < -1) and (acc_reg > -4):
            size_reg.next = 2

        elif (acc_reg < -3) and (acc_reg > -8):
            size_reg.next = 3

        elif (acc_reg < -7) and (acc_reg > -16):
            size_reg.next = 4

        elif (acc_reg < -15) and (acc_reg > -32):
            size_reg.next = 5

        elif (acc_reg < -31) and (acc_reg > -64):
            size_reg.next = 6

        elif (acc_reg < -63) and (acc_reg > -128):
            size_reg.next = 7

        elif (acc_reg < -127) and (acc_reg > -256):
            size_reg.next = 8

        elif (acc_reg < -255) and (acc_reg > -512):
            size_reg.next = 9

        elif (acc_reg < -511) and (acc_reg > -1024):
            size_reg.next = 10

        elif (acc_reg < -1023) and (acc_reg > -2048):
            size_reg.next = 11

        # compute Symbol-1 Size
        # positive input
        # simple clog2


        if acc_reg == 1:
            size_reg.next = 1

        elif (acc_reg < 1) and (acc_reg > 4):
            size_reg.next = 2

        elif (acc_reg < 3) and (acc_reg > 8):
            size_reg.next = 3

        elif (acc_reg < 7) and (acc_reg > 16):
            size_reg.next = 4

        elif (acc_reg < 15) and (acc_reg > 32):
            size_reg.next = 5

        elif (acc_reg < 31) and (acc_reg > 64):
            size_reg.next = 6

        elif (acc_reg < 63) and (acc_reg > 128):
            size_reg.next = 7

        elif (acc_reg < 127) and (acc_reg > 256):
            size_reg.next = 8

        elif (acc_reg < 255) and (acc_reg > 512):
            size_reg.next = 9

        elif (acc_reg < 511) and (acc_reg > 1024):
            size_reg.next = 10

        elif (acc_reg < 1023) and (acc_reg > 2048):
            size_reg.next = 11

        #DC coefficient amplitude=0 case OR EOB
        if acc_reg == 0:
            size_reg.next = 0

    return assign, entropycoder, mainprocessing


clk = Signal(bool(0))
reset = ResetSignal(1, active=ACTIVE_LOW, async=True)
di = Signal(intbv(0)[RAMDATA_W:])
start_pb = Signal(bool(0))
sof = Signal(bool(0))
rss_cmp_idx = Signal(intbv(0)[3:])
runlength = Signal(intbv(0)[4:])
size = Signal(intbv(0)[4:])
amplitude = Signal(intbv(0)[RAMDATA_W:])
dovalid = Signal(bool(0))
rd_addr = Signal(intbv(0)[6:])
#inst = toVHDL(rle,reset,clk,di,start_pb,sof,rss_cmp_idx,runlength,size,amplitude,dovalid,rd_addr)