import os
import utils

#----------------------------------------------------------------------------
def get_bit(v, i):
    v >>= i
    return v & 1

#----------------------------------------------------------------------------
def get_bits(v, i0, i1):
    if i0 > i1:
        t = i1
        i1 = i0
        i0 = i1
    
    m = 0
    for i in range(i0, i1+1, 1):
        m = m | (1 << i)
        
    return (v & m) >> i0

#----------------------------------------------------------------------------
def inst_reserved(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_msb_0(sim, msb, lsb):   
    if lsb == 0x00: inst_nop(sim, msb, lsb)
    elif lsb == 0x08: inst_return(sim, msb, lsb)
    elif lsb == 0x09: inst_retfie(sim, msb, lsb)
    elif lsb == 0x62: inst_option(sim, msb, lsb)
    elif lsb == 0x63: inst_sleep(sim, msb, lsb)
    elif lsb == 0x64: inst_clrwdt(sim, msb, lsb)
    elif lsb == 0x65: inst_tris1(sim, msb, lsb)
    elif lsb == 0x66: inst_tris2(sim, msb, lsb)
    elif lsb == 0x67: inst_tris3(sim, msb, lsb)
    else:
        inst_movwf(sim, msg, lsb)

#----------------------------------------------------------------------------
def inst_nop(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_return(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_retfie(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_option(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_sleep(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_clrwdt(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_tris1(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_tris2(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_tris3(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_movwf(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_clrf(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_subwf(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_decf(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_iorwf(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_andwf(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_xorwf(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_addwf(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_movf(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_comf(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_incf(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_decfsz(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_rrf(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_rlf(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_swapf(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_incfsz(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_bcf(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_bsf(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_btfsc(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_btfss(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_call(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_goto(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_movlw(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_retlw(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_iorlw(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_andlw(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_xorlw(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_sublw(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_addlw(sim, msb, lsb):
    pass


#----------------------------------------------------------------------------
inst_handler = [
    inst_msb_0,    #00
    inst_clrf,    #01
    inst_subwf,    #02
    inst_decf,    #03
    inst_iorwf,    #04
    inst_andwf,    #05
    inst_xorwf,    #06
    inst_addwf,    #07
    inst_movf,    #08
    inst_comf,    #09
    inst_incf,    #0A
    inst_decfsz,    #0B
    inst_rrf,    #0C
    inst_rlf,    #0D
    inst_swapf,    #0E
    inst_incfsz,    #0F
    inst_bcf,    #10
    inst_bcf,    #11
    inst_bcf,    #12
    inst_bcf,    #13
    inst_bsf,    #14
    inst_bsf,    #15
    inst_bsf,    #16
    inst_bsf,    #17
    inst_btfsc,    #18
    inst_btfsc,    #19
    inst_btfsc,    #1A
    inst_btfsc,    #1B
    inst_btfss,    #1C
    inst_btfss,    #1D
    inst_btfss,    #1E
    inst_btfss,    #1F
    inst_call,    #20
    inst_reserved,    #21
    inst_reserved,    #22
    inst_reserved,    #23
    inst_reserved,    #24
    inst_reserved,    #25
    inst_reserved,    #26
    inst_reserved,    #27
    inst_goto,    #28
    inst_reserved,    #29
    inst_reserved,    #2A
    inst_reserved,    #2B
    inst_reserved,    #2C
    inst_reserved,    #2D
    inst_reserved,    #2E
    inst_reserved,    #2F
    inst_movlw,    #30
    inst_movlw,    #31
    inst_movlw,    #32
    inst_movlw,    #33
    inst_retlw,    #34
    inst_retlw,    #35
    inst_retlw,    #36
    inst_retlw,    #37
    inst_iorlw,    #38
    inst_andlw,    #39
    inst_xorlw,    #3A
    inst_reserved,    #3B
    inst_sublw,    #3C
    inst_sublw,    #3D
    inst_addlw,    #3E
    inst_addlw,    #3F
]

    
def gen_pic14_inst_table():
    inst_table = ['inst_reserved']*0x40
    
    for msb in range(0x40):        
        msb = msb & 0x3f
    
        v0 = (msb >> 4) & 0xf #bit 13, 12
        v1 = msb & 0xf
        
        if msb == 0x00:
            inst_table[msb] = 'inst_msb_0'
        elif v0 == 0:
            lst = ['movwf', 'clrf', 'subwf', 'decf', 'iorwf', 'andwf', 'xorwf', 'addwf', 'movf', 'comf', 'incf', 'decfsz', 'rrf', 'rlf', 'swapf', 'incfsz']
            inst_table[msb] = 'inst_' + lst[v1]
      
        elif v0 == 1:
            lst = ['bcf', 'bsf', 'btfsc', 'btfss']            
            if v1 == 0:
                inst = 'bcf'
            elif v1 == 4:
                inst = 'bsf'
            elif v1 == 0x8:
                inst = 'btfsc'
            elif v1 == 0xc:
                inst = 'btfss'
            inst_table[msb] = 'inst_' + inst
        elif v0 == 2:
            if v1 == 0:
                inst_table[msb] = 'inst_call'
            elif v1 == 8:
                inst_table[msb] = 'inst_goto'
        elif v0 == 3:
            if v1 == 0:
                inst = 'movlw'
            elif v1 == 4:
                inst = 'retlw'
            elif v1 == 8:
                inst = 'iorlw'
            elif v1 == 9:
                inst = 'andlw'
            elif v1 == 0xa:
                inst = 'xorlw'
            elif v1 == 0xb:
                inst = 'reserved'
            elif v1 == 0xc:
                inst = 'sublw'
            elif v1 == 0xe:
                inst = 'addlw'
            inst_table[msb] = 'inst_' + inst
    
    #print 'inst_table = ['
    #for i in range(64):
        #print inst_table[i].lower() + ',    #' + utils.tohex(i, 2)
        
    #print ']'
    #lst = []
    #for t in inst_table:
        #if not t in lst:
            #lst.append(t)
    
    #for t in lst:
        #print '#----------------------------------------------------------------------------'
        #print 'def ' + t.lower() + '(sim, msb, lsb):\n    pass\n'
    
    #return inst_table 
    


#---- for testing -------------------------------------------------------------
if __name__ == '__main__':    
    gen_pic14_inst_table()