import os
import datetime

BIT0 = 1
BIT1 = 2
BIT2 = 4
BIT3 = 8
BIT4 = 0x10
BIT5 = 0x20
BIT6 = 0x40
BIT7 = 0x80

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

def comp8(v):
    return 0xFF - v

def hex8(v):
    if v >= 0:
        return hex(v)
    else:
        return hex(comp8(-v) + 1)

def val8(v):
    if v & 0x80:
        # -comp8(v - 1) => -(0xff - (v - 1)) => -(0xff -v + 1) => -(0x100 - v) => v - 0x100
        return v - 0x100
    else:
        return v
    
def tobin(v):
    s = ""
    for i in range(8):
        if v & (1 << (7 - i)):
            s += '1'
        else:
            s += '0'
            
    return s
    
#----------------------------------------------------------------------------
def set_bit(v, i):
    v |= 1 << i
    return v 

#----------------------------------------------------------------------------
def clear_bit(v, i):
    v &= ~(1 << i)
    return v 

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


def tohex(value, n):
    if (value is None) :
        return "None"

    if (value < 0) :
        if (n == 2) :
            value = 0x100 + value
        elif (n == 4) :
            value = 0x10000 + value
        elif (n == 6) :
            value = 0x1000000 + value
        elif (value > -128) :
            value = 0x100 + value
        else :
            value = 0x100000000 + value

    if n == 2 :
        return "%02X" % value
    elif n == 4 :
        return '%04X' % value
    elif n == 6 :
        return '%06X' % value
    elif n == 8 :
        return "%08X" % value
    else :
        return "%X" % value 


def read_file(path):    
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

def get_cur_dir():
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    if cur_dir.find('library.zip') > 0:
        if cur_dir.find('library.zip' + os.sep) > 0:
            cur_dir = cur_dir.replace('library.zip' + os.sep, '')
        else:
            cur_dir = cur_dir.replace('library.zip', '') 
        if cur_dir.find('ide') < 0:
            if cur_dir.endswith(os.sep) == False:
                cur_dir += os.sep
            cur_dir += 'ide'    
    return cur_dir

def get_sfr_addr(dev_name):
    path = get_cur_dir()
    path += os.sep + 'defines' + os.sep + 'p' + dev_name + '.sfr'
    sfr_addr = {}
    if os.path.exists(path):
        print path
        text = read_file(path)
        for line in text.split('\n'):
            if line == '' :
                continue
            k, v = line.split(':')
            if k == 'W' or k == 'F':
                continue
            if k == 'C':
                break
            v = int(v, 16) & 0xff
            sfr_addr[k] = v
            
                    
    return sfr_addr

def get_mem_sfr_map(dev_name):
    path = os.path.dirname(os.path.realpath(__file__)) 
    path += os.sep + 'defines' + os.sep + 'p' + dev_name + '.sfr'
    sfr_map = {}
    if os.path.exists(path):
        print path
        text = read_file(path)
        for line in text.split('\n'):
            if line == '':
                continue
            k, v = line.split(':')
            sfr_map[int(v, 16) & 0xff] = k
        
    return sfr_map


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