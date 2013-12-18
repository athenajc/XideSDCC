import os
import sys

from utils import *
from pic14_inst import *

#----------------------------------------------------------------------------
def test_return(sim):
    sim.log("\n######################## inst_return\n")
    sim.ret()

#----------------------------------------------------------------------------
def test_retfie(sim):
    sim.retfie()

#----------------------------------------------------------------------------
def test_option(sim):
    pass

#----------------------------------------------------------------------------
def test_sleep(sim):
    pass

#----------------------------------------------------------------------------
def test_clrwdt(sim):
    pass

#----------------------------------------------------------------------------
def test_tris1(sim, full_test):
    w = sim.get_wreg()
    sim.set_sfr('trisa', w)

#----------------------------------------------------------------------------
def test_tris2(sim, full_test):
    w = sim.get_wreg()
    sim.set_sfr('trisb', w)    

#----------------------------------------------------------------------------
def test_tris3(sim, full_test):
    w = sim.get_wreg()
    sim.set_sfr('trisc', w)    

#----------------------------------------------------------------------------
def test_movwf(sim, full_test):
    #00 : 0000 0000 1fff ffff  MOVWF f   f <- W
    #
    # f : Register file addesss ( 00(00h) to 127(7Fh) )
    # d always = 1, store result in f    
    f = lsb & 0x7f
    w = sim.get_wreg()
    sim.set_freg(f, w)

#----------------------------------------------------------------------------
def test_clrf(sim, full_test):
    #01 : 0000 0001 dfff ffff  CLR f,d(bit 7)  Z dest <- 0, usually written CLRW or CLRF f
    d = (lsb >> 7) & 1
    f = lsb & 0x7f
    sim.set_z(1)
    if d == 0:
        sim.set_wreg(0)
    else:
        sim.set_freg(f, 0)
        
#----------------------------------------------------------------------------
def test_subwf(sim, full_test):
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
    func = inst_subwf
    op = 0x02
    
    lst = [
        [5, 0x3, 0xff, 1],
        [5, 0x2, 0x00, 1],
        [5, 0xf, 0xf, 0],
        [5, 0x0, 0, 1],
        [5, 0xff, 0xff, 1],
        [6, 3, 2, 0],
        [6, 2, 3, 0],
        [6, 0xfe, 0xf7, 0],
        [13, 0x80, 0x81, 0],
        [14, 0x81, 0x80, 1],
    ]
    if full_test:
        for w in range(256):
            for f in range(256):
                lst.append([5, f, w, 1])
                #v1 = (f + 0x100 - w) & 0xff
                #v1 = val8(v1)
                #if f - w != v1:
                #    print f, w, f - w, (f + 0x100 - w) & 0xff
    error = 0
    for t in lst:
        err = False
        f = t[0]
        v0 = t[1]
        w0 = t[2]
        d = t[3]
        
        sim.set_freg(f, v0)

        sim.set_wreg(w0)
        
        msb = op
        lsb = (d << 7) | f
        
        func = inst_handler[msb]
        func(sim, msb, lsb)
               
        w1 = sim.get_wreg()
        v1 = sim.get_freg(f)
        fv1 = (v0 + 0x100 - w0) & 0xff
        
        if d == 0:
            if w1 != fv1:
                err = True
                print "w1 %x != fv1 %x" % (w1, fv1)
            if v1 != v0:
                err = True
                print "v1 %x != v0 %x" % (v1, v0)
        else:
            if v1 != fv1:
                err = True
                print "v1 %x != fv1 %x" %(v1, fv1)
            if w1 != w0:
                err = True
                print "w1 %x != w0 %x"% (w1, w0)
                
        print 'f' + tohex(f, 2), 
        print 'v0=' + tohex(v0, 2),
        print 'w0=' + tohex(w0, 2),
        print 'd' + str(d),
        if d == 0:
            print 'w='+ tohex(fv1, 2),
        else:
            print 'f='+ tohex(fv1, 2),
        
        print 'v1=' + tohex(v1, 2),
        print 'w1=' + tohex(w1, 2),
        print 'c=' + str(sim.get_c()),
        print 'dc=' + str(sim.get_dc()),
        print 'z=' + str(sim.get_z()),
        
        if fv1 == 0 and sim.get_z() != 1:
            err  = True
        if fv1 != 0 and sim.get_z() == 1:
            err  = True
            
        if err:
            error += 1
            print ''
        else:
            print ' ok'
            

    print 'Error count = ', error
    return error

