import os
import utils

#:BBAAAATT[DDDDDDDD]CC

# where
#  :     is start of line marker
#  BB    is number of data bytes on line
#  AAAA  is address in bytes
#  TT    is type. 00 means data, 01 means EOF and 04 means extended address
#  DD    is data bytes, number depends on BB value
#  CC    is checksum (2s-complement of number of bytes+address+data)

# Code: This is at the top of the file and may be proceeded by an extended address line - 

#    :02 0000 04 0000FA, where 04 is the type for extended address. 

# Standard Intel Hex files can only address 64KB of data, and extended addressing gets over 
# this limitation by adding extended address lines for every 64KB, for example

#    :02 0000 04 0001F9 - 64KB marker
#    :02 0000 04 0002F9 - 128KB marker

# Some compilers include empty code lines (all FF) but others omit these lines to save space.

# EEPROM Data - :0200000400F00A.
#    It is proceeded by the extended address line - 
#    :02 0000 04 00F00A. The EEPROM section is optional

# Configuration bytes: These are stored at 300000h and are preceded by the extended address line - 
#    :02 0000 04 0030CA. 
#
# The correct format is 8 Fuse bytes and 6 Lock bytes all on the same line 
# but different compilers and assemblers have different methods of displaying these bytes. 
# Sometimes lock bytes are omitted if they are not set, sometimes the data is spread over multiple lines.
# The standard format displays unused bits as 1 (e.g. FF for an unused byte) 
# but on the PIC device they read as 0. 
# A programmer should mask unused bits to 0 so that the Configuration Byte will verify correctly.

# User ID: These are bytes for the user to store data, such as code version numbers. 
# They are stored at 200000h. Again they are preceded by the extended address line 
#    :02 0000 04 0020DA. 
# The standard format requires 8 bytes but again some compilers omit unused bytes.

# End of File: The End Of File marker for all Intel Hex files is :
#    :00000001FF
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
class Obj(object):
    pass

#----------------------------------------------------------------------------
def tohex(value, n):
    return utils.tohex(value, n)

#----------------------------------------------------------------------------
def read_file(file_path):    
    return utils.read_file(file_path)
    
#----------------------------------------------------------------------------
def pic16_inst2(s):
    inst = ' '
        
    msb = int('0x' + s[0:2], 16)
    lsb = int('0x' + s[2:4], 16)
    msb1 = int('0x' + s[4:6], 16)
    lsb1 = int('0x' + s[6:8], 16)
    
    op = msb
    
    if (op & 0xC0) == 0xC0:
        #0xC? 1100 source      s of MOVFF s,d    Move absolute
        #0xF? 1111 destination d of MOVFF s, d
        src = ((msb & 0xf) << 8) | lsb
        dst = ((msb1 & 0xf) << 8) | lsb1
        inst = 'movff ' + hex(src) + ', ' + hex(dst)
        
    elif op == 0xEC or op == '0xED':
        k_msb = ((msb1 & 0xf) << 8) | lsb1
        k_lsb = lsb
        addr = (k_msb << 8) | k_lsb
        fast = msb & 1
        inst = 'call ' + hex(addr) 
        if fast:
            inst += ', fast'
        
    elif op == 0xEE:
        f = (lsb >> 4) & 3
        k_msb = lsb & 0xf
        k_lsb = lsb1
        k = (k_msb << 8) | k_lsb
        inst == 'lfsr ' + str(f) + hex(k)
        
    elif op == 0xEF:
        k_msb = ((msb1 & 0xf) << 8) | lsb1
        k_lsb = lsb
        addr = (k_msb << 8) | k_lsb
        inst = 'goto ' + hex(addr)
        
    return inst

