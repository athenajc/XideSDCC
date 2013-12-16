import datetime

from table import *

BIT0 = 1
BIT1 = 2
BIT2 = 4
BIT3 = 8
BIT4 = 0x10
BIT5 = 0x20
BIT6 = 0x40
BIT7 = 0x80
bits = [1,2,4,8,0x10,0x20,0x40,0x80]

comp_lst = [0xff, 0xfe, 0xfd, 0xfc, 0xfb, 0xfa, 0xf9, 0xf8, 0xf7, 0xf6, 0xf5, 0xf4, 0xf3, 0xf2, 0xf1, 0xf0, 
            0xef, 0xee, 0xed, 0xec, 0xeb, 0xea, 0xe9, 0xe8, 0xe7, 0xe6, 0xe5, 0xe4, 0xe3, 0xe2, 0xe1, 0xe0, 
            0xdf, 0xde, 0xdd, 0xdc, 0xdb, 0xda, 0xd9, 0xd8, 0xd7, 0xd6, 0xd5, 0xd4, 0xd3, 0xd2, 0xd1, 0xd0, 
            0xcf, 0xce, 0xcd, 0xcc, 0xcb, 0xca, 0xc9, 0xc8, 0xc7, 0xc6, 0xc5, 0xc4, 0xc3, 0xc2, 0xc1, 0xc0, 
            0xbf, 0xbe, 0xbd, 0xbc, 0xbb, 0xba, 0xb9, 0xb8, 0xb7, 0xb6, 0xb5, 0xb4, 0xb3, 0xb2, 0xb1, 0xb0, 
            0xaf, 0xae, 0xad, 0xac, 0xab, 0xaa, 0xa9, 0xa8, 0xa7, 0xa6, 0xa5, 0xa4, 0xa3, 0xa2, 0xa1, 0xa0, 
            0x9f, 0x9e, 0x9d, 0x9c, 0x9b, 0x9a, 0x99, 0x98, 0x97, 0x96, 0x95, 0x94, 0x93, 0x92, 0x91, 0x90, 
            0x8f, 0x8e, 0x8d, 0x8c, 0x8b, 0x8a, 0x89, 0x88, 0x87, 0x86, 0x85, 0x84, 0x83, 0x82, 0x81, 0x80, 
            0x7f, 0x7e, 0x7d, 0x7c, 0x7b, 0x7a, 0x79, 0x78, 0x77, 0x76, 0x75, 0x74, 0x73, 0x72, 0x71, 0x70, 
            0x6f, 0x6e, 0x6d, 0x6c, 0x6b, 0x6a, 0x69, 0x68, 0x67, 0x66, 0x65, 0x64, 0x63, 0x62, 0x61, 0x60, 
            0x5f, 0x5e, 0x5d, 0x5c, 0x5b, 0x5a, 0x59, 0x58, 0x57, 0x56, 0x55, 0x54, 0x53, 0x52, 0x51, 0x50, 
            0x4f, 0x4e, 0x4d, 0x4c, 0x4b, 0x4a, 0x49, 0x48, 0x47, 0x46, 0x45, 0x44, 0x43, 0x42, 0x41, 0x40, 
            0x3f, 0x3e, 0x3d, 0x3c, 0x3b, 0x3a, 0x39, 0x38, 0x37, 0x36, 0x35, 0x34, 0x33, 0x32, 0x31, 0x30, 
            0x2f, 0x2e, 0x2d, 0x2c, 0x2b, 0x2a, 0x29, 0x28, 0x27, 0x26, 0x25, 0x24, 0x23, 0x22, 0x21, 0x20, 
            0x1f, 0x1e, 0x1d, 0x1c, 0x1b, 0x1a, 0x19, 0x18, 0x17, 0x16, 0x15, 0x14, 0x13, 0x12, 0x11, 0x10, 
            0x0f, 0x0e, 0x0d, 0x0c, 0x0b, 0x0a, 0x09, 0x08, 0x07, 0x06, 0x05, 0x04, 0x03, 0x02, 0x01, 0x00]

global sim

def set_sim(s):
    global sim
    sim = s

def bits8(v):
    return v & 0xff
    
def bit(b):
    return 1 << b  # 1-based indexing

# Typical call:  if hasbit(x, bit(3)) : ...
def hasbit(x, bit):
    if x & (1 << bit):
        return 1
    else:
        return 0

def testbit(x, bit):
    return hasbit(x, bit)