#----------------------------------------------------------------------------
def test_decf(sim, full_test):
    #03 : 0000 0011 dfff ffff  DECF f,d  Z dest <- f-1
    #f : Register file addesss ( 00(00h) to 127(7Fh) )
    #d : Destination select ( 0 or 1 )    
    #d = 0 : store result in W
    #d = 1 : store result in f
    #When the result is 0, it sets 1 to the Z flag.
    #When the result is not 0, it sets 0 to the Z flag.    
    func = inst_decf
    op = 0x03
    
    lst = [
        [5, 0x3, 1],
        [5, 0x2, 1],
        [5, 0x1, 1],
        [5, 0x0, 1],
        [5, 0xff, 1],
        [6, 0, 0],
        [6, 0x11, 0],
        [6, 0xff, 0],
        [13, 0xfe, 0],
        [14, 0x0, 1],
    ]
    
    if full_test:
        for f in range(128):
            for v in range(256):
                for d in range(2):
                    lst.append([f, v, d])
        
    error = 0
    for t in lst:
        err = False
        f = t[0]
        v = t[1]
        d = t[2]
        
        sim.set_freg(f, v)

        w0 = sim.get_wreg()
        
        msb = op
        lsb = (d << 7) | f
        
        func = inst_handler[msb]
        func(sim, msb, lsb)
               
        w1 = sim.get_wreg()
        v1 = sim.get_freg(f)
        fv1 = (v + 0x100 - 1) & 0xff
        
        if d == 0:
            if w1 != fv1:
                err = True
                print "w1 != fv1"
            if v1 != v:
                err = True
                print "v1 != v0"
        else:
            if v1 != fv1:
                err = True
                print "v1 != fv1"
            if w1 != w0:
                err = True
                print "w1 != w0"
                
        print 'f' + tohex(f, 2), 
        print 'v' + tohex(v, 2),
        print 'd' + str(d),
        if d == 0:
            print 'w',
        else:
            print 'f',
            
        print 'v1=' + tohex(v1, 2),
        print 'w1=' + tohex(w1, 2),
        print 'z=' + str(sim.get_z()),
        
        if fv1 == 0 and sim.get_z() != 1:
            err  = True
        if fv1 != 0 and sim.get_z() == 1:
            err  = True
            
        if err:
            error += 1
            print ''
        else:
            print ' ok'
            

    print 'Error count = ', error
    return error
        
#----------------------------------------------------------------------------
def test_iorwf(sim, full_test):
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
    sim.clear_status_reg_flags()
    if v == 0:
        sim.set_z(1)
    
    if d == 0:
        sim.set_wreg(v)
    else:
        sim.set_freg(f, v)

#----------------------------------------------------------------------------
def test_andwf(sim, full_test):
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
def test_xorwf(sim, full_test):
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
def test_addwf(sim, full_test):
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
        
    if (v & 0xf) + (w & 0xf) > 0xf:
        dc = 1
        
    if v == 0:
        z = 1

    sim.set_c(c)
    sim.set_z(z)
    sim.set_dc(dc)
    
    if d == 0:
        sim.set_wreg(v)
    else:
        sim.set_freg(f, v)
        
#----------------------------------------------------------------------------
def test_movf(sim, full_test):
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
    sim.clear_status_reg_flags()
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
def test_comf(sim, full_test):
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
    sim.clear_status_reg_flags()
    if v == 0:
        sim.set_z(1)
    
    if d == 0:
        sim.set_wreg(v)
    else:
        sim.set_freg(f, v)
    
#----------------------------------------------------------------------------
def test_incf(sim, full_test):
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
    func = inst_incf
    op = 0x0a
    
    lst = [
        [5, 0x1, 1],
        [5, 0x2, 1],
        [5, 0x3, 1],
        [5, 0x4, 1],
        [5, 0xff, 1],
        [6, 0, 0],
        [6, 0x11, 0],
        [6, 0xff, 0],
        [13, 0xfe, 0],
        [14, 0xff, 1],
    ]
    
    if full_test:
        for f in range(128):
            for v in range(256):
                for d in range(2):
                    lst.append([f, v, d])
        
    error = 0
    for t in lst:
        err = False
        f = t[0]
        v = t[1]
        d = t[2]
        
        sim.set_freg(f, v)

        w0 = sim.get_wreg()
        
        msb = op
        lsb = (d << 7) | f
        
        func = inst_handler[msb]
        func(sim, msb, lsb)
        
       
        w1 = sim.get_wreg()
        v1 = sim.get_freg(f)
        fv1 = (v + 1) & 0xff
        
        if d == 0:
            if w1 != fv1:
                err = True
                print "w1 != fv1"
            if v1 != v:
                err = True
                print "v1 != v0"
        else:
            if v1 != fv1:
                err = True
                print "v1 != fv1"
            if w1 != w0:
                err = True
                print "w1 != w0"
                
        print 'f' + tohex(f, 2), 
        print 'v' + tohex(v, 2),
        print 'd' + str(d),
        if d == 0:
            print 'w',
        else:
            print 'f',
            
        print 'v1=' + tohex(v1, 2),
        print 'w1=' + tohex(w1, 2),
        
        if err:
            error += 1
            print ''
        else:
            print ' ok'
            

    print 'Error count = ', error
    return error

