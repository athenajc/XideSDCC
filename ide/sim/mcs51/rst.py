import os
import sys
from utils import *


#----------------------------------------------------------------
class CodeMap():
    def __init__(self, line_i, s):
        self.line_index = line_i + 1
        n = len(s)
        s = s[41:n]
        lst = s.split(':')
        self.c_file = lst[0].replace('\t', '')
        self.c_line = int(lst[1])
        self.c_code = lst[2]
        self.addr_lst = []
        
    def add_addr(self, addr):
        self.addr_lst.append(addr)
        
#----------------------------------------------------------------        
def print_out(addr_map_lst, code_map_lst):
    for m in addr_map_lst:
        print("[" + hex(m[0]) + ", " + str(m[1]) + "], ")
    print ""
    
    for obj in code_map_lst:
        print "\nC line   : " + str(obj.c_line)
        print "C code   :" + obj.c_code
        sys.stdout.write("Addr map : ")
        
        for a in obj.addr_lst:
            sys.stdout.write(hex(a) + ", ")
            
#----------------------------------------------------------------
def rst_get_lines(text, c_name, fn_index):
    code_map_lst = []
    addr_map_lst = []
    i = 0
    obj = None
    addr_min = 0x7fffffff
    addr_max = 0
    for line in text.split('\n') : 
        s = line[6:12].strip()
        if s != "" :
            s = s.replace(' ', '')
            addr = int("0x" + s, 16)
            if addr < addr_min:
                addr_min = addr
            if addr > addr_max:
                addr_max = addr
            
            if obj is not None:
                #print hex(addr), obj.c_line
                as_text = line[40:len(line)]
                addr_map_lst.append([addr, obj.c_file, obj.c_line, as_text, obj.count])
                obj.count += 1
                obj.add_addr(addr)
                
        if line.find(c_name) > 0 or (line.find(';') > 0 and line.find('.c') > 0):
            obj = CodeMap(i, line)
            obj.count = 0
            code_map_lst.append(obj)
            #print(line)
        i += 1
        
    #print addr_min, addr_max
    #lst = [0] * (addr_max + 1)
        
    #for a in addr_map_lst:
        #print a[0], a[1]
    #    lst[a[0]] = [a[1], a[2], a[3], a[4]]
    #print_out(addr_map_lst, code_map_lst)
        
    return addr_map_lst

class MapList():
    def __init__(self, file_path):
        text = read_whole_file(file_path)
        lst = []
        self.addr_lst = []
        self.symbol_lst = []
        for line in text.split('\n'):
            if line.find('C:') == 0:
                line = line.replace('C: ', '')
                line = line.strip()
                t = []            
                for s in line.split(' '):
                    if s != '':
                        t.append(s)
                addr = int('0x' + t[0], 16)
                symbol = t[1]
                c0 = symbol[0:1]
                if c0 == '_':
                    self.addr_lst.append(addr)
                    self.symbol_lst.append(symbol)
                    lst.append([addr, symbol])
        print self.addr_lst
        self.lst = lst
        
    def get_symbol(self, addr):
        print hex(addr)
        if addr in self.addr_lst:
            i = self.addr_lst.index(addr)
            print self.symbol_lst[i]
            return self.symbol_lst[i]

        return None
        
def map_scan(fn):
    path, ext = fn.split('.')
    map_file = path + ".map"
    if not os.path.exists(map_file):
        return []
            
    map_lst = MapList(map_file)

    return map_lst

def rst_scan_file(fn, fn_index):
    #print fn
    path, ext = fn.split('.')
    rst_file = path + ".rst"
    
    if not os.path.exists(rst_file):
        return []
    
    text = read_whole_file(rst_file)
    
    c_name = path + ".c"
    #print c_name
    lst = rst_get_lines(text, c_name, fn_index)
    #print lst
    return lst
    
def rst_scan(source_list):
    fn_index = 0
    lst = [0] * 4096
    for fn in source_list:
        addr_map_lst = rst_scan_file(fn, fn_index)
        
        for a in addr_map_lst:
            #print a[0], a[1]
            while a[0] >= len(lst):
                lst.append(0)
            lst[a[0]] = [a[1], a[2], a[3], a[4]]
        
        fn_index += 1
    
    return lst
        
    
#---- for testing -------------------------------------------------------------
if __name__ == '__main__':    
    fn = "/home/athena/src/8051/BlinkLEDs/main.rst"
    rst_scan(fn)

