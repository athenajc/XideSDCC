import os
import utils
import re

#----------------------------------------------------------------
#.line	14; test.c	PORTA = 0;
#.line	15; test.c	PORTB = 0;
#.line	18; test.c	TRISA |= 0x10;
#.line	19; test.c	TRISB &= 0xF0;
header = 'gplink'

class CodeLineMap():
    def __init__(self, line_i, s):
        self.line_index = line_i + 1
        s = re.sub("\s+", " ", s)        # replace space
        
        p0 = s.find('.line')
        p1 = s.find(';', p0)
        s0 = s[p0:p1].replace('.line', '').strip()
        if s0 == '':
            return
        self.c_line = int(s0)
        #print p0, p1, self.c_line
  
        n = len(s)
        
        p2 = s.find('\"', p1)
        p3 = s.find('\"', p2 + 1)
        self.c_file = s[p2+1:p3]
        self.c_code = s[p3 + 2:n].strip()
        #print self.c_line, self.c_file, self.c_code
        self.addr_lst = []
        
    def add_addr(self, addr):
        self.addr_lst.append(addr)
        
class CodeLineMapGpasm():
#                          00153 ;       .line   25; "/home/athena/src/pic/0001/t0001.c" CMCON = 0x07;   /** Disable comparators.  NEEDED
    def __init__(self, line_i, s):
        self.line_index = line_i + 1
        
        s = re.sub("\s+", " ", s)        # replace space
        s = s.replace(';', '')
        s = s.replace('  ', ' ')
        p1 = s.find('.line')
        n = len(s)
        s = s[p1:n]
        lst = s.split(' ')

        lst.pop(0)
        v = lst.pop(0)

        self.c_line = int(v)
        self.c_file = lst.pop(0).strip()
        
        s = ' '.join(lst)
        self.c_code = s
        #print s
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
            
def ishex(s):
    s = s.lower()
    for c in s:
        if not c in '0123456789abcdef':
            return False
    return True



#----------------------------------------------------------------
def lst_get_lines(text, fn_index):
    code_map_lst = []
    addr_map_lst = []
    i = 0
    obj = None
    addr_min = 0x7fffffff
    addr_max = 0
    for line in text.split('\n') : 
        s = line[0:7].strip()
        #print line
        
        if s != '' and ishex(s) :
            #print line
            s1 = re.sub("\s+", " ", line)        # replace space
            lst = s1.split(' ')
            #print lst
            addr = int("0x" + lst[0], 16)
            if addr < addr_min:
                addr_min = addr
            if addr > addr_max:
                addr_max = addr
                            
            if obj is not None:
                #print hex(addr), obj.c_line
                p0 = line.find(lst[2])
                as_text = line[p0:len(line)]
                #print as_text
                addr_map_lst.append([addr, obj.c_file, obj.c_line, as_text, obj.count])
                obj.count += 1
                obj.add_addr(addr)
                
        if line.find('.line') >= 0:
            global header
            if header == 'gpasm':
                obj = CodeLineMapGpasm(i, line)
            else:
                obj = CodeLineMap(i, line)
            obj.count = 0
            code_map_lst.append(obj)
            #print(line)
        i += 1
        
    return addr_map_lst
    
                   
#----------------------------------------------------------------
def lst_scan_file(fn, fn_index):
    path, ext = fn.split('.')
    lst_file = path + ".lst"
    
    if not os.path.exists(lst_file):
        return []
    #print lst_file
    text = utils.read_file(lst_file)
    global header
    header = text[0:12]
    print header
    if header.find('gpasm') >= 0:
        header = 'gpasm'
    elif header.find('gplink') >= 0:
        header = 'gplink'
        
    c_name = path + ".c"
    ##print c_name
    lst = lst_get_lines(text, fn_index)
    #print lst
    return lst
    
#----------------------------------------------------------------
def pic_lst_scan(source_list):
    fn_index = 0
    lst = [0] * 4096
    for fn in source_list:
        addr_map_lst = lst_scan_file(fn, fn_index)
        
        for a in addr_map_lst:
            #print hex(a[0]), a[1], a[2], a[3]
            while a[0] >= len(lst):
                lst.append(0)
            lst[a[0]] = [a[1], a[2], a[3], a[4]]
        
        fn_index += 1
    
    return lst

##----------------------------------------------------------------
#def temp_scan_lst(fn):
    #fn = fn.replace('.hex', '.lst')
    #print fn
    #text = read_file(fn)
    #for line in text.split('\n'):
        #if line.find('.line') >= 0:
            #lst = line.split('\t')
            #for t in lst:
                #if t.find(';') > 0 and t.find('.c') > 0:
                    #t0, t1 = t.split(';')
                    #print t0.strip()
                    #print t1.strip()
                #else:
                    #print t

#----------------------------------------------------------------
def test_pic_lst_scan(fn):
    print fn
    #temp_scan_lst(fn)
    lst = pic_lst_scan([fn])
    for t in lst:
        if t != 0:
            print t
    pass

#---- for testing -------------------------------------------------------------
if __name__ == '__main__':    
    #fn = "/home/athena/src/pic14/0002/interrupt.hex"
    #fn = "/home/athena/src/pic14/0004/uart_tx.hex"
    fn = "/home/athena/src/pic14/0001/t0001.hex"
    test_pic_lst_scan(fn)
    
    