#----------------------------------------------------------------------------
def test_decfsz(sim, full_test):
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
    func = inst_decfsz
    op = 0x0b
    
    lst = [
        [5, 0x04, 1],
        [5, 0x03, 1],
        [5, 0x02, 1],
        [5, 0x01, 1],
        [5, 0x00, 1],
        [6, 0x00, 0],
        [6, 0x11, 1],
        [6, 0xff, 0],
        [13, 0xfe, 0],
        [14, 0x01, 1],
    ]
    
    if full_test:
        for f in range(128):
            for v in range(256):
                for d in range(2):
                    lst.append([f, v, d])
        
    error = 0
    for t in lst:
        err = False
        f = t[0]
        v = t[1]
        d = t[2]
        
        sim.set_freg(f, v)
        
        pc0 = sim.pc
        w0 = sim.get_wreg()
        
        msb = op
        lsb = (d << 7) | f
        
        func = inst_handler[msb]
        func(sim, msb, lsb)
        
        pc1 = sim.pc
        offset = pc1 - pc0
        
        w1 = sim.get_wreg()
        v1 = sim.get_freg(f)
        fv1 = (v + 0x100 - 1) & 0xff
        
        # dest <- f-1, then skip if zero  
        if fv1 == 0 and offset == 0:
            err = True
            print 'should skip'
        if fv1 < 0 and offset != 0:
            err = True
            print 'should not skip'
            
        if d == 0:
            if w1 != fv1:
                err = True
                print "w1 != fv1"
            if v1 != v:
                err = True
                print "v1 != v0"
        else:
            if v1 != fv1:
                err = True
                print "v1 != fv1"
            if w1 != w0:
                err = True
                print "w1 != w0"
                
        print 'f' + tohex(f, 2), 
        print 'v' + tohex(v, 2),
        print 'd' + str(d),
        if d == 0:
            print 'w',
        else:
            print 'f',
            
        print 'v1=' + tohex(v1, 2),
        print 'w1=' + tohex(w1, 2),
        print 'pc', tohex(pc0, 2), tohex(pc1, 2), 
        if offset == 1:
            print 'skip'
        else:
            print ''
        
        if err:
            error += 1

    print 'Error count = ', error
    return error

#----------------------------------------------------------------------------
def test_rrf(sim, full_test):
    #0c : 0000 1100 dfff ffff  RRF f,d C  dest <- CARRY<<7 | f>>1, rotate right through carry
    #   c -> f7 f0 -> c
    # d = 0 : store result in W
    # d = 1 : store result in f
    func = inst_rrf
    op = 0x0c
    
    lst = [
        [5, 0x1, 1],
        [5, 0x2, 1],
        [5, 0x3, 1],
        [5, 0x4, 1],
        [5, 0xff, 1],
        [6, 0, 0],
        [6, 0x11, 0],
        [6, 0xff, 0],
        [13, 0xfe, 0],
        [14, 0xff, 1],
    ]
    
    if full_test:
        for f in range(128):
            for v in range(256):
                for d in range(2):
                    lst.append([f, v, d])
        
    error = 0
    for t in lst:
        err = False
        f = t[0]
        v = t[1]
        d = t[2]
        
        sim.set_freg(f, v)
        c = sim.get_c()
        w0 = sim.get_wreg()
        
        msb = op
        lsb = (d << 7) | f
        
        func = inst_handler[msb]
        func(sim, msb, lsb)

        w1 = sim.get_wreg()
        v1 = sim.get_freg(f)
        
        #dest <- CARRY<<7 | f>>1,
        fv1 = (c << 7) | (v >> 1) 
        
        if d == 0:
            if w1 != fv1:
                err = True
                print "w1 != fv1"
            if v1 != v:
                err = True
                print "v1 != v0"
        else:
            if v1 != fv1:
                err = True
                print "v1 != fv1"
            if w1 != w0:
                err = True
                print "w1 != w0"
                
        print 'f' + tohex(f, 2), 
        print 'v' + tohex(v, 2),
        print 'd' + str(d),
        if d == 0:
            print 'w',
        else:
            print 'f',
            
        print 'v1=' + tohex(v1, 2),
        print 'w1=' + tohex(w1, 2),
        
        if err:
            error += 1
            print ''
        else:
            print ' ok'
            

    print 'Error count = ', error
    return error