#----------------------------------------------------------------------------
def pic16_inst(s):
    v = int('0x' + s, 16)

    msb = (v >> 8) & 0xff
    lsb = v & 0xff
    v0 = (msb >> 4) & 0xf #bit 13, 12
    v1 = msb & 0xf        #bit 11, 10, 9, 8
    v2 = (lsb >> 4) & 0xf
    v3 = lsb & 0xf    
    
    inst = ' - '
    if msb == 0x00:
        #0000 0000 0000 0000   0x0000,NOP    No operation
        #0000 0000 0000 0011   0x0003,SLEEP    Go into standby mode
        #0000 0000 0000 0100   0x0004,CLRWDT    Restart watchdog timer
        #0000 0000 0000 0101   0x0005,PUSH    Push PC on top of stack
        #0000 0000 0000 0110   0x0006,POP    Pop (and discard) top of stack
        #0000 0000 0000 0111   0x0007,DAW C   Decimal adjust W
        #0000 0000 0000 1000   0x0008,TBLRD*    Table read
        #0000 0000 0000 1001   0x0009,TBLRD*+    Table read with postincrement
        #0000 0000 0000 1010   0x000A,TBLRD*-    Table read with postdecrement
        #0000 0000 0000 1011   0x000B,TBLRD+*    Table read with pre-increment
        #0000 0000 0000 11 mod 0x000c | mod,TBLWR    Table write, same modes as TBLRD
        #0000 0000 0001 000 s  0x0010-1,RETFIE [, FAST]    Return from interrupt
        #0000 0000 0001 001 s  0x0012-3,RETURN [, FAST]    Return from subroutine
        #0000 0000 1111 1111   0x00FF,RESET cleared Software reset
        
        lst = ['nop', '', '', 'sleep', 'clrwdt', 'push', 'pop', 'daw c', 
               'tblrd*', 'tblrd*+', 'tblrd*-', 'tblrd+*',
               'tblwr*', 'tblwr*+', 'tblwr*-', 'tblwr+*',
               'retfie', 'retfie_fast', 'return', 'return_fast',]
        if lsb < len(lst):
            inst = lst[lsb]
        elif lst == 0xff:
            inst = 'reset'
    elif v0 == 0x0:
        #0x01 0000 0001 0000 k MOVLB    Move literal k to bank select register            
        #0x02-0x03 0000 001 a f MULWF f,a    PRODH:PRODL <- W x f (unsigned)
        #0x04-0x07 0000 01 d a f DECF f,d,a C Z N dest <- f - 1
        
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
        #0x10-0x13 0001 00 d a f IORWF f,d,a  Z N dest <- f | W, logical inclusive or
        #0x14-0x17 0001 01 d a f ANDWF f,d,a  Z N dest <- f & W, logical and
        #0x18-0x1b 0001 10 d a f XORWF f,d,a  Z N dest <- f ^ W, exclusive or
        #0x1c-0x1f 0001 11 d a f COMF f,d,a  Z N dest <- ~f, bitwise complement
        lst = ['iorwf', 'andwf', 'xorwf', 'comf']
        inst = lst[v1 >> 2]
        d = get_bit(v, 9)
        a = get_bit(v, 8)
        f = lsb
        inst += ' ' + hex(f) + ', ' + hex(d) + ', ' + str(a)
    elif v0 == 2:
        #0x20-0x23 0010 00 d a f ADDWFC f,d,a C Z N dest <- f + W + C
        #0x24-0x27 0010 01 d a f ADDWF f,d,a C Z N dest <- f + W
        #0x28-0x2b 0000 10 d a f INCF f,d,a C Z N dest <- f + 1
        #0x2c-0x2f 0010 11 d a f DECFSZ f,d,a    dest <- f - 1, skip if 0
        lst = ['ADDWFC', 'ADDWF', 'INCF', 'DECFSZ']
        inst = lst[v1 >> 2]
        d = get_bit(v, 9)
        a = get_bit(v, 8)
        f = lsb
        inst += ' ' + hex(f) + ', ' + hex(d) + ', ' + str(a)        
    elif v0 == 0x3:
        #0x30-0x33 0011 00 d a f RRCF f,d,a C Z N dest <- f>>1 | C<<7, rotate right through carry
        #0x34-0x37 0011 01 d a f RLCF f,d,a C Z N dest <- f<<1 | C, rotate left through carry
        #0x38-0x3b 0011 10 d a f SWAPF f,d,a    dest <- f<<4 | f>>4, swap nibbles
        #0x3c-0x3f 0011 11 d a f INCFSZ f,d,a    dest <- f + 1, skip if 0
        lst = ['ADDWFC', 'ADDWF', 'INCF', 'DECFSZ']
        inst = lst[v1 >> 2]
        d = get_bit(v, 9)
        a = get_bit(v, 8)
        f = lsb
        inst += ' ' + hex(f) + ', ' + hex(d) + ', ' + str(a)        
    elif v0 == 0x4:
        #0x40-0x43 0100 00 d a f RRNCF f,d,a  Z N dest <- f>>1 | f<<7, rotate right (no carry)
        #0x44-0x47 0100 01 d a f RLNCF f,d,a  Z N dest <- f<<1 | f>>7, rotate left (no carry)
        #0x48-0x4B 0100 10 d a f INFSNZ f,d,a    dest <- f + 1, skip if not 0
        #0x4c-0x4F 0100 11 d a f DCFSNZ f,d,a    dest <- f - 1, skip if not 0
        lst = ['RRNCF', 'RLNCF', 'INFSNZ', 'DCFSNZ']
        inst = lst[v1 >> 2]
        d = get_bit(v, 9)
        a = get_bit(v, 8)
        f = lsb
        inst += ' ' + hex(f) + ', ' + hex(d) + ', ' + str(a)        
    elif v0 == 0x5:
        #0x50-0x53 0101 00 d a f MOVF f,d,a  Z N dest <- f
        #0x54-0x57 0101 01 d a f SUBFWB f,d,a C Z N dest <- W + ~f + C (dest <- W - f - invertC)
        #0x58-0x5B 0101 10 d a f SUBWFB f,d,a C Z N dest <- f + ~W + C (dest <- f - W - invertC)
        #0x5c-0x5F 0101 11 d a f SUBWF f,d,a C Z N dest <- f - W (dest <- f + ~W + 1)        
        lst = ['MOVF', 'SUBFWB', 'SUBWFB', 'SUBWF']
        inst = lst[v1 >> 2]
        d = get_bit(v, 9)
        a = get_bit(v, 8)
        f = lsb
        inst += ' ' + hex(f) + ', ' + hex(d) + ', ' + str(a)        
    elif v0 == 0x6:
        #0x60, 0x61 0110 000 a f CPFSLT f,a    skip if f < W
        #0x62, 0x63 0110 001 a f CPFSEQ f,a    skip if f == W
        #0x64, 0x65 0110 010 a f CPFSGT f,a    skip if f > W
        #0x66, 0x67 0110 011 a f TSTFSZ f,a    skip if f == 0
        #0x68, 0x69 0110 100 a f SETF f,a      f <- 0xFF
        #0x6A, 0x6B 0110 101 a f CLRF f,a    1  f <- 0, PSR.Z <- 1
        #0x6C, 0x6D 0110 110 a f NEGF f,a    C Z N f <- -f
        #0x6E, 0x6F 0110 111 a f MOVWF f,a    f <- W        
        lst = ['CPFSLT', 'CPFSEQ', 'CPFSGT', 'TSTFSZ', 'SETF', 'CLRF', 'NEGF', 'MOVWF']
        inst = lst[v1 >> 1]
        f = lsb
        a = get_bit(v, 8)
        inst += ' ' + hex(f) + ', ' + str(a)
    elif v0 >= 0x7 and v0 <= 0xB:
        #0x7? 0111 bit a f BTG f,b,a    Toggle bit b of f
        #0x8? 1000 bit a f BSF f,b,a    Set bit b of f
        #0x9? 1001 bit a f BCF f,b,a    Clear bit b of f
        #0xA? 1010 bit a f BTFSS f,b,a    Skip if bit b of f is set
        #0xB? 1011 bit a f BTFSC f,b,a    Skip if bit b of f is clear    
        lst = ['BTG', 'BSF', 'BCF', 'BTFSS', 'BTFSC']
        inst = lst[v0 - 0x7]
        b = get_bits(v, 9, 11)
        a = get_bit(v, 8)
        f = lsb
        inst += ' ' + hex(f) + ', ' + hex(b) + ', ' + str(a)
    elif v0 == 0xC:
        #0xC? 1100 source      s of MOVFF s,d    Move absolute
        #0xF? 1111 destination d of MOVFF s, d
        inst = 'MOVFF'
    elif v0 == 0xD:
        #0xD? 1101 0 n BRA n    Branch to PC + 2n
        #0xD? 1101 1 n RCALL n    Subroutine call to PC + 2n
        lst = ['BRA', 'RCALL']
        inst = lst[v1 >> 3]
        n = get_bits(v, 0, 10) * 2
        if n & 0x800:
            n = (n & 0x7ff) - 0x800
            print 'inst_bra', n

        inst += ' ' + hex(n)
    elif v0 == 0xE:
        #0xE0  1110 0000 nnnn nnnn  BZ n    Branch if PSR.Z is set
        #0xE1  1110 0001 nnnn nnnn  BNZ n    Branch if PSR.Z is clear
        #0xE2  1110 0010 nnnn nnnn  BC n    Branch if PSR.C is set
        #0xE3  1110 0011 nnnn nnnn  BNC n    Branch if PSR.C is clear
        #0xE4  1110 0100 nnnn nnnn  BOV n    Branch if PSR.V is set
        #0xE5  1110 0101 nnnn nnnn  BNOV n    Branch if PSR.V is clear
        #0xE6  1110 0110 nnnn nnnn  BN n    Branch if PSR.N is set
        #0xE7  1110 0111 nnnn nnnn  BNN n    Branch if PSR.N is clear
        #0xE8 - 0xEB  1110 10  (reserved)
        #0xEC-0xED  1110 110 s k (lsbits) CALL k[, FAST]    Call subroutine
        #0xEE  1110 1110 00 f k (msb) LFSR f,k    Move 12-bit literal to FSRf
        lst = ['BZ', 'BNZ', 'BC', 'BNC', 'BOV', 'BNOV', 'BN', 'BNN', 
               'reserved','reserved','reserved','reserved',
               'CALL', 'CALL', 'LFSR'
               ]
        inst = lst[v1]
        
    elif v0 == 0xF:
        # Must check with prev inst
        #0xF0-0xFF  1111 k (msbits)
        
        #0xF0  1111 0000 k (lsbits)
        #0xEF 1110 1111 k (lsbits) GOTO k    Absolute jump, PC <- k
        #1111 k (msbits)
        #1111 k (No operation)    
        inst = 'inst1 '
        
    return inst

