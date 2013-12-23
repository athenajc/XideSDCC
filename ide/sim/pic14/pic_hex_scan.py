import os
import utils

from pic_lst_scan import pic_lst_scan

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
    
    
#-----------------------------------------------------------------------
def map_scan(fn):
    path, ext = fn.split('.')
    map_file = path + ".map"
    if not os.path.exists(map_file):
        return []
            
    text = utils.read_file(map_file)
    label_list = {}

    pos = text.find('Symbols - Sorted by Address')
    length = len(text)
    text = text[pos:length]
    for line in text.split('\n'):
        if line.find(' program ') < 0:
            continue
        #print line
        items = []
        for t in line.split(' '):
            if t == 'program':
                break
            if t != '':
                items.append(t)
        #print items
        
        addr = int(items[1], 16)
        symbol = items[0]
        label_list[addr] = symbol

    return label_list



def get_freg_name(sfr_name, f):
    if sfr_name:
        name = sfr_name.get(f, hex(f))
        return name
    return hex(f)

#----------------------------------------------------------------------------
def pic14_inst(s, map_list, sfr_name):
    v = int('0x' + s, 16)
    
    msb = (v >> 8) & 0xff
    lsb = v & 0xff
    msb = msb & 0x3f

    v0 = (msb >> 4) & 0xf #bit 13, 12
    v1 = msb & 0xf        #bit 11, 10, 9, 8
    v2 = (lsb >> 4) & 0xf
    v3 = lsb & 0xf
    f = get_bits(v, 0, 6)
    inst = ''
    if v0 == 0 and v1 == 0:
        #0000 : 0000 0000 0000 0000 : NOP   No operation (MOVW 0,W)
        #0008 : 0000 0000 0000 1000 : RETURN   Return from subroutine, W unmodified
        #0009 : 0000 0000 0000 1001 : RETFIE   Return from interrupt
        #0062 : 0000 0000 0110 0010 : OPTION   Copy W to OPTION register
        #0063 : 0000 0000 0110 0011 : SLEEP   Go into standby mode
        #0064 : 0000 0000 0110 0100 : CLRWDT   Restart watchdog timer
        #0065,0066,0067 : 0000 0000 0110 01f : TRIS f   Copy W to tri-state register (f = 1, 2 or 3)
        if lsb == 0x00: inst = '   nop'
        elif lsb == 0x08: inst = 'return'
        elif lsb == 0x09: inst = 'retfie'
        elif lsb == 0x62: inst = 'option'
        elif lsb == 0x63: inst = ' sleep'
        elif lsb == 0x64: inst = 'clrwdt'
        elif lsb == 0x65: inst = ' tris1'
        elif lsb == 0x66: inst = ' tris2'
        elif lsb == 0x67: inst = ' tris3'
        else:
            inst = ' movwf ' + get_freg_name(sfr_name, f)
    elif v0 == 0:
        # d - bit7, f bit0-6
        #00 : 0000 0000 1fff ffff  MOVWF f   f <- W
        #01 : 0000 0001 dfff ffff  CLR f,d(bit 7)  Z dest <- 0, usually written CLRW or CLRF f
        #02 : 0000 0010 dfff ffff  SUBWF f,d C Z dest <- f-W (dest <- f+~W+1)
        #03 : 0000 0011 dfff ffff  DECF f,d  Z dest <- f-1
        #04 : 0000 0100 dfff ffff  IORWF f,d  Z dest <- f | W, logical inclusive or
        #05 : 0000 0101 dfff ffff  ANDWF f,d  Z dest <- f & W, logical and
        #06 : 0000 0110 dfff ffff  XORWF f,d  Z dest <- f ^ W, logical exclusive or
        #07 : 0000 0111 dfff ffff  ADDWF f,d C Z dest <- f+W
        #08 : 0000 1000 dfff ffff  MOVF f,d  Z dest <- f
        #09 : 0000 1001 dfff ffff  COMF f,d  Z dest <- ~f, bitwise complement
        #0a : 0000 1010 dfff ffff  INCF f,d  Z dest <- f+1
        #0b : 0000 1011 dfff ffff  DECFSZ f,d   dest <- f-1, then skip if zero
        #0c : 0000 1100 dfff ffff  RRF f,d C  dest <- CARRY<<7 | f>>1, rotate right through carry
        #0d : 0000 1101 dfff ffff  RLF f,d C  dest <- f<<1 | CARRY, rotate left through carry
        #0e : 0000 1110 dfff ffff  SWAPF f,d   dest <- f<<4 | f>>4, swap nibbles
        #0f : 0000 1111 dfff ffff  INCFSZ f,d   dest <- f+1, then skip if zero        
               
        lst = [' movwf', 'clr', ' subwf', '  decf', ' iorwf', ' andwf', ' xorwf', ' addwf', 
               '  movf', '  comf', '  incf', 'decfsz', '   rrf', '   rlf',
               ' swapf', 'incfsz']
        inst = lst[v1]
        d = get_bit(v, 7)
        
        if inst == 'clr':
            if d == 0:
                inst = '  clrw'
            else:
                inst = '  clrf ' + get_freg_name(sfr_name, f) 
        else:
            inst += ' ' + get_freg_name(sfr_name, f) 
            if d == 0:
                inst += ',w'
            elif v1 != 0x01:
                inst += ',f'
  
    elif v0 == 1:
        #& 0xfc
        #10 : 0001 00bb bfff ffff  bit(3, b7-b9) f(7, b0-b6) BCF f,b   Clear bit b of f
        #14 : 0001 01bb bfff ffff  BSF f,b   Set bit b of f
        #18 : 0001 10bb bfff ffff  BTFSC f,b   Skip if bit b of f is clear
        #1c : 0001 11bb bfff ffff  BTFSS f,b   Skip if bit b of f is set        
        lst = ['bcf   ', 'bsf   ', 'btfsc ', 'btfss ']
        v1 &= 0xc
        b = get_bits(v, 7, 9)
        
        if v1 == 0:
            inst = '   bcf'
        elif v1 == 4:
            inst = '   bsf'
        elif v1 == 0x8:
            inst = ' btfsc'
        elif v1 == 0xc:
            inst = ' btfss'
        inst += ' ' + get_freg_name(sfr_name, f) + ',' + str(b)
    elif v0 == 2:
        #& 0xf8
        #20 : 0010 0kkk kkkk kkkk CALL k   Call subroutine
        #28 : 0010 1kkk kkkk kkkk GOTO k   Jump to address k
        if (v1 & 0x8) == 0:
            inst = '  call'
        elif (v1 & 0x8) == 8:
            inst = '  goto'
        k = get_bits(v, 0, 10)
        label = map_list.get(k, hex(k))
        inst += ' ' + label
    elif v0 == 3:
        #30 : 0011 00xx kkkk kkkk MOVLW k   W <- k
        #34 : 0011 01xx kkkk kkkk RETLW k   W <- k, then return from subroutine
        #38 : 0011 1000 kkkk kkkk IORLW k  Z W <- k | W, bitwise logical or
        #39 : 0011 1001 kkkk kkkk ANDLW k  Z W <- k & W, bitwise and
        #3a : 0011 1010 kkkk kkkk XORLW k  Z W <- k ^ W, bitwise exclusive or
        #3b : 0011 1011 kkkk kkkk (reserved)
        #3c : 0011 110x kkkk kkkk SUBLW k C Z W <- k-W (dest <- k+~W+1)
        #3e : 0011 111x kkkk kkkk ADDLW k C Z W <- k+W
        
        if v1 == 0:
            inst = ' movlw'
        elif v1 == 4:
            inst = ' retlw'
        elif v1 == 8:
            inst = ' iorlw'
        elif v1 == 9:
            inst = ' andlw'
        elif v1 == 0xa:
            inst = ' xorlw'
        elif v1 == 0xb:
            inst = 'reserved'
        elif v1 == 0xc:
            inst = ' sublw'
        elif v1 == 0xe:
            inst = ' addlw'
        k = lsb
        inst += ' ' + hex(k)
            
    return inst