def getbit(x, bit):
    # print("getbit", x, p, bit(p))
    return x & (1 << bit)

def setbit(x, bit):
    return x | (1 << bit)

def clearbit(v1, bit):
    v2 = ~(1 << bit)
    return v1 & v2

def bits_test(v1, v2):
    if v1 & v2:
        return 1
    else:
        return 0

def bits_and(v1, v2):
    return v1 & v2

def bits_or(v1, v2):
    return v1 | v2

def bits_xor(v1, v2):
    return v1 ^ v2

def bits_not(v):
    return ~v & 0xffff

def bits_lshift(v, n):  # <<
    return v << n

def bits_rshift(v, n):  # >>
    return v >> n

def int_to_byte(v):   
    if (v < 0) :
        v = 0x100 + v;        
    return v

def tonumber(s, d):
    if s is None or s == "" :
        return 0    
    return int("0x" + s, d)

def tostring(v):
    return str(v)

def int_to_word(v):    
    if (v < 0) :
        v = 0x10000 + v;        
    return v

def byte_to_int(v):
    if (bits_test(v, 0x80)) :
        #print(v, bits_and(v, 0x7f), bits_and(v, 0x7f) - 128)
        v = (v & 0x7f) - 128
        #print(v)    
    return v

def word_to_int(v):
    if (v > 0x7fff) :
        v = (v & 0x7fff) - 0x10000;
    return v

def tohex(value, n):
    if (value is None) :
        return "None"

    if (value < 0) :
        if (n == 2) :
            value = 0x100 + value
        elif (n == 4) :
            value = 0x10000 + value
        elif (value > -128) :
            value = 0x100 + value
        else :
            value = 0x10000000 + value

    if n == 2 :
        return "%02X" % value
    elif n == 4 :
        return '%04X' % value
    elif n == 8 :
        return "%08X" % value
    else :
        return "%X" % value 


def read_whole_file(path):    
    with open(path, 'r') as content_file:
        content = content_file.read()
    return content

def print_table(lst):
    for t in lst :
        print t

def get_lines(text):
    for line in text.split('\n') : 
        print(line)

def get_tokens(line):
    tokens = []

    for token in line.split(' '):
        tokens.append(token)

    return tokens


def print_symbol_table():
    for sym in symbol_table:
        if (sym == nil) :
            print(tohex(i), "nil")
        else:
            t = get_tokens(sym[5])
            print(tohex(i), t[1], t[2], t[3], t[4], t[5])
            #--print(tohex(i), sym[1], tohex(sym[2]), sym[5])
            v1, v2 = string.find(sym[5], tohex(i))
            if (v1 == nil) :
                print(tohex(i), sym[1], tohex(sym[2]), sym[5])
            #end
            #--print(v1, v2)
            if (tohex(i) != sym[5][v1-1:v2]) :
                print(tohex(i), sym[5][v1-1:v2], tohex(i) == sym[5][v1-1:v2])
            #end
        #end
    #end
    print("total", len(symbol_table))
#end



class Inst():
    def __init__(self, inst, op1, op2, op3):
        self.inst = inst
        self.op1 = op1
        self.op2 = op2
        self.op3 = op3
       

def get_hh_mm_ss():
    now = datetime.datetime.now()
    return str(datetime.time(now.hour, now.minute, now.second)) + "  "

def print_records(records):
    count = len(records)
    
    for r in records:
        print(r.ll, tohex(r.aaaa, 4), len(r.insts))
        for dd in r.insts :
            print("    ", tohex(dd.inst,2), dd.op1, dd.op2, dd.op3)            

def array_list(table, n):
    lst = []
    for i in range(n):
        lst.append(0)
    for t in table:
        lst[t[0]] = t[1]
    return lst

def comp8(v):
    return 0xFF - v

def hex8(v):
    if v >= 0:
        return hex(v)
    else:
        return hex(0xFF - (-v) + 1)

def val8(v):
    if v & 0x80:
        v = 0xff - (v - 1)
        return -v
    else:
        return v
    
def getbit(x, bit):
    # print("getbit", x, p, bit(p))
    return x & (1 << bit)

def setbit(x, bit):
    return x | (1 << bit)

def clearbit(v1, bit):
    v2 = ~(1 << bit)
    return v1 & v2


#---- for testing -------------------------------------------------------------
if __name__ == '__main__':    
    #temp()
    lst = []
    
    for v in range(256):
        #print hex(comp8(v)) + ",",
        print comp8(v), v,  comp8(v) == 0xFF - v