#----------------------------------------------------------------------------
def test_rlf(sim, full_test):
    #0d : 0000 1101 dfff ffff  RLF f,d C  dest <- f<<1 | CARRY, rotate left through carry
    #  c <- f7 f0 <- c
    # d = 0 : store result in W
    # d = 1 : store result in f    
    d = (lsb >> 7) & 1
    f = lsb & 0x7f
    v = sim.get_freg(f)
    bit7 = (v >> 7) & 1
    c = sim.get_c()
    v = ((v << 1) & 0xff) | c
    sim.set_c(bit7)
    if d == 0:
        sim.set_wreg(v)
    else:
        sim.set_freg(f, v)

#----------------------------------------------------------------------------
def test_swapf(sim, full_test):
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
def test_incfsz(sim, full_test):
    #0f : 0000 1111 dfff ffff  INCFSZ f,d   dest <- f+1, then skip if zero   
    func = inst_incfsz
    op = 0x0f
    
    lst = [
        [5, 0xff, 1],
        [6, 0, 0],
        [6, 0x11, 0],
        [6, 0xff, 0],
        [13, 0xfe, 0],
        [14, 0xff, 1],
    ]
    
    if full_test:
        for f in range(128):
            for v in range(256):
                for d in range(2):
                    lst.append([f, v, d])
        
    error = 0
    for t in lst:
        err = False
        f = t[0]
        v = t[1]
        d = t[2]
        
        sim.set_freg(f, v)
        
        pc0 = sim.pc
        w0 = sim.get_wreg()
        
        msb = op
        lsb = (d << 7) | f
        
        func = inst_handler[msb]
        func(sim, msb, lsb)
        
        pc1 = sim.pc
        offset = pc1 - pc0
        
        # dest <- f+1, then skip if zero  
        if v == 0xff and offset == 0:
            err = True
            print 'should skip'
        if v < 0xff and offset != 0:
            err = True
            print 'should not skip'
        
        w1 = sim.get_wreg()
        v1 = sim.get_freg(f)
        fv1 = (v + 1) & 0xff
        
        if d == 0:
            if w1 != fv1:
                err = True
                print "w1 != fv1"
            if v1 != v:
                err = True
                print "v1 != v0"
        else:
            if v1 != fv1:
                err = True
                print "v1 != fv1"
            if w1 != w0:
                err = True
                print "w1 != w0"
                
        print 'f' + tohex(f, 2), 
        print 'v' + tohex(v, 2),
        print 'd' + str(d),
        if d == 0:
            print 'w',
        else:
            print 'f',
            
        print 'v1=' + tohex(v1, 2),
        print 'w1=' + tohex(w1, 2),
        print 'pc', tohex(pc0, 2), tohex(pc1, 2), 
        if offset == 1:
            print 'skip'
        else:
            print ''
        
        if err:
            error += 1

    print 'Error count = ', error
    return error
        
#----------------------------------------------------------------------------
def test_bcf(sim, full_test):
    #10 : 0001 00bb bfff ffff  bit(3, b7-b9) f(7, b0-b6) BCF f,b   Clear bit b of f
    func = inst_bcf
    op = 0x10
    
    lst = [
        [3, 5, 0], [3, 6, 0],
        [3, 5, 0], [3, 6, 1],
        [3, 5, 1], [3, 6, 0],
        [3, 5, 1], [3, 6, 1],
        [6, 2, 1], 
        [0x3f, 7, 0],
    ]
    
    if full_test:
        for f in range(127):
            for b in range(8):
                for v in range(2):
                    lst.append([f, b, v])
        
    error = 0
    for t in lst:
        err = False
        f = t[0]
        b = t[1]
        v = t[2]
        
        # preset test bit 
        fv = sim.get_freg(f)
        if v == 1:
            fv = set_bit(fv, b)
        else:
            fv = clear_bit(fv, b)
        sim.set_freg(f, fv)
        
        # get msb and lsb
        lsb = ((b & 1) << 7) | f
        msb = op | (b >> 1)
        
        func = inst_handler[msb]
        func(sim, msb, lsb)
        
        fv1 = sim.get_freg(f)
        v1 = get_bit(fv1, b)
        
        print 'bit' + str(b), 
        print 'v' + str(v),
        print 'v1=' + str(v1),
        print 'bank=' + hex(sim.bank_addr),
        # bcf : Clear bit b of f
        if v1 == 1:
            err = True
            print ' bit ' + str(b) +  ' not clear'
        else:
            print ' bit clear ok'
            
        if err:
            error += 1

    print 'Error count = ', error
    return error

