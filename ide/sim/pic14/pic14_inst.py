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
        inst_movwf(sim, msb, lsb)

#----------------------------------------------------------------------------
def inst_nop(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_return(sim, msb, lsb):
    sim.log("\n######################## inst_return\n")
    sim.ret()

#----------------------------------------------------------------------------
def inst_retfie(sim, msb, lsb):
    sim.retfie()

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
    w = sim.get_wreg()
    sim.set_reg('trisa', w)

#----------------------------------------------------------------------------
def inst_tris2(sim, msb, lsb):
    w = sim.get_wreg()
    sim.set_reg('trisb', w)    

#----------------------------------------------------------------------------
def inst_tris3(sim, msb, lsb):
    w = sim.get_wreg()
    sim.set_reg('trisc', w)    

#----------------------------------------------------------------------------
def inst_movwf(sim, msb, lsb):
    #00 : 0000 0000 1fff ffff  MOVWF f   f <- W
    #
    # f : Register file addesss ( 00(00h) to 127(7Fh) )
    # d always = 1, store result in f    
    f = lsb & 0x7f
    w = sim.get_wreg()
    sim.set_freg(f, w)

#----------------------------------------------------------------------------
def inst_clrf(sim, msb, lsb):
    #01 : 0000 0001 dfff ffff  CLR f,d(bit 7)  Z dest <- 0, usually written CLRW or CLRF f
    d = (lsb >> 7) & 1
    f = lsb & 0x7f
    sim.set_z(1)
    if d == 0:
        sim.set_wreg(0)
    else:
        sim.set_freg(f, 0)
        
#----------------------------------------------------------------------------
def inst_subwf(sim, msb, lsb):
    #02 : 0000 0010 dfff ffff  SUBWF f,d C Z dest <- f-W (dest <- f+~W+1)
    #
    # f : Register file addesss ( 00(00h) to 127(7Fh) )
    # d : Destination select ( 0 or 1 )    
    #
    # d = 0 : store result in W
    # d = 1 : store result in f    
    #
    # C=1, Z=0 ( Result is positive )
    # C=1, Z=1 ( Result is zero )
    # C=0, Z=0 ( Result is negative )
    
    d = (lsb >> 7) & 1
    f = lsb & 0x7f
    v = sim.get_freg(f)
    w = sim.get_wreg()
    if v > w:
        c = 1
        z = 0
        v = v - w
    elif v == w:
        c = z = 1
        v = 0
    else:
        c = z = 0
        v = v + ~w + 1
        
    sim.set_c(c)
    sim.set_z(z)
    if d == 0:
        sim.set_wreg(v)
    else:
        sim.set_freg(f, v)

#----------------------------------------------------------------------------
def inst_decf(sim, msb, lsb):
    #03 : 0000 0011 dfff ffff  DECF f,d  Z dest <- f-1
    #f : Register file addesss ( 00(00h) to 127(7Fh) )
    #d : Destination select ( 0 or 1 )    
    #d = 0 : store result in W
    #d = 1 : store result in f
    #When the result is 0, it sets 1 to the Z flag.
    #When the result is not 0, it sets 0 to the Z flag.    
    d = (lsb >> 7) & 1
    f = lsb & 0x7f
    v = sim.get_freg(f)
    if v == 1:
        v = 0
        z = 1
    else:
        v = (v - 1) & 0xff
        z = 0
    sim.set_z(z)
    
    if d == 0:
        sim.set_wreg(v)
    else:
        sim.set_freg(f, v)
        
#----------------------------------------------------------------------------
def inst_iorwf(sim, msb, lsb):
    #04 : 0000 0100 dfff ffff  IORWF f,d  Z dest <- f | W, logical inclusive or
    #f : Register file addesss ( 00(00h) to 127(7Fh) )
    #d : Destination select ( 0 or 1 )    
    #When the result is 0, it sets 1 to the Z flag.
    #When the result is not 0, it sets 0 to the Z flag.    
    #d = 0 : store result in W
    #d = 1 : store result in f    
    d = (lsb >> 7) & 1
    f = lsb & 0x7f
    v = sim.get_freg(f)
    w = sim.get_wreg()
    v = v | w
    if v == 0:
        z = 1
    else:
        z = 0
    sim.set_z(z)
    if d == 0:
        sim.set_wreg(v)
    else:
        sim.set_freg(f, v)

#----------------------------------------------------------------------------
def inst_andwf(sim, msb, lsb):
    #05 : 0000 0101 dfff ffff  ANDWF f,d  Z dest <- f & W, logical and
    #f : Register file addesss ( 00(00h) to 127(7Fh) )
    #d : Destination select ( 0 or 1 )    
    #When the result is 0, it sets 1 to the Z flag.
    #When the result is not 0, it sets 0 to the Z flag.    
    #d = 0 : store result in W
    #d = 1 : store result in f    
    d = (lsb >> 7) & 1
    f = lsb & 0x7f
    v = sim.get_freg(f)
    w = sim.get_wreg()
    v = v & w
    if v == 0:
        z = 1
    else:
        z = 0
    sim.set_z(z)
    if d == 0:
        sim.set_wreg(v)
    else:
        sim.set_freg(f, v)


#----------------------------------------------------------------------------
def inst_xorwf(sim, msb, lsb):
    #06 : 0000 0110 dfff ffff  XORWF f,d  Z dest <- f ^ W, logical exclusive or
    # f : Register file addesss ( 00(00h) to 127(7Fh) )
    # d : Destination select ( 0 or 1 )    
    # When the result is 0, it sets 1 to the Z flag.
    # When the result is not 0, it sets 0 to the Z flag.    
    # d = 0 : store result in W
    # d = 1 : store result in f    
    d = (lsb >> 7) & 1
    f = lsb & 0x7f
    v = sim.get_freg(f)
    w = sim.get_wreg()
    v = v ^ w
    if v == 0:
        z = 1
    else:
        z = 0
    sim.set_z(z)
    if d == 0:
        sim.set_wreg(v)
    else:
        sim.set_freg(f, v)


#----------------------------------------------------------------------------
def inst_addwf(sim, msb, lsb):
    #07 : 0000 0111 dfff ffff  ADDWF f,d C Z dest <- f+W
    #
    # f : Register file addesss ( 00(00h) to 127(7Fh) )
    # d : Destination select ( 0 or 1 )        
    #
    # When the byte overflows, it sets 1 to the C flag.
    # When 4 bits of lower part overflow, it sets 1 to the DC flag.
    # When the result is 0, it sets 1 to the Z flag.
    # In the case except the above, it sets 0 to C, DC and Z.    
    #
    # d = 0 : store result in W
    # d = 1 : store result in f        
    d = (lsb >> 7) & 1
    f = lsb & 0x7f
    v = sim.get_freg(f)
    w = sim.get_wreg()
    v = v + w
    c = dc = z = 0
    if v > 0xff:
        c = 1
        v = v & 0xff
    elif v > 0xf:
        dc = 1
    elif v == 0:
        z = 1

    sim.set_c(c)
    sim.set_z(z)
    sim.set_dc(dc)    
    
    if d == 0:
        sim.set_wreg(v)
    else:
        sim.set_freg(f, v)
        
#----------------------------------------------------------------------------
def inst_movf(sim, msb, lsb):
    #08 : 0000 1000 dfff ffff  MOVF f,d  Z dest <- f
    #
    # f : Register file addesss ( 00(00h) to 127(7Fh) )
    # d : Destination select ( 0 or 1 )    
    #
    # When the result is 0, it sets 1 to the Z flag.
    # When the result is not 0, it sets 0 to the Z flag.    
    #
    # d = 0 : store result in W
    # d = 1 : store result in f    
    #
    d = (lsb >> 7) & 1
    f = lsb & 0x7f
    v = sim.get_freg(f)
    w = sim.get_wreg()

    if v == 0:
        z = 1
    else:
        z = 0
    sim.set_z(z)
    if d == 0:
        sim.set_wreg(v)
    else:
        sim.set_freg(f, v)

#----------------------------------------------------------------------------
def inst_comf(sim, msb, lsb):
    #09 : 0000 1001 dfff ffff  COMF f,d  Z dest <- ~f, bitwise complement
    #
    # f : Register file addesss ( 00(00h) to 127(7Fh) )
    # d : Destination select ( 0 or 1 )    
    #
    # When the result is 0, it sets 1 to the Z flag.
    # When the result is not 0, it sets 0 to the Z flag.    
    #
    # d = 0 : store result in W
    # d = 1 : store result in f    
    #
    d = (lsb >> 7) & 1
    f = lsb & 0x7f
    v = ~sim.get_freg(f)
    w = sim.get_wreg()

    if v == 0:
        z = 1
    else:
        z = 0
        
    sim.set_z(z)
    if d == 0:
        sim.set_wreg(v)
    else:
        sim.set_freg(f, v)
    
#----------------------------------------------------------------------------
def inst_incf(sim, msb, lsb):
    #0a : 0000 1010 dfff ffff  INCF f,d  Z dest <- f+1
    #
    # f : Register file addesss ( 00(00h) to 127(7Fh) )
    # d : Destination select ( 0 or 1 )    
    #
    # When the result is 0, it sets 1 to the Z flag.
    # When the result is not 0, it sets 0 to the Z flag.    
    #
    # d = 0 : store result in W
    # d = 1 : store result in f    
    #    
    d = (lsb >> 7) & 1
    f = lsb & 0x7f
    v = sim.get_freg(f)
    v = (v + 1) & 0xff
    
    if v == 0:
        v = 0
        z = 1
    else:
        z = 0
        
    sim.set_z(z)
    
    if d == 0:
        sim.set_wreg(v)
    else:
        sim.set_freg(f, v)

#----------------------------------------------------------------------------
def inst_decfsz(sim, msb, lsb):
    #0b : 0000 1011 dfff ffff  DECFSZ f,d   dest <- f-1, then skip if zero
    #
    # f : Register file addesss ( 00(00h) to 127(7Fh) )
    # d : Destination select ( 0 or 1 )    
    #
    # d = 0 : store result in W
    # d = 1 : store result in f
    #
    # When the result is 0, it sets 1 to the Z flag.
    # When the result is not 0, it sets 0 to the Z flag.    
    #
    d = (lsb >> 7) & 1
    f = lsb & 0x7f
    v = sim.get_freg(f)
    if v == 1:
        v = 0
        z = 1
    else:
        v = (v - 1) & 0xff
        z = 0
    sim.set_z(z)
    
    if d == 0:
        sim.set_wreg(v)
    else:
        sim.set_freg(f, v)
        
    if v == 0:
        sim.skip_next_inst()

#----------------------------------------------------------------------------
def inst_rrf(sim, msb, lsb):
    #0c : 0000 1100 dfff ffff  RRF f,d C  dest <- CARRY<<7 | f>>1, rotate right through carry
    #   c -> f7 f0 -> c
    # d = 0 : store result in W
    # d = 1 : store result in f
    
    d = (lsb >> 7) & 1
    f = lsb & 0x7f
    v = sim.get_freg(f)
    bit0 = v & 1
    c = sim.get_c()
    v = (v >> 1) | (c << 7)
    sim.set_c(bit0)
    if d == 0:
        sim.set_wreg(v)
    else:
        sim.set_freg(f, v)

#----------------------------------------------------------------------------
def inst_rlf(sim, msb, lsb):
    #0d : 0000 1101 dfff ffff  RLF f,d C  dest <- f<<1 | CARRY, rotate left through carry
    #  c <- f7 f0 <- c
    # d = 0 : store result in W
    # d = 1 : store result in f    
    d = (lsb >> 7) & 1
    f = lsb & 0x7f
    v = sim.get_freg(f)
    bit7 = (v >> 7) & 1
    c = sim.get_c()
    v = (v << 1) | c
    sim.set_c(bit7)
    if d == 0:
        sim.set_wreg(v)
    else:
        sim.set_freg(f, v)

#----------------------------------------------------------------------------
def inst_swapf(sim, msb, lsb):
    #0e : 0000 1110 dfff ffff  SWAPF f,d   dest <- f<<4 | f>>4, swap nibbles
    #  f3-0 swap with f7-4
    d = (lsb >> 7) & 1
    f = lsb & 0x7f
    v = sim.get_freg(f)
    bit_3_0 = v & 0xf
    bit_7_4 = (v >> 4) & 0xf
    v = (bit_3_0 << 4) | bit_7_4
    if d == 0:
        sim.set_wreg(v)
    else:
        sim.set_freg(f, v)
        
#----------------------------------------------------------------------------
def inst_incfsz(sim, msb, lsb):
    #0f : 0000 1111 dfff ffff  INCFSZ f,d   dest <- f+1, then skip if zero   
    d = (lsb >> 7) & 1
    f = lsb & 0x7f
    v = sim.get_freg(f)
    v = (v + 1) & 0xff
    
    if v == 0:
        v = 0
        z = 1
    else:
        z = 0
        
    sim.set_z(z)
    
    if d == 0:
        sim.set_wreg(v)
    else:
        sim.set_freg(f, v)
        
    if v == 0:
        sim.skip_next_inst()
        
#----------------------------------------------------------------------------
def inst_bcf(sim, msb, lsb):
    #10 : 0001 00bb bfff ffff  bit(3, b7-b9) f(7, b0-b6) BCF f,b   Clear bit b of f
    bit = get_bits((msb << 8) | lsb, 7, 9)
    f = lsb & 0x7f
    if f == 3:
        sim.set_status_reg(bit, 0)
    else:
        v = sim.get_freg(f)
        v = utils.clear_bit(v, bit)
        sim.set_freg(f, v)

#----------------------------------------------------------------------------
def inst_bsf(sim, msb, lsb):
    #14 : 0001 01bb bfff ffff  BSF f,b   Set bit b of f
    bit = get_bits((msb << 8) | lsb, 7, 9)
    f = lsb & 0x7f
    if f == 3:
        sim.set_status_reg(bit, 1)
    else:    
        v = sim.get_freg(f)
        v = utils.set_bit(v, bit)
        sim.set_freg(f, v)

#----------------------------------------------------------------------------
def inst_btfsc(sim, msb, lsb):
    #18 : 0001 10bb bfff ffff  BTFSC f,b   Skip if bit b of f is clear
    bit = get_bits((msb << 8) | lsb, 7, 9)
    f = lsb & 0x7f
    v = sim.get_freg(f)
    b = get_bit(v, bit)
    if b == 0:
        sim.skip_next_inst()

#----------------------------------------------------------------------------
def inst_btfss(sim, msb, lsb):
    #1c : 0001 11bb bfff ffff  BTFSS f,b   Skip if bit b of f is set
    bit = get_bits((msb << 8) | lsb, 7, 9)
    f = lsb & 0x7f
    v = sim.get_freg(f)
    b = get_bit(v, bit)
    if b != 0:
        sim.skip_next_inst()

#----------------------------------------------------------------------------
def inst_call(sim, msb, lsb):
    #20 : 0010 0kkk kkkk kkkk CALL k   Call subroutine
    k = ((msb & 0x7) << 8) | lsb
    sim.call(k)

#----------------------------------------------------------------------------
def inst_goto(sim, msb, lsb):
    #28 : 0010 1kkk kkkk kkkk  GOTO k   Jump to address k 
    k = ((msb & 0x7) << 8) | lsb
    sim.jump(k)

#----------------------------------------------------------------------------
def inst_movlw(sim, msb, lsb):
    #30 : 0011 00xx kkkk kkkk MOVLW k   W <- k
    sim.set_wreg(lsb)

#----------------------------------------------------------------------------
def inst_retlw(sim, msb, lsb):
    #34 : 0011 01xx kkkk kkkk RETLW k   W <- k, then return from subroutine
    sim.set_wreg(lsb)
    sim.ret()

#----------------------------------------------------------------------------
def inst_iorlw(sim, msb, lsb):
    #38 : 0011 1000 kkkk kkkk IORLW k  Z W <- k | W, bitwise logical or
    w = sim.get_wreg()
    k = lsb
    w = k | w
    if w == 0:
        z = 1
    else:
        z = 0
    sim.set_wreg(w)
    sim.set_z(z)

#----------------------------------------------------------------------------
def inst_andlw(sim, msb, lsb):
    #39 : 0011 1001 kkkk kkkk ANDLW k  Z W <- k & W, bitwise and
    w = sim.get_wreg()
    k = lsb
    w = k & w
    if w == 0:
        z = 1
    else:
        z = 0
    sim.set_wreg(w)
    sim.set_z(z)

#----------------------------------------------------------------------------
def inst_xorlw(sim, msb, lsb):
    #3a : 0011 1010 kkkk kkkk XORLW k  Z W <- k ^ W, bitwise exclusive or
    w = sim.get_wreg()
    k = lsb
    w = k ^ w
    
    if w == 0:
        z = 1
    else:
        z = 0
    sim.set_wreg(w)
    sim.set_z(z)

#----------------------------------------------------------------------------
def inst_sublw(sim, msb, lsb):
    #3c : 0011 110x kkkk kkkk SUBLW k C Z W <- k-W (dest <- k+~W+1)
    w = sim.get_wreg()
    k = lsb
    if k > w:
        w = k - w
        c = 1
        z = 0
    elif k < w:
        w = k + ~w + 1
        c = 0
        z = 0
    else:
        w = 0
        c = 1
        z = 1
        
    sim.set_wreg(w)
    sim.set_c(c)
    sim.set_z(z)

#----------------------------------------------------------------------------
def inst_addlw(sim, msb, lsb):
    #3e : 0011 111x kkkk kkkk ADDLW k C Z W <- k+W
    c = z = dc = 0
    w = sim.get_wreg() 
    k = lsb
    w = k + w
    
    if w > 0xf:
        dc = 1
        
    if w > 0xff:
        c = 1
        w = w & 0xff
            
    if w == 0:
        z = 1

    sim.set_wreg(w)
    sim.set_c(c)
    sim.set_z(z)
    sim.set_dc(dc)
    

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
    inst_call,    #21
    inst_call,    #22
    inst_call,    #23
    inst_call,    #24
    inst_call,    #25
    inst_call,    #26
    inst_call,    #27
    inst_goto,    #28
    inst_goto,    #29
    inst_goto,    #2A
    inst_goto,    #2B
    inst_goto,    #2C
    inst_goto,    #2D
    inst_goto,    #2E
    inst_goto,    #2F
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
    
#----------------------------------------------------------------------------
def get_pic14_inst_str(v, msb, lsb):
    msb = msb & 0x3f

    v0 = (msb >> 4) & 0xf #bit 13, 12
    v1 = msb & 0xf        #bit 11, 10, 9, 8
    v2 = (lsb >> 4) & 0xf
    v3 = lsb & 0xf
    
    f = get_bits(v, 0, 6)
    inst = ' - '
    if v0 == 0 and v1 == 0:
        if lsb == 0x00: inst = 'nop'
        elif lsb == 0x08: inst = 'return'
        elif lsb == 0x09: inst = 'retfie'
        elif lsb == 0x62: inst = 'option'
        elif lsb == 0x63: inst = 'sleep'
        elif lsb == 0x64: inst = 'clrwdt'
        elif lsb == 0x65: inst = 'tris1'
        elif lsb == 0x66: inst = 'tris2'
        elif lsb == 0x67: inst = 'tris3'
        else:
            inst = 'movwf ' + hex(f)
    elif v0 == 0:  
        lst = ['movwf', 'clrf', 'subwf', 'decf', 'iorwf', 'andwf', 'xorwf', 'addwf', 'movf', 'comf', 'incf', 'decfsz', 'rrf', 'rlf', 'swapf', 'incfsz']
        inst = lst[v1]
        d = get_bit(v, 7)
        #f = get_bits(v, 0, 6)
        inst += ' ' + hex(f) 
        if d == 0:
            inst += ', w'
        elif v1 != 0x01:
            inst += ', f'
  
    elif v0 == 1:
        lst = ['bcf', 'bsf', 'btfsc', 'btfss']
        v1 &= 0xc
        #f = v3 & 0x7f
        b = get_bits(v, 7, 9)
        
        if v1 == 0:
            inst = 'bcf'
        elif v1 == 4:
            inst = 'bsf'
        elif v1 == 0x8:
            inst = 'btfsc'
        elif v1 == 0xc:
            inst = 'btfss'
        inst += ' ' + hex(f) + ',' + hex(b)
    elif v0 == 2:
        b = v1 & 0x8
        if b == 0:
            inst = 'call'
        elif b == 8:
            inst = 'goto'
        k = get_bits(v, 0, 10)
        inst += ' ' + hex(k)
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
        k = v3
        inst += ' ' + hex(k)
            
    return inst

#---- for testing -------------------------------------------------------------
if __name__ == '__main__':    
    gen_pic14_inst_table()