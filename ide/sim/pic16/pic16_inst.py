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
    lst = [inst_nop, None, None, inst_sleep, inst_clrwdt, inst_push, inst_pop, inst_daw, 
           inst_tblrd, inst_tblrd, inst_tblrd, inst_tblrd,
           inst_tblwr, inst_tblwr, inst_tblwr, inst_tblwr,
           inst_retfie, inst_retfie, inst_return, inst_return]
    if lsb < len(lst):
        f = lst[lsb]
        if f is not None:
            f(sim, msb, lsb)
    elif lsb == 0xff:
        inst_reset(sim, msb, lsb)
        
#----------------------------------------------------------------------------
def inst_reset(sim, msb, lsb):
    pass
#----------------------------------------------------------------------------
def inst_nop(sim, msb, lsb):
    pass
#----------------------------------------------------------------------------
def inst_sleep(sim, msb, lsb):
    pass
#----------------------------------------------------------------------------
def inst_clrwdt(sim, msb, lsb):
    pass
#----------------------------------------------------------------------------
def inst_nop(sim, msb, lsb):
    pass
#----------------------------------------------------------------------------
def inst_push(sim, msb, lsb):
    pass
#----------------------------------------------------------------------------
def inst_pop(sim, msb, lsb):
    pass
#----------------------------------------------------------------------------
def inst_daw(sim, msb, lsb):
    pass
#----------------------------------------------------------------------------
def inst_tblrd(sim, msb, lsb):
    pass
#----------------------------------------------------------------------------
def inst_tblwr(sim, msb, lsb):
    pass
#----------------------------------------------------------------------------
def inst_retfie(sim, msb, lsb):
    pass
