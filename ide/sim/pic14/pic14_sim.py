import os
import sys
import thread
import threading
import time
import Queue
import wx
import importlib
import inspect

from utils import *
import utils
import pic_lst_scan
from pic_hex_scan import pic_hex_scan
from pic14_inst import *

pic14_devices = ['10f320', '10f322', '12f1501', '12f1822', '12f1840', 
                 '12f609', '12f615', '12f617', '12f629',  '12f635', 
                 '12f675', '12f683', '12f752', '12lf1552', '14regs', 
                 '16c432', '16c433', '16c554', '16c557', '16c558', 
                 '16c62', '16c620', '16c620a', '16c621', '16c621a', 
                 '16c622', '16c622a', '16c63a', '16c65b', '16c71', 
                 '16c710', '16c711', '16c715', '16c717', '16c72', 
                 '16c73b', '16c745', '16c74b', '16c765', '16c770', 
                 '16c771', '16c773', '16c774', '16c781', '16c782', 
                 '16c925', '16c926', '16f1454', '16f1455', '16f1458', 
                 '16f1459', '16f1503', '16f1507', '16f1508', '16f1509', 
                 '16f1512', '16f1513', '16f1516', '16f1517', '16f1518', 
                 '16f1519', '16f1526', '16f1527', '16f1704', '16f1708', 
                 '16f1782', '16f1783', '16f1784', '16f1786', '16f1787', 
                 '16f1788', '16f1789', '16f1823', '16f1824', '16f1825', 
                 '16f1826', '16f1827', '16f1828', '16f1829', '16f1847', 
                 '16f1933', '16f1934', '16f1936', '16f1937', '16f1938', 
                 '16f1939', '16f1946', '16f1947', '16f610', '16f616', 
                 '16f627', '16f627a', '16f628', '16f628a', '16f630', 
                 '16f631', '16f636', '16f639', '16f648a', '16f676', 
                 '16f677', '16f684', '16f685', '16f687', '16f688', 
                 '16f689', '16f690', '16f707', '16f716', '16f72', 
                 '16f720', '16f721', '16f722', '16f722a', '16f723', 
                 '16f723a', '16f724', '16f726', '16f727', '16f73', 
                 '16f737', '16f74', '16f747', '16f753', '16f76', 
                 '16f767', '16f77', '16f777', '16f785', '16f818', 
                 '16f819', '16f84', '16f84a', '16f87', '16f870', 
                 '16f871', '16f872', '16f873', '16f873a', '16f874', 
                 '16f874a', '16f876', '16f876a', '16f877', '16f877a', 
                 '16f88', '16f882', '16f883', '16f884', '16f886', 
                 '16f887', '16f913', '16f914', '16f916', '16f917', 
                 '16f946', '16fam', '16hv616', '16hv753', '16lf1704', 
                 '16lf1708', '16lf1902', '16lf1903', '16lf1904', '16lf1906', '16lf1907']