#----------------------------------------------------------------------------
def pic_hex_scan(frame, fn, mcu, dev_name):
    sfr_addr = utils.get_sfr_addr(dev_name)
    if sfr_addr:
        sfr_name = {}
        for k in sfr_addr:
            v = sfr_addr[k]
            sfr_name[v] = k.upper()

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
                pass #print s, 'Extended address line'
            else:
                pass #print s,'type = 04'
        elif tt == '01':
            if line.find(':00000001FF') >= 0:
                pass #print s, '  End of file', line
                break
            else:
                pass #print s, 'type = 01'
        elif tt != '00':
            pass #print s, 'type = ' + tt
        else:
            pass #print s
                   
        record_bytes = int("0x" + ll, 16)
        record_addr = int("0x" + aaaa, 16)
        record_type = int("0x" + tt, 16)

        r = Obj()
        r.bytes = record_bytes
        r.addr = record_addr
        r.type = record_type
        r.line = s
        r.insts = []
        
        j = 9
        n = record_bytes / 2
        for i in range(n):
            lsb = line[j:j+2]
            msb = line[j+2:j+4]
            r.insts.append(msb + lsb)
            j += 4
        
        lst.append(r)
        prev_r = lst[index]
        index += 1
        
    fn = fn.replace('.hex', '.hex2asm')
    f = open(fn, 'w+')
    
    map_list = map_scan(fn)
    #print map_list
    for r in lst:
        addr = r.addr/2

        #print >>f, tohex(r.addr, 6), tohex(addr,6), tohex(r.bytes,2), tohex(r.type,2) + ':'
        #print >>f, r.line
        for inst in r.insts:
            label = map_list.get(addr, "")
            if label and f:
                print >>f, '\n' + label + ':'            
            s = pic14_inst(inst, map_list, sfr_name)
            print >>f, "    %06X  %s %s" % (addr, inst, s)
            addr += 1

        
    f.close()
        
    #print '\n' + fn
    text = read_file(fn)
    print text
    return text
    