#----------------------------------------------------------------------------
def test_bsf(sim, full_test):
    #14 : 0001 01bb bfff ffff  BSF f,b   Set bit b of f
    func = inst_bsf
    op = 0x14
    
    lst = [
        [3, 5, 0], [3, 6, 0],
        [3, 5, 0], [3, 6, 1],
        [3, 5, 1], [3, 6, 0],
        [3, 5, 1], [3, 6, 1],
        [6, 2, 1], 
        [0x3f, 7, 0],
    ]
    
    if full_test:
        for f in range(127):
            for b in range(8):
                for v in range(2):
                    lst.append([f, b, v])
        
    error = 0
    for t in lst:
        err = False
        f = t[0]
        b = t[1]
        v = t[2]
        
        # preset test bit 
        fv = sim.get_freg(f)
        if v == 1:
            fv = set_bit(fv, b)
        else:
            fv = clear_bit(fv, b)
        sim.set_freg(f, fv)
        
        # get msb and lsb
        lsb = ((b & 1) << 7) | f
        msb = op | (b >> 1)
        
        func = inst_handler[msb]
        func(sim, msb, lsb)
        
        fv1 = sim.get_freg(f)
        v1 = get_bit(fv1, b)
        
        print 'bit' + str(b), 
        print 'v' + str(v),
        print 'v1=' + str(v1),
        print 'bank=' + hex(sim.bank_addr),
        # bsf : Set bit b of f
        if v1 == 0:
            err = True
            print ' bit ' + str(b) +  ' not set'
        else:
            print ' bit set ok'
            
        if err:
            error += 1

    print 'Error count = ', error
    return error
        
#----------------------------------------------------------------------------
def test_btfsc(sim, full_test):
    #18 : 0001 10bb bfff ffff  BTFSC f,b   Skip if bit b of f is clear
    func = inst_btfsc
    op = 0x18
    
    lst = [
        [3, 0, 0],   # c
        [3, 0, 1],
        [3, 2, 1],   # z
        [3, 2, 0],
    ]
    
    if full_test:
        for b in range(8):
            for v in range(2):
                lst.append([3, b, v])
        
    error = 0
    for t in lst:
        err = False
        f = t[0]
        b = t[1]
        v = t[2]
        
        sim.set_status_reg(b, v)
        #print 'status reg', sim.get_freg(3)
        pc0 = sim.pc
        
        lsb = ((b & 1) << 7) | f
        msb = op | (b >> 1)
        
        func = inst_handler[msb]
        func(sim, msb, lsb)
        
        pc1 = sim.pc
        offset = pc1 - pc0
        
        # Skip if bit b of f is clear
        if v == 1 and offset != 0:
            err = True
            print 'bit is set, should not skip'
        if v == 0 and offset == 0:
            err = True
            print 'bit is clear, should skip'
        
        print 'bit' + str(b), 
        print 'v' + str(v),
        print 'pc', tohex(pc0, 2), tohex(pc1, 2), 
        if offset == 1:
            print 'skip'
        else:
            print ''
        
        if err:
            error += 1

    print 'Error count = ', error
    return error

#----------------------------------------------------------------------------
def test_btfss(sim, full_test):
    #1c : 0001 11bb bfff ffff  BTFSS f,b   Skip if bit b of f is set
    func = inst_btfss
    op = 0x1c
    
    lst = [
        [3, 0, 0],   # c
        [3, 0, 1],
        [3, 2, 1],   # z
        [3, 2, 0],
    ]
    
    if full_test:
        for b in range(8):
            for v in range(2):
                lst.append([3, b, v])
        
    error = 0
    for t in lst:
        err = False
        f = t[0]
        b = t[1]
        v = t[2]
        
        sim.set_status_reg(b, v)
        #print 'status reg', sim.get_freg(3)
        pc0 = sim.pc
        lsb = ((b & 1) << 7) | f
        msb = op | (b >> 1)
        
        func(sim, msb, lsb)
        
        pc1 = sim.pc
        offset = pc1 - pc0
        
        # Skip if bit b of f is set
        if v == 0 and offset != 0:
            err = True
            print 'bit not set, should not skip'
        if v == 1 and offset == 0:
            err = True
            print 'bit is set, should skip'
        
        print 'bit' + str(b), 
        print 'v' + str(v),
        print 'pc', tohex(pc0, 2), tohex(pc1, 2), 
        if offset == 1:
            print 'skip'
        else:
            print ''
        
        if err:
            error += 1

    print 'Error count = ', error
    return error


#----------------------------------------------------------------------------
def test_call(sim, full_test):
    #20 : 0010 0kkk kkkk kkkk CALL k   Call subroutine
    func = inst_call
    msb = 0x20

