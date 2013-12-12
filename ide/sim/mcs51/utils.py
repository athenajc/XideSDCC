import datetime

from table import *

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
    v1 = 0
    for i in range(8):
        b = (v >> i) & 1
        if b == 0:
            v1 |= 1 << i
    #print v, v1, hex(v), hex(v1), bin(v), bin(v1)
    return v1

def hex8(v):
    if v >= 0:
        return hex(v)
    else:
        return hex(comp8(-v) + 1)

def val8(v):
    if v & 0x80:
        v = comp8(v - 1)
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