#----------------------------------------------------------------------------
def pic_hex_scan(frame, fn, mcu):
   
    text = read_file(fn)

    lst = []
    index = 0

    for line in text.split('\n'):
        if line == "":
            continue
                    
        n = len(line)
        ll   = line[1:3]
        aaaa  = line[3:7]
        tt = line[7:9]
        dd = line[9:n-2]
        cc = line[n-2:n]
        s = ll + ' ' + aaaa + ' ' + tt + '  ' + dd + '  +' + cc
        if tt == '04':
            if line.find(":020000040000FA") >= 0:
                print s, 'Extended address line'
            else:
                print s,'type = 04'
        elif tt == '01':
            if line.find(':00000001FF') >= 0:
                print s, '  End of file', line
                break
            else:
                print s, 'type = 01'
        elif tt != '00':
            print s, 'type = ' + tt
        else:
            print s
                   
        record_bytes = int("0x" + ll, 16)
        record_addr = int("0x" + aaaa, 16)
        record_type = int("0x" + tt, 16)
        #if prev_r :
        #    print tohex(prev_r.addr, 4), tohex(prev_r.bytes, 2), tohex(prev_r.addr + prev_r.bytes, 4), aaaa
        if record_type == 0 and prev_r and prev_r.addr + prev_r.bytes == record_addr and prev_r.type == 0 :
            prev_r.bytes += record_bytes
            r = prev_r
            append_to_prev = True
        else:
            r = Obj()
            r.bytes = record_bytes
            r.addr = record_addr
            r.type = record_type
            r.dd = []
            append_to_prev = False
        
        j = 9
        for i in range(record_bytes / 2):
            lsb = line[j:j+2]
            msb = line[j+2:j+4]
            op = int('0x' + msb, 16)
            if (op & 0xc0) == 0xc0:
                inst_len = 2
            elif op >= 0xEC and op <= 0xEF:
                inst_len = 2
            else:
                inst_len = 1
            
            if inst_len == 1:
                r.dd.append(msb + lsb)
                j += 4
            else:
                j += 4
                lsb1 = line[j:j+2]
                msb1 = line[j+2:j+4]
                r.dd.append(msb + lsb + msb1 + lsb1)
                j += 4
            if j >= record_bytes:
                break
        
        if append_to_prev == False:
            lst.append(r)
            prev_r = lst[index]
            index += 1
            
    fn = fn.replace('.hex', '.hex2asm')
    f = open(fn, 'w+')
    for r in lst:
        print >>f, tohex(r.addr/2,4), tohex(r.bytes,2), tohex(r.type,2) + ':'
        addr = r.addr
        for d in r.dd:
            if len(d) == 4:
                s = pic16_inst(d)
                inst_len = 2
                print >>f,tohex(addr/2,4), d + '     ', ' ' +  s.lower()
            else:
                s = pic16_inst2(d)
                inst_len = 4
                print >>f,tohex(addr/2,4), d[0:4] + ' ' + d[4:8], ' ' +  s.lower()
            addr += inst_len
            
        print >>f,""
        
    f.close()
        
    print '\n' + fn
    text = read_file(fn)
    print text
    return text
    
#----------------------------------------------------------------------------
def test_pic_hex_scan(fn):
    cfn = fn.replace('.hex', '.c')
    text = utils.read_file(cfn)
    mcu = None
    if text.find('pic16f') >= 0 or text.find('PIC16F') >= 0:
        mcu = 'pic14'
    elif text.find('pic18f') >= 0 or text.find('PIC18F') >= 0:
        mcu = 'pic16'
    else:
        print fn
        print 'Error: Cannot detect pic model'
        
    if mcu:
        print mcu, fn
        pic_hex_scan(None, fn, mcu)
    
#---- for testing -------------------------------------------------------------
if __name__ == '__main__':    
    fn = "/home/athena/src/pic/test1/test.hex"
    #fn = "/home/athena/src/pic/0004/uart_tx.hex"
    #fn = "/home/athena/src/pic/0001/test.hex"
    test_pic_hex_scan(fn)
    