#----------------------------------------------------------------------------
class SimPic():    
    def __init__(self, frame, hex_file, source_list, mcu_name, mcu_device):
        self.frame = frame
        self.mcu_name = mcu_name
        self.dev_name = mcu_device
        self.source_list = source_list
        self.hex_file = hex_file
        self.inst_addr = 0
        self.bank_addr = 0
        
        #self.get_mcu_name()
        #print self.mcu_name, self.dev_name
        self.sfr_addr = get_sfr_addr(self.dev_name)
        
        #print self.sfr_addr
        self.mem_sfr_map = {}
        self.reg_table = {}
        for k, v in self.sfr_addr.items():
            self.mem_sfr_map[v] = k
            self.reg_table[k] = 0
            
        #print self.mem_sfr_map
        
        self.addr_map_lst = pic_lst_scan.pic_lst_scan(source_list)
        #print '\n\nself.addr_map_lst', self.addr_map_lst
        #for t in self.addr_map_lst:
        #    if t != 0:
        #        print(t)
                
        self.c_line = 0
        self.asm_code = ""
        
        self.stack = []
        self.stack_depth = 0
        self.err = 0
        self.sbuf_list = []
        self.init_memory()
        self.init_registers()
        self.c_file = source_list[0]
        self.c_line = 0
        self.load_code()
        self.mem_access_list = []
        self.status_bits_name = ['C', 'DC', 'Z', 'PD', 'TO', 'RP0', 'RP1', 'IRP']
        self.step_mode = None

    #-------------------------------------------------------------------
    def log(self, *args):
        #if self.c_line == 0:
        #    return
        #import inspect
        #s1 = inspect.stack()[1][3] + " "
        
        msg = " "
        for t in args:
            msg = msg + str(t) + " "
        s = get_hh_mm_ss() + msg + "\n"
        if self.frame == None:
            print get_hh_mm_ss() + msg
        else:
            self.frame.log(s)

    #-------------------------------------------------------------------
    def log1(self, *args):
        pass #print('log1', args)
        
    #-------------------------------------------------------------------
    def get_mcu_name(self):
        for fn in self.source_list:
            text = utils.read_file(fn)
            inc_lines = ""
            for line in text.split('\n'):
                if line.find("#include") >= 0:
                    inc_lines += line + '\n'
                    
            text = inc_lines
            for d in pic14_devices:
                if text.find(d) >= 0:
                    self.dev_name = d
                    break
                    
            if text.find('pic16f') >= 0 or text.find('PIC16F') >= 0:
                self.mcu_name = 'pic14'
                return 'pic14'
            elif text.find('pic18f') >= 0 or text.find('PIC18F') >= 0:
                self.mcu_name = 'pic16'
                return 'pic16'
            else:
                self.mcu_name = None
                
        return None    
    
    #-------------------------------------------------------------------
    def disassembly(self):
        return pic_hex_scan(self.frame, self.hex_file, self.mcu_name)
        
    #-------------------------------------------------------------------
    def init_registers(self):
        self.status_reg = 0
        self.pc = 0
        self.wreg = 0
        self.bsr = 0
        self.wreg_addr = self.sfr_addr.get('wreg', 0x0FE8)
        self.bsr_addr = self.sfr_addr.get('bsr', 0xFE0) 
        
    #-------------------------------------------------------------------
    def init_memory(self):
        self.mem = [0] * 0x1000
        self.ext_mem = [0] * 64 * 1024
        self.code_space = [0] * 64 * 1024
        self.freg = self.mem #[0] * 128 * 4
        
    #-------------------------------------------------------------------
    def select_access_bank(self):
        self.log("     set bank")
        
    #-------------------------------------------------------------------
    def get_mem(self, addr):
        v = self.mem[addr]
        key = self.mem_sfr_map.get(addr, "")
        self.log("     get mem "+hex(addr) + " " + key +" = "+hex(v))
        return v    
    
    #-------------------------------------------------------------------
    def set_mem(self, addr, v):
        key = self.mem_sfr_map.get(addr, "")
        self.log("     set mem " + hex(addr) + " " + key + " = " + hex(v))
        if (v > 0xff) :
            self.log(v, "> 0xff")
            v = bits_and(v, 0xff)
        
        if not addr in self.mem_access_list:
            self.mem_access_list.append(addr)
            
        self.mem[addr] = v
        
        if key != "":
            #self.log('     set_reg ', key, v)
            self.set_reg(key, v)
        return v

    #-------------------------------------------------------------------
    def mem_get_bit(self, addr, bit):       
        v = self.get_mem(addr)

        if v & (1 << bit):
            self.log("     get bit " + str(bit) + " of " + tohex(addr, 4), 1)
            return 1
        else:
            self.log("     get bit " + str(bit) + " of " + tohex(addr, 4), 0)
            return 0
                
    #-------------------------------------------------------------------
    def mem_set_bit(self, addr, bit, b):
        v = self.get_mem(addr)
        
        if b == 1:
            v = set_bit(v, bit)
        else:
            v = clear_bit(v, bit)
            
        self.set_mem(addr, v)
        
    #-------------------------------------------------------------------
    def set_sfr(self, k, v):
        #self.log('set sfr ', k, v)
        addr = self.sfr_addr[k]
        self.set_mem(addr, v)
        
        # update reg_table
        self.reg_table[k] = v
        
    #-------------------------------------------------------------------
    def get_sfr(self, k):
        addr = self.sfr_addr[k]
        v = self.get_mem(addr)
        
        # update reg_table
        self.reg_table[k] = v
        return v
    
    #-------------------------------------------------------------------
    def update_sfr(self):     
        pass
        #n = 0x1000
        #for k, v in self.sfr_addr.items():
            #if v < n:
                #self.set_sfr(k, self.mem[v])
            
    #-------------------------------------------------------------------
    def set_reg(self, k, v):
        self.reg_table[k] = v
        
    #-------------------------------------------------------------------
    def get_reg(self, k):
        v = self.reg_table.get(k, 0)
        #self.log('get_reg', k, hex(self.sfr_addr.get(k, 0)), v)
        return v
    
    #-------------------------------------------------------------------
    def set_freg(self, addr, v):
        if not addr in [2, 3, 4, 0xA, 0xB]:
            addr += self.bank_addr
        key = self.mem_sfr_map.get(addr, "")
        self.log("     set freg " + key + " " + hex(addr) + " = "+hex(v))
        #self.freg[addr] = v
        self.set_mem(addr, v)
        if addr == 3:
            self.status_reg = v
                    
        #self.mem[addr] = v
        #key = self.mem_sfr_map.get(addr, None)
        #if key:
        #    self.set_reg(key, v)
        
    #-------------------------------------------------------------------
    def get_freg(self, addr):
        if not addr in [2, 3, 4, 0xA, 0xB]:
            addr += self.bank_addr        

        v = self.mem[addr]
        self.log("     get freg " + hex(addr) + " = "+hex(v))
        return v
    
    #-------------------------------------------------------------------
    def set_wreg(self, v):
        self.log("     set w = "+hex(v))
        self.wreg = v
        self.set_reg('W', v)
        
    #-------------------------------------------------------------------
    def get_wreg(self):
        #v = self.get_sfr('W')
        v = self.wreg
        self.log("     get w = "+hex(v))
        return v
        
    #-------------------------------------------------------------------
    def set_bsr(self, v):
        self.log("     set bsr = "+hex(v))
        self.set_sfr('BSR', v)
        
    #-------------------------------------------------------------------
    def get_bsr(self):
        v = self.get_sfr('BSR')
        self.log("     get bsr = "+hex(v))
        return v
    
    #-------------------------------------------------------------------
    def set_prod(self, v):
        self.log("     set prod = "+hex(v))
        self.set_sfr('PRODH', (v >> 8) & 0xff)
        self.set_sfr('PRODL', v & 0xff)
    
    #-------------------------------------------------------------------
    def set_status_reg(self, bit, v, name = ''):
        #bit 7:
        #IRP: Register Bank Select bit (used for indirect addressing)
        #0 = Bank 0, 1 (00h - FFh)
        #1 = Bank 2, 3 (100h - 1FFh)
        #The IRP bit is not used by the PIC16F8X. IRP should be maintained clear. 
         
        #bit 6-5:
        #RP1:RP0: Register Bank Select bits (used for direct addressing)
        #00 = Bank 0 (00h - 7Fh)
        #01 = Bank 1 (80h - FFh)
        #10 = Bank 2 (100h - 17Fh)
        #11 = Bank 3 (180h - 1FFh)
        #Each bank is 128 bytes. Only bit RP0 is used by the PIC16F8X. RP1 should be maintained clear.
         
        #bit 4:
        #TO: Time-out bit
        #1 = After power-up, CLRWDT instruction, or SLEEP instruction
        #0 = A WDT time-out occurred
         
        #bit 3:
        #PD: Power-down bit
        #1 = After power-up or by the CLRWDT instruction
        #0 = By execution of the SLEEP instruction
         
        #bit 2:
        #Z: Zero bit
        #1 = The result of an arithmetic or logic operation is zero
        #0 = The result of an arithmetic or logic operation is not zero
        #bit (for ADDWF and ADDLW instructions) (For borrow the polarity is reversed)
         
        #bit 1:
        #DC: Digit carry/borrow
        #1 = A carry-out from the 4th low order bit of the result occurred
        #0 = No carry-out from the 4th low order bit of the result
        #bit (for ADDWF and ADDLW instructions)
         
        #bit 0:
        #C: Carry/borrow
        #1 = A carry-out from the most significant bit of the result occurred
        #0 = No carry-out from the most significant bit of the result occurred
        #Note: For borrow the second operand the polarity is reversed. A subtraction is executed by adding the two's complement of. For rotate (RRF, RLF) instructions, this bit is loaded with either the high or low order bit of the source register.        
        if name:
            self.log("     set status " + name + " bit " + str(bit) + " = "+hex(v))
        else:
            self.log("     set status bit " + str(bit) + " = "+hex(v))

        if v:
            self.status_reg = set_bit(self.status_reg, bit)
        else:
            self.status_reg = clear_bit(self.status_reg, bit)
        #self.set_freg(3, self.status_reg)
        self.mem[0x03] = self.status_reg
        self.mem[0x83] = self.status_reg
        self.mem[0x103] = self.status_reg
        self.mem[0x183] = self.status_reg
        
        if bit == 5 or bit == 6:
            bank = (self.status_reg >> 5) & 0x3
            self.bank_addr = bank * 0x80
            if bit == 6:
                self.log("     select bank " + str(bank) + ", " + hex(self.bank_addr))
                
    #-------------------------------------------------------------------
    def clear_status_reg_flags(self):
        self.status_reg = self.status_reg & 0xf0
        
        #self.set_freg(3, self.status_reg)
        self.mem[0x03] = self.status_reg
        self.mem[0x83] = self.status_reg
        self.mem[0x103] = self.status_reg
        self.mem[0x183] = self.status_reg        
        
    #-------------------------------------------------------------------
    def get_status_reg(self, bit):
        v = self.status_reg
        b = get_bit(v, bit)
            
        self.log("     get status bit" + str(bit) + " = "+hex(b))
        
        return b
                
    #-------------------------------------------------------------------
    def set_z(self, v):
        self.set_status_reg(2, v, 'z')

    #-------------------------------------------------------------------
    def set_dc(self, v):
        self.set_status_reg(1, v, 'dc')
        
    #-------------------------------------------------------------------
    def set_c(self, v):
        self.set_status_reg(0, v, 'c')
        
    #-------------------------------------------------------------------
    def get_c(self):
        return self.get_status_reg(0)
        
    #-------------------------------------------------------------------
    def push(self, v):
        self.log("     push "+hex(v))
        self.stack.insert(0, v)
        self.set_reg('SP', len(self.stack))
        # print("     #stack = "+tostring(#self.stack))
        
    #-------------------------------------------------------------------
    def pop(self):
        if len(self.stack) == 0:
            self.log("     pop empty")
            self.stopped = True
            return 0
        v = self.stack.pop(0)
        self.set_reg('SP', len(self.stack))
        self.log("     pop "+hex(v))
        return v

    #-------------------------------------------------------------------
    def set_pc(self, v):
        #PCL      0FF9
        #PCLATH   0FFA
        #PCLATU   0FFB
        self.log("     set pc = "+tohex(v, 4), hex(self.get_reg('PC')))
        self.pc = v
        self.set_reg('PC', v)
                
    #-------------------------------------------------------------------
    def jump(self, addr):
        self.set_pc(addr)
        
    #-------------------------------------------------------------------
    def jump_rel(self, v):
        offset = val8(v)
        
        self.log("     jump_rel  "+str(offset) )
        self.set_pc(self.pc + offset)
        
    #-------------------------------------------------------------------
    def call(self, addr):
        self.push(self.pc)
        self.set_pc(addr)
        self.stack_depth += 1
        
    #-------------------------------------------------------------------
    def ret(self):
        addr = self.pop()
        self.set_pc(addr)
        self.stack_depth -= 1
        self.log("****** ret set pc = "+tohex(addr, 4), hex(self.get_reg('PC')))
        
    #-------------------------------------------------------------------
    def retfie(self):
        # return from interrupt
        addr = self.pop()
        self.set_pc(addr)
        self.stack_depth -= 1
        # set INTCON Bit7
        # GIE Global Interrupt Enable bit
        #     1 = Enables all un-masked interrupts
        #     0 = Disables all interrupts
        a = self.sfr_addr['INTCON']
        v = self.mem[a]
        set_bit(v, 7)
        self.mem[a] = v
        
    #-------------------------------------------------------------------
    def skip_next_inst(self):
        self.log("     skip next inst")
        self.set_pc(self.pc + 1)
        
    #-------------------------------------------------------------------
    def code_space_fill(self, addr, sz, ddstr):
        i1 = 0
        i2 = 2
        #--print(tohex(addr, 4), tohex(sz, 2), ddstr)
        for i in range(sz):
            dd = ddstr[i1:i2]
            #self.log(hex(addr+i), dd)
            self.code_space[addr + i] = int("0x" + dd, 16)
            #self.log(tohex(addr + i, 4), dd, tohex(self.mem[addr + i], 2))
            i1 += 2
            i2 += 2

    #-------------------------------------------------------------------
    def load_code(self):    
        text = utils.read_file(self.hex_file)
        
        # for each line, :llaaaatt
        for line in text.split('\n'):
            if line == '':
                continue
            if line == ':00000001FF':
                break
            
            llen = int('0x' + line[1:3], 16)
            addr = int('0x' + line[3:7], 16)
            ttype = int('0x' + line[7:9], 16)
            
            if (ttype == 0) :
                self.code_space_fill(addr, llen, line[9: 10 + llen*2])
                
    #-------------------------------------------------------------------
    def load_inst(self):
        # get current program counter 
        addr = self.pc
        self.set_reg('PC', self.pc)
        self.inst_addr = self.pc
        if addr < len(self.addr_map_lst):
            t = self.addr_map_lst[addr]
            #print addr, len(self.addr_map_lst), t
            if t != 0:
                self.c_file = t[0]
                self.c_line = t[1]
                self.asm_code = t[2]
        else:
            self.c_file = ""
            self.c_line = 0
            self.asm_code = ""
        
        lsb = self.code_space[addr*2]
        msb = self.code_space[addr*2 + 1] & 0x3f
        opcode = (msb << 8) + lsb
        #self.log('**************** ', hex(msb), hex(lsb))
        
        # self.set_pc(self.pc + blen)
        self.pc = self.pc + 1
        
        #self.log('**************** pc ', hex(self.pc))
        f = inst_handler[msb]
        s = get_pic14_inst_str(opcode, msb, lsb)
        self.log("---------", tohex(addr, 4) + "  " + tohex(msb, 2) + tohex(lsb, 2) + '  <' + s +'>')
        #self.log("asm_code    ", self.c_line, self.asm_code)
        #self.log("     ", s)
        f(self, msb, lsb)
        
        #ch = self.get_uart_put_ch()
        #if ch != 0:
            #self.sbuf_list.append(ch)
                
    #-------------------------------------------------------------------
    def start(self):
        self.stopped = False
        self.running = True
        #set_sim(self)

        self.mode = 'run'
        self.pc = 0x0
        self.cmd_queue = Queue.Queue()
        self.c_line = 0
        
        #while self.c_line == 0:
        #    self.load_inst()
            
    #-------------------------------------------------------------------
    def step(self):
        if self.stopped:
            return False
        
        self.step_mode = None

        self.load_inst()
        self.update_sfr()
        
        if self.err:
            self.log("#simulation Error")
            return False
        if self.pc == 0 :
            self.log("#end of simulation")
            return False
        
        return True

    #-------------------------------------------------------------------
    def step_tick(self):
        if self.stopped:
            return False
        if self.step_mode == None:
            return False
        
        n = self.c_line
        f = self.c_file
        i = 1
        
        while self.c_line == n and self.c_file == f:
            i += 1
            self.load_inst()
            if i > 10:
                break
            
        self.update_sfr()
        
        if self.step_mode == 'c_line':
            if self.c_line != self.start_line or self.c_file != self.start_file:
                self.step_mode = None
        elif self.step_mode == 'over':
            if self.stack_depth == self.start_stack_depth:
                if self.c_line != self.start_line or self.c_file != self.start_file:
                    self.step_mode = None
        elif self.step_mode == 'out':
            if self.stack_depth < self.start_stack_depth:
                self.step_mode = None
        
        if self.err:
            self.log("#simulation Error")
            return False
        if self.pc == 0 :
            self.log("#end of simulation")
            return False
        
        return True    

    #-------------------------------------------------------------------
    def step_c_line(self):
        if self.stopped:
            return False
        self.step_mode = 'c_line'
        self.start_line = self.c_line
        self.start_file = self.c_file
        
        return True

    #-------------------------------------------------------------------
    def step_over(self):
        #self.log("step_over")

        if self.stopped:
            return False
        self.step_mode = 'over'
        self.start_stack_depth = self.stack_depth
        self.start_line = self.c_line
        self.start_file = self.c_file

        return True
        
    #-------------------------------------------------------------------
    def step_out(self):
        #self.log("step_out")
        if self.stopped:
            return False
        self.step_mode = 'out'
        self.start_stack_depth = self.stack_depth

        return True
    
    #-------------------------------------------------------------------
    def stop(self):
        self.stopped = True
                
        
        

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
            
def test_sim():
    #fn = "/home/athena/src/pic14/0004/uart_tx.hex"
    #fn = "/home/athena/src/pic14/0001/test.hex"
    fn = "/home/athena/src/pic14/0001/t0001.c"
    hex_fn = fn.replace('.c', '.hex')
    #frame, hex_file, source_list, mcu_name, mcu_device
    sim = SimPic(None, hex_fn, [fn], 'pic14', '16f628a')
    sim.start()
    
    for i in range(10):
        sim.step()    

#---- for testing -------------------------------------------------------------
if __name__ == '__main__':    
    test_sim()
    #convert_header_files()
    #set_pic14_inst_table()
    
    
    