#----------------------------------------------------------------------------
def test_goto(sim, full_test):
    #28 : 0010 1kkk kkkk kkkk  GOTO k   Jump to address k 
    func = inst_goto
    msb = 0x28
    

#----------------------------------------------------------------------------
def test_movlw(sim, full_test):
    #30 : 0011 00xx kkkk kkkk MOVLW k   W <- k
    func = inst_movlw
    msb = 0x30
    
    lst = []
    for i in range(256):
        lst.append(i)
        
    error = 0
    for t in lst:
        k = lsb = t
        
        func(sim, msb, lsb)
        
        result = "%02X" % sim.get_wreg()
               
        w1 = sim.get_wreg()
        print  tohex(k, 2), result, ' ',k - w1
        if k != w1:
            error += 1
            print "******** Error ", k, w1
        
    print 'Error count = ', error
    return error

#----------------------------------------------------------------------------
def test_retlw(sim, full_test):
    #34 : 0011 01xx kkkk kkkk RETLW k   W <- k, then return from subroutine
    func = inst_retlw
    msb = 0x34
    lst = [
        [0, 0],
        [0xf, 0xf],
        [0xf0, 0x0f],
        [0x00, 0xff],
        [2, 3],
        [0x1f, 0x28],
        [0x28, 0x1f],
        [0x10, 0xf0],
        [0xff, 0x1],
        [0xff, 0xff],
        [0x90, 0x81],
        [2, 128],
        [2, 127],
        ]
    if full_test:
        for j in range(256):
            for i in range(256):
                lst.append([i, j])
    error = 0
    for t in lst:
        err = False
        addr = t[0]
        lsb = t[1]
        pc0 = sim.pc
        
        sim.push(addr)
        func(sim, msb, lsb)
        
        pc1 = sim.pc
        w = sim.get_wreg()
        print tohex(t[0], 2), tohex(t[1], 2),
        print ' pc', tohex(sim.pc, 2), 
        print ' w', tohex(w, 2)
        
        if w != lsb :
            print  "Error w != lsb"
            err = True
            
        if pc1 != addr:
            print  "Error return address set error"
            err = True
            
        if err:
            error += 1
    
    print 'RETLW Error count = ', error
    return error

#----------------------------------------------------------------------------
def test_iorlw(sim, full_test):
    #38 : 0011 1000 kkkk kkkk IORLW k  Z W <- k | W, bitwise logical or
    func = inst_iorlw
    msb = 0x38

    lst = [
        [0, 0],
        [0xf, 0xf],
        [0xf0, 0x0f],
        [0x00, 0xff],
        [2, 3],
        [0x1f, 0x28],
        [0x28, 0x1f],
        [0x10, 0xf0],
        [0xff, 0x1],
        [0xff, 0xff],
        [0x90, 0x81],
        [2, 128],
        [2, 127],
        ]
    if full_test:
        for j in range(256):
            for i in range(256):
                lst.append([i, j])
    error = 0
    for t in lst:
        w = t[0]
        k = t[1]
        
        sim.set_wreg(t[0])
        lsb = k
        #print k, w
            
        #print "%4d ^ %4d = %4d  " % (k , w, k ^ w),
        
        func(sim, msb, lsb)
        
        result = "%02X" % sim.get_wreg()
        z = '   zdc ' + str(sim.get_z())   
        dc = ' ' + str(sim.get_dc())   
        c = ' ' + str(sim.get_c())
               
        v = k | w
        #w = sim.get_wreg()
        print  z + dc + c + '   ' + tohex(k, 2), tohex(w, 2), result, ' ',v - sim.get_wreg()
        w = sim.get_wreg()
        if v != w:
            error += 1
            print "******** Error ", v, w
        
    print 'Error count = ', error
    return error
    
#----------------------------------------------------------------------------
def test_andlw(sim, full_test):
    #39 : 0011 1001 kkkk kkkk ANDLW k  Z W <- k & W, bitwise and
    func = inst_andlw
    msb = 0x39

    lst = [
        [0, 0],
        [0xf, 0xf],
        [0xf0, 0x0f],
        [0x00, 0xff],
        [2, 3],
        [0x1f, 0x28],
        [0x28, 0x1f],
        [0x10, 0xf0],
        [0xff, 0x1],
        [0xff, 0xff],
        [0x90, 0x81],
        [2, 128],
        [2, 127],
        ]
    if full_test:
        for j in range(256):
            for i in range(256):
                lst.append([i, j])

    for t in lst:
        w = t[0]
        k = t[1]
        
        sim.set_wreg(t[0])
        lsb = k
        #print k, w
            
        #print "%4d ^ %4d = %4d  " % (k , w, k ^ w),
        
        func(sim, msb, lsb)
        
        result = "%02X" % sim.get_wreg()
        z = '   zdc ' + str(sim.get_z())   
        dc = ' ' + str(sim.get_dc())   
        c = ' ' + str(sim.get_c())
               
        v = k & w
        #w = sim.get_wreg()
        print  z + dc + c + '   ' + tohex(k, 2), tohex(w, 2), result, ' ',v - sim.get_wreg()
        w = sim.get_wreg()
        if v != w:
            print "******** Error ", v, w
        
        print ''