#----------------------------------------------------------------------------
def inst_return(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
def inst_movlb(sim, msb, lsb):
    # 0x01 0000 0001 0000 k MOVLB    Move literal k to bank select register 
    k = get_bits(lsb, 0, 5)
    sim.set_bsr(k)

#----------------------------------------------------------------------------
def inst_movlw(sim, msb, lsb):
    # 0000 1110 kkkk kkkk, k -> W  , The eight-bit literal 'k' is loaded into W
    # no status register bit affacted
    # movlw 0x5a
    # w = 0x5a
    sim.set_wreg(lsb)
    
#----------------------------------------------------------------------------
def inst_mulwf(sim, msb, lsb):
    #0x02-0x03 0000 001a ffff ffff MULWF f,a    PRODH:PRODL <- W x f (unsigned)
    # a is access
    # a == 0, Access Bank will be selected, overriding the BSR value.
    # a == 1, BSR will not be overridden(default)
    w = sim.get_wreg()
    f = sim.get_mem(lsb)
    a = get_bit(msb, 0)
    if a == 0:
        sim.select_access_bank()
    v = w * f
    sim.set_prod(v)
    
#----------------------------------------------------------------------------
def inst_decf(sim, msb, lsb):
    #0x04-0x07 0000 01 d a f DECF f,d,a C Z N dest <- f - 1
    pass

#----------------------------------------------------------------------------
def inst_iorwf(sim, msb, lsb):
    #0x10-0x13 0001 00 d a f IORWF f,d,a  Z N dest <- f | W, logical inclusive or
    pass

#----------------------------------------------------------------------------
def inst_andwf(sim, msb, lsb):
    #0x14-0x17 0001 01da ffff ffff  ANDWF f,d,a  Z N dest <- f & W, logical and
    # d == 0, result stored in W
    # d == 1, result stored to f    
    # a is access
    # a == 0, Access Bank will be selected, overriding the BSR value.
    # a == 1, BSR will not be overridden(default)
    w = sim.get_wreg()
    f = sim.get_mem(lsb)
    d = get_bit(msb, 1)
    a = get_bit(msb, 0)
    if a == 0:
        sim.select_access_bank()
    v = w & f
    if d == 0:
        sim.set_wreg(v)
    else:
        sim.set_mem(lsb, v)
    
#----------------------------------------------------------------------------
def inst_xorwf(sim, msb, lsb):
    w = sim.get_wreg()
    f = sim.get_mem(lsb)
    d = get_bit(msb, 1)
    a = get_bit(msb, 0)
    if a == 0:
        sim.select_access_bank()
    v = w | f
    if d == 0:
        sim.set_wreg(v)
    else:
        sim.set_mem(lsb, v)    

#----------------------------------------------------------------------------
def inst_comf(sim, msb, lsb):
    pass
#----------------------------------------------------------------------------
def inst_addwfc(sim, msb, lsb):
    #0x20-0x23 0010 00 d a f ADDWFC f,d,a C Z N dest <- f + W + C
    pass
#----------------------------------------------------------------------------
def inst_addwf(sim, msb, lsb):
    #0x24-0x27 0010 01 d a f ADDWF f,d,a C Z N dest <- f + W
    w = sim.get_wreg()
    f = sim.get_mem(lsb)
    d = get_bit(msb, 1)
    a = get_bit(msb, 0)
    if a == 0:
        sim.select_access_bank()
    v = w + f
    if d == 0:
        sim.set_wreg(v)
    else:
        sim.set_mem(lsb, v)    

#----------------------------------------------------------------------------
def inst_incf(sim, msb, lsb):
    #0x28-0x2b 0000 10 d a f INCF f,d,a C Z N dest <- f + 1
    pass
#----------------------------------------------------------------------------
def inst_decfsz(sim, msb, lsb):
    #0x2c-0x2f 0010 11 d a f DECFSZ f,d,a    dest <- f - 1, skip if 0
    pass
#----------------------------------------------------------------------------
def inst_rrncf(sim, msb, lsb):
    #0x40-0x43 0100 00 d a f RRNCF f,d,a  Z N dest <- f>>1 | f<<7, rotate right (no carry)
    pass
#----------------------------------------------------------------------------
def inst_rlncf(sim, msb, lsb):
    #0x44-0x47 0100 01 d a f RLNCF f,d,a  Z N dest <- f<<1 | f>>7, rotate left (no carry)
    pass
#----------------------------------------------------------------------------
def inst_infsnz(sim, msb, lsb):
    #0x48-0x4B 0100 10 d a f INFSNZ f,d,a    dest <- f + 1, skip if not 0
    pass
#----------------------------------------------------------------------------
def inst_dcfsnz(sim, msb, lsb):
    #0x4c-0x4F 0100 11 d a f DCFSNZ f,d,a    dest <- f - 1, skip if not 0
    pass
#----------------------------------------------------------------------------
def inst_movf(sim, msb, lsb):
    #0x50-0x53 0101 00 d a f MOVF f,d,a  Z N dest <- f
    pass
#----------------------------------------------------------------------------
def inst_subfwb(sim, msb, lsb):
    #0x54-0x57 0101 01 d a f SUBFWB f,d,a C Z N dest <- W + ~f + C (dest <- W - f - Cinvert)
    pass
#----------------------------------------------------------------------------
def inst_subwfb(sim, msb, lsb):
    #0x58-0x5B 0101 10 d a f SUBWFB f,d,a C Z N dest <- f + ~W + C (dest <- f - W - Cinvert)
    pass
#----------------------------------------------------------------------------
def inst_subwf(sim, msb, lsb):
    #0x5c-0x5F 0101 11 d a f SUBWF f,d,a C Z N dest <- f - W (dest <- f + ~W + 1)        
    pass
#----------------------------------------------------------------------------
def inst_cpfslt(sim, msb, lsb):
    #0x60, 0x61 0110 000 a f CPFSLT f,a    skip if f < W
    pass
#----------------------------------------------------------------------------
def inst_cpfseq(sim, msb, lsb):
    #0x62, 0x63 0110 001 a f CPFSEQ f,a    skip if f == W
    pass
#----------------------------------------------------------------------------
def inst_cpfsgt(sim, msb, lsb):
    #0x64, 0x65 0110 010 a f CPFSGT f,a    skip if f > W
    pass
#----------------------------------------------------------------------------
def inst_tstfsz(sim, msb, lsb):
    #0x66, 0x67 0110 011 a f TSTFSZ f,a    skip if f == 0
    pass
#----------------------------------------------------------------------------
def inst_setf(sim, msb, lsb):
    #0x68, 0x69 0110 100 a f SETF f,a      f <- 0xFF
    f = lsb
    a = get_bit(msb, 1)
    sim.set_mem(f, 1)

#----------------------------------------------------------------------------
def inst_clrf(sim, msb, lsb):
    # 0110 101a f CLRF f,a  1  f <- 0, PSR.Z <- 1
    f = lsb
    a = get_bit(msb, 1)
    #print 'inst_clrf', f, a
    sim.set_mem(f, 0)
    sim.set_z(1)

#----------------------------------------------------------------------------
def inst_negf(sim, msb, lsb):
    #0x6C, 0x6D 0110 110 a f NEGF f,a    C Z N f  <- -f
    pass
#----------------------------------------------------------------------------
def inst_movwf(sim, msb, lsb):
    #0x6E, 0x6F 0110 111a ffff ffff MOVWF f,a    f  <- W
    # a is access
    # a == 0, Access Bank will be selected, overriding the BSR value.
    # a == 1, BSR will not be overridden(default)
    w = sim.get_wreg()
    a = get_bit(msb, 0)
    if a == 0:
        sim.select_access_bank()

    sim.set_mem(lsb, w)
        
#----------------------------------------------------------------------------
def inst_btg(sim, msb, lsb):
    #0x7? 0111 bit a f BTG f,b,a    Toggle bit b of f
    pass

#----------------------------------------------------------------------------
def inst_bsf(sim, msb, lsb):
    #0x8? 1000 bit a f BSF f,b,a    Set bit b of f
    # a is access
    # a = 0, Access Bank will be selected, overriding the BSR value.
    # a = 1, the bank will be selected as per the BSR value.
    bit = get_bits(msb, 1, 3)
    a = get_bit(msb, 0)
    f = lsb
    sim.mem_set_bit(f, bit, 1)

#----------------------------------------------------------------------------
def inst_bcf(sim, msb, lsb):
    #0x9? 1001 bit a f BCF f,b,a    Clear bit b of f
    bit = get_bits(msb, 1, 3)
    a = get_bit(msb, 0)
    f = lsb
    v = sim.mem_get_bit(f, bit)
    if v == 0:
        sim.skip_next_inst()

#----------------------------------------------------------------------------
def inst_btfss(sim, msb, lsb):
    #0xA? 1010 bbba ffff ffff  BTFSS f,b,a    Skip if bit b of f is set
    bit = get_bits(msb, 1, 3)
    a = get_bit(msb, 0)
    f = lsb
    v = sim.mem_get_bit(f, bit)
    if v != 0:
        sim.skip_next_inst()
    
#----------------------------------------------------------------------------
def inst_btfsc(sim, msb, lsb):
    #0xB? 1011 bit a f BTFSC f,b,a    Skip if bit b of f is clear    
    pass
#----------------------------------------------------------------------------
def inst_bra(sim, msb, lsb):
    #0xD? 1101 0 n BRA n    Branch to PC + 2n
    # 1101 0nnn nnnn nnnn
    v = (msb << 8) | lsb
    n = get_bits(v, 0, 10)
    n = n * 2
    if n & 0x800:
        n = (n & 0x7ff) - 0x800
        print 'inst_bra', n
    sim.set_pc(sim.pc + n)
    
#----------------------------------------------------------------------------
def inst_rcall(sim, msb, lsb):
    #0xD? 1101 1 n RCALL n    Subroutine call to PC + 2n
    pass
#----------------------------------------------------------------------------
def inst_bz(sim, msb, lsb):
    #0xE0  1110 0000 n BZ n    Branch if PSR.Z is set
    pass
#----------------------------------------------------------------------------
def inst_bnz(sim, msb, lsb):
    #0xE1  1110 0001 n BNZ n    Branch if PSR.Z is clear
    pass
#----------------------------------------------------------------------------
def inst_bc(sim, msb, lsb):
    #0xE2  1110 0010 n BC n    Branch if PSR.C is set
    pass
#----------------------------------------------------------------------------
def inst_bnc(sim, msb, lsb):
    #0xE3  1110 0011 n BNC n    Branch if PSR.C is clear
    pass
#----------------------------------------------------------------------------
def inst_bov(sim, msb, lsb):
    #0xE4  1110 0100 n BOV n    Branch if PSR.V is set
    pass
#----------------------------------------------------------------------------
def inst_bnov(sim, msb, lsb):
    #0xE5  1110 0101 n BNOV n    Branch if PSR.V is clear
    pass
#----------------------------------------------------------------------------
def inst_bn(sim, msb, lsb):
    #0xE6  1110 0110 n BN n    Branch if PSR.N is set
    pass
#----------------------------------------------------------------------------
def inst_bnn(sim, msb, lsb):
    #0xE7  1110 0111 n BNN n    Branch if PSR.N is clear      
    pass
#----------------------------------------------------------------------------
def inst_check_prev(sim, msb, lsb):
    pass

#----------------------------------------------------------------------------
inst_handler = [
    inst_msb_0,    #00
    inst_movlb,    #01
    inst_mulwf,    #02
    inst_mulwf,    #03
    inst_decf,     #04
    inst_decf,     #05
    inst_decf,     #06
    inst_decf,     #07
    inst_reserved,    #08
    inst_reserved,    #09
    inst_reserved,    #0A
    inst_reserved,    #0B
    inst_reserved,    #0C
    inst_reserved,    #0D
    inst_movlw,       #0E
    inst_reserved,    #0F
    inst_iorwf,    #10
    inst_iorwf,    #11
    inst_iorwf,    #12
    inst_iorwf,    #13
    inst_andwf,    #14
    inst_andwf,    #15
    inst_andwf,    #16
    inst_andwf,    #17
    inst_xorwf,    #18
    inst_xorwf,    #19
    inst_xorwf,    #1A
    inst_xorwf,    #1B
    inst_comf,     #1C
    inst_comf,     #1D
    inst_comf,     #1E
    inst_comf,     #1F
    inst_addwfc,   #20
    inst_addwfc,   #21
    inst_addwfc,   #22
    inst_addwfc,   #23
    inst_addwf,    #24
    inst_addwf,    #25
    inst_addwf,    #26
    inst_addwf,    #27
    inst_incf,    #28
    inst_incf,    #29
    inst_incf,    #2A
    inst_incf,    #2B
    inst_decfsz,    #2C
    inst_decfsz,    #2D
    inst_decfsz,    #2E
    inst_decfsz,    #2F
    inst_addwfc,    #30
    inst_addwfc,    #31
    inst_addwfc,    #32
    inst_addwfc,    #33
    inst_addwf,    #34
    inst_addwf,    #35
    inst_addwf,    #36
    inst_addwf,    #37
    inst_incf,    #38
    inst_incf,    #39
    inst_incf,    #3A
    inst_incf,    #3B
    inst_decfsz,    #3C
    inst_decfsz,    #3D
    inst_decfsz,    #3E
    inst_decfsz,    #3F
    inst_rrncf,    #40
    inst_rrncf,    #41
    inst_rrncf,    #42
    inst_rrncf,    #43
    inst_rlncf,    #44
    inst_rlncf,    #45
    inst_rlncf,    #46
    inst_rlncf,    #47
    inst_infsnz,    #48
    inst_infsnz,    #49
    inst_infsnz,    #4A
    inst_infsnz,    #4B
    inst_dcfsnz,    #4C
    inst_dcfsnz,    #4D
    inst_dcfsnz,    #4E
    inst_dcfsnz,    #4F
    inst_movf,    #50
    inst_movf,    #51
    inst_movf,    #52
    inst_movf,    #53
    inst_subfwb,    #54
    inst_subfwb,    #55
    inst_subfwb,    #56
    inst_subfwb,    #57
    inst_subwfb,    #58
    inst_subwfb,    #59
    inst_subwfb,    #5A
    inst_subwfb,    #5B
    inst_subwf,    #5C
    inst_subwf,    #5D
    inst_subwf,    #5E
    inst_subwf,    #5F
    inst_cpfslt,    #60
    inst_cpfslt,    #61
    inst_cpfseq,    #62
    inst_cpfseq,    #63
    inst_cpfsgt,    #64
    inst_cpfsgt,    #65
    inst_tstfsz,    #66
    inst_tstfsz,    #67
    inst_setf,    #68
    inst_setf,    #69
    inst_clrf,    #6A
    inst_clrf,    #6B
    inst_negf,    #6C
    inst_negf,    #6D
    inst_movwf,    #6E
    inst_movwf,    #6F
    inst_btg,    #70
    inst_btg,    #71
    inst_btg,    #72
    inst_btg,    #73
    inst_btg,    #74
    inst_btg,    #75
    inst_btg,    #76
    inst_btg,    #77
    inst_btg,    #78
    inst_btg,    #79
    inst_btg,    #7A
    inst_btg,    #7B
    inst_btg,    #7C
    inst_btg,    #7D
    inst_btg,    #7E
    inst_btg,    #7F
    inst_bsf,    #80
    inst_bsf,    #81
    inst_bsf,    #82
    inst_bsf,    #83
    inst_bsf,    #84
    inst_bsf,    #85
    inst_bsf,    #86
    inst_bsf,    #87
    inst_bsf,    #88
    inst_bsf,    #89
    inst_bsf,    #8A
    inst_bsf,    #8B
    inst_bsf,    #8C
    inst_bsf,    #8D
    inst_bsf,    #8E
    inst_bsf,    #8F
    inst_bcf,    #90
    inst_bcf,    #91
    inst_bcf,    #92
    inst_bcf,    #93
    inst_bcf,    #94
    inst_bcf,    #95
    inst_bcf,    #96
    inst_bcf,    #97
    inst_bcf,    #98
    inst_bcf,    #99
    inst_bcf,    #9A
    inst_bcf,    #9B
    inst_bcf,    #9C
    inst_bcf,    #9D
    inst_bcf,    #9E
    inst_bcf,    #9F
    inst_btfss,    #A0
    inst_btfss,    #A1
    inst_btfss,    #A2
    inst_btfss,    #A3
    inst_btfss,    #A4
    inst_btfss,    #A5
    inst_btfss,    #A6
    inst_btfss,    #A7
    inst_btfss,    #A8
    inst_btfss,    #A9
    inst_btfss,    #AA
    inst_btfss,    #AB
    inst_btfss,    #AC
    inst_btfss,    #AD
    inst_btfss,    #AE
    inst_btfss,    #AF
    inst_btfsc,    #B0
    inst_btfsc,    #B1
    inst_btfsc,    #B2
    inst_btfsc,    #B3
    inst_btfsc,    #B4
    inst_btfsc,    #B5
    inst_btfsc,    #B6
    inst_btfsc,    #B7
    inst_btfsc,    #B8
    inst_btfsc,    #B9
    inst_btfsc,    #BA
    inst_btfsc,    #BB
    inst_btfsc,    #BC
    inst_btfsc,    #BD
    inst_btfsc,    #BE
    inst_btfsc,    #BF
    inst_reserved,    #C0
    inst_reserved,    #C1
    inst_reserved,    #C2
    inst_reserved,    #C3
    inst_reserved,    #C4
    inst_reserved,    #C5
    inst_reserved,    #C6
    inst_reserved,    #C7
    inst_reserved,    #C8
    inst_reserved,    #C9
    inst_reserved,    #CA
    inst_reserved,    #CB
    inst_reserved,    #CC
    inst_reserved,    #CD
    inst_reserved,    #CE
    inst_reserved,    #CF
    inst_bra,    #D0
    inst_bra,    #D1
    inst_bra,    #D2
    inst_bra,    #D3
    inst_bra,    #D4
    inst_bra,    #D5
    inst_bra,    #D6
    inst_bra,    #D7
    inst_rcall,    #D8
    inst_rcall,    #D9
    inst_rcall,    #DA
    inst_rcall,    #DB
    inst_rcall,    #DC
    inst_rcall,    #DD
    inst_rcall,    #DE
    inst_rcall,    #DF
    inst_bz,    #E0
    inst_bz,    #E1
    inst_bnz,    #E2
    inst_bnz,    #E3
    inst_bc,    #E4
    inst_bc,    #E5
    inst_bnc,    #E6
    inst_bnc,    #E7
    inst_bov,    #E8
    inst_bov,    #E9
    inst_bnov,    #EA
    inst_bnov,    #EB
    inst_bn,    #EC
    inst_bn,    #ED
    inst_bnn,    #EE
    inst_bnn,    #EF
    inst_check_prev,    #F0
    inst_check_prev,    #F1
    inst_check_prev,    #F2
    inst_check_prev,    #F3
    inst_check_prev,    #F4
    inst_check_prev,    #F5
    inst_check_prev,    #F6
    inst_check_prev,    #F7
    inst_check_prev,    #F8
    inst_check_prev,    #F9
    inst_check_prev,    #FA
    inst_check_prev,    #FB
    inst_check_prev,    #FC
    inst_check_prev,    #FD
    inst_check_prev,    #FE
    inst_check_prev,    #FF
]

    
def gen_pic16_inst_table():
    inst_table = []
    
    for msb in range(256):
        inst_table.append('inst_reserved')
        
        v0 = (msb >> 4) & 0xf #bit 13, 12
        v1 = msb & 0xf        #bit 11, 10, 9, 8

        if msb == 0x00:
            inst_table[msb] = 'inst_msb_0'

        elif v0 == 0x0:
            if v1 == 1:
                inst_table[msb] = 'inst_movlb'
            elif v1 == 2 or v1 == 3:
                inst_table[msb] = 'inst_mulwf'
            elif v1 >= 4 and v1 <= 7:
                inst_table[msb] = 'inst_decf'
            elif v1 == 0xE:
                inst_table[msb] = 'inst_movlw'
        elif v0 == 0x1:
            lst = ['iorwf', 'andwf', 'xorwf', 'comf']
            inst_table[msb] = 'inst_' + lst[v1 >> 2]
        elif v0 == 2:
            lst = ['ADDWFC', 'ADDWF', 'INCF', 'DECFSZ']
            inst = lst[v1 >> 2]
            inst_table[msb] = 'inst_' + inst
        elif v0 == 0x3:
            lst = ['ADDWFC', 'ADDWF', 'INCF', 'DECFSZ']
            inst = lst[v1 >> 2]
            inst_table[msb] = 'inst_' + inst
        elif v0 == 0x4:
            lst = ['RRNCF', 'RLNCF', 'INFSNZ', 'DCFSNZ']
            inst = lst[v1 >> 2]
            inst_table[msb] = 'inst_' + inst
        elif v0 == 0x5:
            lst = ['MOVF', 'SUBFWB', 'SUBWFB', 'SUBWF']
            inst = lst[v1 >> 2]
            inst_table[msb] = 'inst_' + inst
        elif v0 == 0x6:
            lst = ['CPFSLT', 'CPFSEQ', 'CPFSGT', 'TSTFSZ', 'SETF', 'CLRF', 'NEGF', 'MOVWF']
            inst = lst[v1 >> 1]
            inst_table[msb] = 'inst_' + inst
        elif v0 >= 0x7 and v0 <= 0xB:
            lst = ['BTG', 'BSF', 'BCF', 'BTFSS', 'BTFSC']
            inst = lst[v0 - 0x7]
            inst_table[msb] = 'inst_' + inst
        elif v0 == 0xC:
            inst = 'MOVFF'
        elif v0 == 0xD:
            lst = ['BRA', 'RCALL']
            inst = lst[v1 >> 3]
            inst_table[msb] = 'inst_' + inst
        elif v0 == 0xE:
            lst = ['BZ', 'BNZ', 'BC', 'BNC', 'BOV', 'BNOV', 'BN', 'BNN', 
                   'reserved','reserved','reserved','reserved',
                   'CALL', 'CALL', 'LFSR'
                   ]
            inst = lst[v1 >> 1]
            inst_table[msb] = 'inst_' + inst
        elif v0 == 0xF:
            inst_table[msb] = 'inst_check_prev'
    
    print 'inst_table = ['
    for i in range(256):
        print inst_table[i].lower() + ',    #' + utils.tohex(i, 2)
        
    #print ']'
    #lst = []
    #for t in inst_table:
        #if not t in lst:
            #lst.append(t)
    
    #for t in lst:
        #print 'def ' + t.lower() + '(sim, msb, lsb):\n    pass\n'
    
    #return inst_table 
    

#----------------------------------------------------------------------------
def get_pic16_inst_str(v, msb, lsb):
    v0 = (msb >> 4) & 0xf #bit 13, 12
    v1 = msb & 0xf        #bit 11, 10, 9, 8
    v2 = (lsb >> 4) & 0xf
    v3 = lsb & 0xf    
    
    inst = ' - '
    if msb == 0x00:
        lst = ['nop', '', '', 'sleep', 'clrwdt', 'push', 'pop', 'daw c', 
               'tblrd*', 'tblrd*+', 'tblrd*-', 'tblrd+*',
               'tblwr*', 'tblwr*+', 'tblwr*-', 'tblwr+*',
               'retfie', 'retfie_fast', 'return', 'return_fast',]
        if lsb < len(lst):
            inst = lst[lsb]
        elif lst == 0xff:
            inst = 'reset'
    elif v0 == 0x0:
        if v1 == 1:
            inst = 'movlb'
            k = get_bits(v, 0, 3)
            inst += ' ' + hex(k)
        elif v1 == 2 or v1 == 3:
            a = get_bit(v, 8)
            f = lsb            
            inst = 'mulwf ' + hex(f) + ', ' + str(a)
        elif v1 >= 4 and v1 <= 7:
            d = get_bit(v, 9)
            a = get_bit(v, 8)
            f = lsb            
            inst = 'decf ' + hex(f) + ', ' + hex(d) + ', ' + str(a)
        elif v1 == 0xE:
            inst = 'movlw ' + hex(lsb)
            
    elif v0 == 0x1:
        lst = ['iorwf', 'andwf', 'xorwf', 'comf']
        inst = lst[v1 >> 2]
        d = get_bit(v, 9)
        a = get_bit(v, 8)
        f = lsb
        inst += ' ' + hex(f) + ', ' + hex(d) + ', ' + str(a)
    elif v0 == 2:
        lst = ['ADDWFC', 'ADDWF', 'INCF', 'DECFSZ']
        inst = lst[v1 >> 2]
        d = get_bit(v, 9)
        a = get_bit(v, 8)
        f = lsb
        inst += ' ' + hex(f) + ', ' + hex(d) + ', ' + str(a)
    elif v0 == 0x3:
        lst = ['ADDWFC', 'ADDWF', 'INCF', 'DECFSZ']
        inst = lst[v1 >> 2]
        d = get_bit(v, 9)
        a = get_bit(v, 8)
        f = lsb
        inst += ' ' + hex(f) + ', ' + hex(d) + ', ' + str(a)
    elif v0 == 0x4:
        lst = ['RRNCF', 'RLNCF', 'INFSNZ', 'DCFSNZ']
        inst = lst[v1 >> 2]
        d = get_bit(v, 9)
        a = get_bit(v, 8)
        f = lsb
        inst += ' ' + hex(f) + ', ' + hex(d) + ', ' + str(a)
    elif v0 == 0x5:      
        lst = ['MOVF', 'SUBFWB', 'SUBWFB', 'SUBWF']
        inst = lst[v1 >> 2]
        d = get_bit(v, 9)
        a = get_bit(v, 8)
        f = lsb
        inst += ' ' + hex(f) + ', ' + hex(d) + ', ' + str(a)
    elif v0 == 0x6:
        lst = ['CPFSLT', 'CPFSEQ', 'CPFSGT', 'TSTFSZ', 'SETF', 'CLRF', 'NEGF', 'MOVWF']
        inst = lst[v1 >> 1]
        f = lsb
        a = get_bit(v, 8)
        inst += ' ' + hex(f) + ', ' + str(a)
    elif v0 >= 0x7 and v0 <= 0xB:
        lst = ['BTG', 'BSF', 'BCF', 'BTFSS', 'BTFSC']
        inst = lst[v0 - 0x7]
        b = get_bits(v, 9, 11)
        a = get_bit(v, 8)
        f = lsb
        inst += ' ' + hex(f) + ', ' + hex(b) + ', ' + str(a)
    elif v0 == 0xC:
        inst = 'MOVFF'
    elif v0 == 0xD:
        lst = ['BRA', 'RCALL']
        inst = lst[v1 >> 3]
        n = get_bits(v, 0, 10)
        inst += ' ' + hex(n)
    elif v0 == 0xE:
        lst = ['BZ', 'BNZ', 'BC', 'BNC', 'BOV', 'BNOV', 'BN', 'BNN', 
               'reserved','reserved','reserved','reserved',
               'CALL', 'CALL', 'LFSR'
               ]
        inst = lst[v1 >> 1]
        
    elif v0 == 0xF:
        inst = 'depend on previous '
        
    return inst.lower()

#---- for testing -------------------------------------------------------------
if __name__ == '__main__':    
    gen_pic16_inst_table()