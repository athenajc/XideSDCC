import os
import utils

#----------------------------------------------------------------
#.line	14; test.c	PORTA = 0;
#.line	15; test.c	PORTB = 0;
#.line	18; test.c	TRISA |= 0x10;
#.line	19; test.c	TRISB &= 0xF0;

class CodeLineMap():
    def __init__(self, line_i, s):
        self.line_index = line_i + 1
        n = len(s)
        lst = s.split('\t')

        lst1 = lst[2].split(';')
        self.c_line = int(lst1[0].strip())
        self.c_file = lst1[1].strip()
        self.c_code = lst[3].strip()

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
def lst_get_lines(text, fn_index):
    code_map_lst = []
    addr_map_lst = []
    i = 0
    obj = None
    addr_min = 0x7fffffff
    addr_max = 0
    for line in text.split('\n') : 
        s = line[0:7].strip()
        if s != '' and s.isdigit() :
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
                
        if line.find('.line') >= 0:
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
    pic_lst_scan([fn])
        
#---- for testing -------------------------------------------------------------
if __name__ == '__main__':    
    fn = "/home/athena/src/pic/test1/test.hex"
    #fn = "/home/athena/src/pic/0004/uart_tx.hex"
    #fn = "/home/athena/src/pic/0001/test.hex"
    test_pic_lst_scan(fn)
    
    