#----------------------------------------------------------------------------
def test_xorlw(sim, full_test):
    #3a : 0011 1010 kkkk kkkk XORLW k  Z W <- k ^ W, bitwise exclusive or
    func = inst_xorlw
    msb = 0x3a
    
    lst = [
        [0, 0],
        [0xf, 0xf],
        [2, 3],
        [0x1f, 0x28],
        [0x28, 0x1f],
        [0x10, 0xf0],
        [0xff, 0x1],
        [0xff, 0xff],
        [0x90, 0x81],
        [2, 128],
        [2, 127],
        ]
    if full_test:
        for j in range(256):
            for i in range(256):
                lst.append([i, j])

    for t in lst:
        w = t[0]
        k = t[1]
        
        sim.set_wreg(t[0])
        lsb = k
        #print k, w
            
        #print "%4d ^ %4d = %4d  " % (k , w, k ^ w),
        

        func(sim, msb, lsb)
        
        result = "%02X" % sim.get_wreg()
        z = '   zdc ' + str(sim.get_z())   
        dc = ' ' + str(sim.get_dc())   
        c = ' ' + str(sim.get_c())
        v = k ^ w
        print  z + dc + c + '   ' + tohex(k, 2), tohex(w, 2), result, v - sim.get_wreg()
        
        w = sim.get_wreg()
        if v != w:
            print "******** Error ", v, w
        
        print ''

#----------------------------------------------------------------------------
def test_sublw(sim, full_test):
    #3c : 0011 110x kkkk kkkk SUBLW k C Z W <- k-W (dest <- k+~W+1)
    func = inst_sublw
    msb = 0x3c
    
    lst = [
        [0, 0],
        [3, 2],
        [2, 3],
        [-3, -2],
        [-2, -77],
        [0x1f, 0x28],
        [0x28, 0x1f],
        [0x10, 0xf0],
        [0xff, 0x1],
        [0xff, 0xff],
        [0x90, 0x81],
        [2, 128],
        [2, 127],
        ]
    if full_test:
        for j in range(256):
            for i in range(256):
                lst.append([i, j])

    for t in lst:
        w = t[0]
        k = t[1]
        
        sim.set_wreg(t[0])
        lsb = k
        #print k, w
        w = val8(w)
        k = val8(k)
            
        print "%4d - %4d = %4d  " % (k , w, k - w),
        #print tohex(w, 2) + '-' + tohex(k, 2) + '=' + "%4d" % (k - w), tohex(k - w, 2), 
        func(sim, msb, lsb)
        
        result = "%02X" % sim.get_wreg()
        z = '   zdc ' + str(sim.get_z())   
        dc = ' ' + str(sim.get_dc())   
        c = ' ' + str(sim.get_c())
        
        print  z + dc + c + '   ' + result,
        
        v = val8((k-w) & 0xff)
        w = val8(sim.get_wreg())
        print '    ', v, w
        if v != w:
            print "******** Error ", v, w
        
        print ''
    
   
#-----------------------------------------------------------------------------------
def test_addlw(sim, full_test):
    #3e : 0011 111x kkkk kkkk ADDLW k C Z W <- k+W
    func = inst_addlw
    msb = 0x3e
    
    lst = [
        [3, 2],
        [0, 0],
        [0x1f, 0x28],
        [0x10, 0xf0],
        [0xff, 0x1],
        [0xff, 0xff],
        [0x90, 0x81],
        ]
    if full_test:
        for j in range(256):
            for i in range(256):
                lst.append([i, j])
    
    for t in lst:
        w = t[0]
        l = t[1]
        sim.set_wreg(t[0])
        lsb = l
        print tohex(w, 2) + '+' + tohex(l, 2) + '=' + tohex(w + l, 2)
        func(sim, msb, lsb)
        
        w1 = sim.get_wreg()
        print tohex(w1, 2), tohex(w + l, 2), ', c',sim.get_c(), ', z', sim.get_z(), ', dc', sim.get_dc(), '\n'
        if w1 != ((w + l) & 0xff) :
            print "******** Error"
            
            