#----------------------------------------------------------------------------
def test_pic_hex_scan(fn):
    cfn = fn.replace('.hex', '.c')
    text = utils.read_file(cfn)
    
    dev_name = utils.get_dev_name(cfn)
    if dev_name == None:
        print "Can't find matched device " + cfn
        return
    
    mcu = None
    if dev_name[0:2] != "18":
        mcu = 'pic14'
      
    if mcu:
        print mcu, dev_name, fn
        pic_hex_scan(None, fn, mcu, dev_name)
    
import re
#-------------------------------------------------------------------
def test_get_dev_name(fn):
    fn = "/home/athena/src/pic14/0001/t0001.c"
    
    text = read_file(fn)
    
    match = re.findall(r"#include <\w+.h>", text)
    #log(match)
    for t in match :
        t = re.sub("#include <", "", t)
        t = re.sub(">", "", t)

        if t.find("pic16") >= 0 or t.find("pic10") >= 0 or t.find("pic12") >= 0 :
            mcu = "pic14"
            dev = re.sub("pic", "", t)
            dev = re.sub(".h", "", dev)
            print mcu, dev
    return None    

#---- for testing -------------------------------------------------------------
if __name__ == '__main__':    
    #fn = "/home/athena/src/pic/test1/test.hex"
    #fn = "/home/athena/src/pic/0004/uart_tx.hex"
    fn = "/home/athena/src/pic14/0001/t0001.hex"
    #test_pic_hex_scan(fn)
    #print map_scan(fn)
    test_get_dev_name(fn)