import os
import sys
from utils import *
from table import *
import rst


#-------------------------------------------------------------------
# combine multiline records
def pre_process_ihx_text(text):
    lst = []
    index = 0
    prev_r = None
    for line in text.split('\n'):
        if line == "":
            continue
        
        n = len(line)
        ll   = line[1:3]
        aaaa  = line[3:7]
        tt = line[7:9]
        #dd = line[9:n-2]

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
        for i in range(record_bytes):
            r.dd.append(line[j:j+2])
            j += 2
        
        if append_to_prev == False:
            lst.append(r)
            prev_r = lst[index]
            index += 1
        
    #for r in lst:
        #print tohex(r.addr,4), tohex(r.bytes,2), tohex(r.type,2), ':',
        #for d in r.dd:
            #print d,
        #print ""        
    return lst

    
#-------------------------------------------------------------------
def do_scan(f, text, symbol_table, map_list):
    lst = pre_process_ihx_text(text)
    
    code_map = {}
    for item in lst:
        if item.type != 0:
            continue
                
        addr = item.addr

        # get all instruction data 
        i = 0

        while (i < item.bytes) : 
            label = map_list.get_symbol(addr)
            if label and f:
                print >>f, '\n' + label + ':'
                
            inst = item.dd[i]
            inst_code = int('0x' + inst, 16)
            sym = symbol_table[inst_code]
            blen = sym[1]
            s = sym[5].lower()
            op1 = op2 = op3 = "  "
            v1 = v2 = v3 = 0
            if blen > 1:
                op1 = item.dd[i+1]
                v1 = int('0x' + op1, 16)
                if blen > 2:
                    op2 = item.dd[i+2]
                    v2 = int('0x' + op2, 16)
                    if blen > 3:
                        op3 = item.dd[i+3]
                        v3 = int('0x' + op3, 16)
                
                            
            if s.find('code_addr') > 0:
                v = int('0x' + op1 + op2, 16)
                label = map_list.get_symbol(v)
                s = s.replace('code_addr', label)
            elif inst == 'jb   ' or inst == 'jnb  ' :
                label = map_list.get_symbol(v1)
            elif s.find('addr') > 0 or s.find('#') > 0:
                if blen == 2:
                    if s.find('iram_addr') > 0:
                        t1 = addr_sfr.get(v1, op1)
                        s = s.replace('iram_addr', t1)
                    s = s.replace('#data', '#' + op1)
                    
                    if s.find('bit_addr') > 0:
                        s1 = bit_addr_map.get(v1, op1)
                        s = s.replace('bit_addr', s1)
                    if s.find('reladdr') > 0:
                        v = val8(v1)
                        rel_addr = addr + 2 + v
                        label = map_list.get_symbol(rel_addr)
                        if label:
                            s = s.replace('reladdr', label)
                        else:
                            s = s.replace('reladdr', str(v))
                        
                elif blen == 3:
                    if s.find(',#data,reladdr') > 0:
                        s = s.replace('#data', '#' + op1)
                        
                    if s.find(',reladdr') > 0:
                        v = val8(v2)
                        rel_addr = addr + 2 + v
                        label = map_list.get_symbol(rel_addr)
                        if label:
                            s = s.replace('reladdr', label)
                        else:
                            s = s.replace('reladdr', str(v))
                    if s.find('iram_addr,#data') > 0:
                        t1 = addr_sfr.get(v1, op1)
                        s = s.replace('iram_addr', t1)
                        s = s.replace('#data', '#' + op2)
                    elif s.find('iram_addr,') > 0:
                        t1 = addr_sfr.get(v1, op1)
                        s = s.replace('iram_addr,', t1 + ',')
                    if s.find(',iram_addr') > 0:
                        t1 = addr_sfr.get(v2, op2)
                        s = s.replace(',iram_addr', ',' + t1)
                    if s.find('bit_addr,') > 0:
                        s1 = bit_addr_map.get(v1, op1)
                        s = s.replace('bit_addr,', s1 + ',')
                    
            tlst = s.split(' ')
            s1 = tlst[0]
            n = len(s1)
            if n == 2:
                s = s.replace(s1, s1 + "  ")
            elif n == 3:
                s = s.replace(s1, s1 + " ")
            if f:
                print >>f,  "    %06X  %s %s %s %s   %s" % (addr, inst, op1, op2, op3, s)
            
            lst = [inst, op1, op2, op3, s]
            code_map[addr] = " ".join(lst)
            i += blen
            addr += blen

    return code_map


#----------------------------------------------------------------------------
def hex_scan_to_map(file_path, text, mcu_name):
    text = read_whole_file(file_path)
    #print(file_path)
    #frame.log(text + "\n")
    map_list = rst.map_scan(file_path)
    
    fn = file_path.replace('.ihx', '.tmp')
    
    code_map = do_scan(None, text, symbol_table, map_list)
    return code_map
    
#----------------------------------------------------------------------------
def hex_scan(file_path, mcu_name):
    text = read_whole_file(file_path)
    #print(file_path)
    #frame.log(text + "\n")
    map_list = rst.map_scan(file_path)
    
    fn = file_path.replace('.ihx', '.tmp')
    f = open(fn, 'w')
    do_scan(f, text, symbol_table, map_list)
    f.close()
    
    text = read_whole_file(fn)
    
    return text
    
#----------------------------------------------------------------------------
def convert2():
    for key, value in sorted(sfr_map.iteritems(), key=lambda (k,v): (v,k)):
        print "0x%02x:\'%s\'," % (value, key)
        
#----------------------------------------------------------------------------
def convert():        
    for s in txt.split('\n'):
        if s.find('__sbit') > 0:
            s = s.strip()
            s = s.replace('__sbit __at (', '')
            s = s.replace(';', '')
            s = s.replace(')', '')
            s = s.strip()
            s = s.replace('  ', '')
            s0, s1 = s.split(' ')
            print s0 + ': \'' + s1 + '\','

#---- for testing -------------------------------------------------------------
if __name__ == '__main__':    
    #fn = "/home/athena/src/pic/test1/test.hex"
    #fn = "/home/athena/src/pic/0004/uart_tx.hex"
    fn = "/home/athena/src/8051/test_uart/test_uart.ihx"
    #fn = "/home/athena/src/8051/t0/t0.ihx"
    symbol_table.sort()
    s = hex_scan(None, fn, '8051')
    print s
    #convert()