def test_hex8():
    for i in range(-128, 128, 1):
        print i, hex8(i)
        
def test_val8():
    for i in range(256):
        print hex(i), val8(i)
            
def test_all(full_test):
    test_clrf(sim, full_test)    #01
    test_subwf(sim, full_test)    #02
    test_decf(sim, full_test)    #03
    test_iorwf(sim, full_test)    #04
    test_andwf(sim, full_test)    #05
    test_xorwf(sim, full_test)    #06
    test_addwf(sim, full_test)    #07
    test_movf(sim, full_test)    #08
    test_comf(sim, full_test)    #09
    test_incf(sim, full_test)    #0A
    test_decfsz(sim, full_test)    #0B
    test_rrf(sim, full_test)    #0C
    test_rlf(sim, full_test)    #0D
    test_swapf(sim, full_test)    #0E
    test_incfsz(sim, full_test)    #0F
    test_bcf(sim, full_test)    #10-13
    test_bsf(sim, full_test)    #14-17
    test_btfsc(sim, full_test)   #18-1B
    test_btfss(sim, full_test)   #1C-1F
    test_call(sim, full_test)    #20-27
    test_goto(sim, full_test)    #28-2f
    
    
    test_movlw(sim, full_test)    #30-33
    test_retlw(sim, full_test)    
    test_iorlw(sim, full_test)
    test_andlw(sim, full_test)
    test_xorlw(sim, full_test)
    test_sublw(sim, full_test)
    test_addlw(sim, full_test)
    
#-----------------------------------------------------------------------------------
def pic14_test_inst(sim):
    full_test = True
    #full_test = False
    if full_test:
        sys.stdout = open('/home/athena/ttt/inst_test.log', 'w')

    test_subwf(sim, full_test)    
    #test_val8()



def convert_inc(fn, dst):
    text = utils.read_file(fn)
    lst = []
    for line in text.split('\n'):
        if line.startswith(';'):
            continue
        if line.find('  EQU ') > 0:
            line = line.replace('  EQU ', ';')
            t = line.split(';')
            t[0] = t[0].strip()
            t[1] = t[1].strip()
            lst.append([t[0], t[1]])
            
    f = open(dst, 'w+')
    #print >>f, 'defines = {'
    for t in lst:
        name = t[0]
        value = t[1]
        if value.find('H') >= 0: #"H'0F8C'"
            value = value.replace('H', '')
            value = value.replace('\'', '')
            value = '0x' + value
        else:
            value = hex(int(value))
        #name = '\'' + name + '\''
        print >>f, '%s:%s' % (name, value)
    #print >>f, '}'
    f.close()
    
def check_reg(fn):
    print fn
    text = utils.read_file(fn)
    for line in text.split('\n'):
        if line.startswith(';'):
            continue
        if line.find('WREG') >= 0:
            print line
        if line.find('STATUS') >= 0:
            print line
            
def convert_header_files():
    src_path = '/usr/local/share/gputils/header' + os.sep
    dst_path = os.path.dirname(os.path.realpath(__file__)) + os.sep + 'defines' + os.sep
    lst = os.listdir(src_path)
    #f = path + 'p' + dev_name + '.inc'
    #print f, os.path.exists(f)
    for f in lst:
        for d in pic14_devices:
            if f.find(d) >= 0:
                f1 = f.replace('.inc', '.sfr')
                convert_inc(src_path + f, dst_path + f1)


from pic14_sim import *
        
            
def test_sim():
    #fn = "/home/athena/src/pic14/0004/uart_tx.hex"
    #fn = "/home/athena/src/pic14/0001/test.hex"
    fn = "/home/athena/src/pic14/0001/t0001.c"
    hex_fn = fn.replace('.c', '.hex')
    #frame, hex_file, source_list, mcu_name, mcu_device
    sim = SimPic(None, hex_fn, [fn], 'pic14', '16f628a')
    sim.start()
    pic14_test_inst(sim)
            
    #for i in range(10):
    #    sim.step()    

#-------------------------------------------------------------------
def get_dev_name(fn):
    from pic14_devices import pic14_devices
    
    text = read_file(fn)
    inc_lines = ""
    for line in text.split('\n'):
        if line.find("#include") >= 0:
            inc_lines += line + '\n'
            
    text = inc_lines
    for d in pic14_devices:
        if text.find(d) >= 0:
            return d
            
    return None    
    
def test_import():
    fn = "/home/athena/src/pic14/0001/t0001.c"
    
#---- for testing -------------------------------------------------------------
if __name__ == '__main__':    
    #test_sim()
    convert_header_files()
    #set_pic14_inst_table()
    #test_import()