import os
import sys
import thread
import threading
import time
import Queue
import wx
import importlib


from utils import *
import utils
import pic_lst_scan
from pic_hex_scan import pic_hex_scan
from pic16_inst import *

pic16_devices = ['18f1220', '18f1230', '18f1320', '18f1330', '18f13k22', 
                '18f13k50', '18f14k22', '18f14k50', '18f2220', '18f2221', 
                '18f2320', '18f2321', '18f2331', '18f23k20', '18f23k22',
                '18f2410', '18f242', '18f2420', '18f2423', '18f2431',
                '18f2439', '18f2450', '18f2455', '18f2458', '18f248', 
                '18f2480', '18f24j10', '18f24j11', '18f24j50', '18f24k20', 
                '18f24k22', '18f24k50', '18f2510', '18f2515', '18f252', 
                '18f2520', '18f2523', '18f2525', '18f2539', '18f2550', 
                '18f2553', '18f258', '18f2580', '18f2585', '18f25j10', 
                '18f25j11', '18f25j50', '18f25k20', '18f25k22', '18f25k50', 
                '18f25k80', '18f2610', '18f2620', '18f2680', '18f2682', 
                '18f2685', '18f26j11', '18f26j13', '18f26j50', '18f26j53', 
                '18f26k20', '18f26k22', '18f26k80', '18f27j13', '18f27j53', 
                '18f4220', '18f4221', '18f4320', '18f4321', '18f4331', 
                '18f43k20', '18f43k22', '18f4410', '18f442', '18f4420', 
                '18f4423', '18f4431', '18f4439', '18f4450', '18f4455', 
                '18f4458', '18f448', '18f4480', '18f44j10', '18f44j11', 
                '18f44j50', '18f44k20', '18f44k22', '18f4510', '18f4515', 
                '18f452', '18f4520', '18f4523', '18f4525', '18f4539', 
                '18f4550', '18f4553', '18f458', '18f4580', '18f4585', 
                '18f45j10', '18f45j11', '18f45j50', '18f45k20', '18f45k22', 
                '18f45k50', '18f45k80', '18f4610', '18f4620', '18f4680', 
                '18f4682', '18f4685', '18f46j11', '18f46j13', '18f46j50', 
                '18f46j53', '18f46k20', '18f46k22', '18f46k80', '18f47j13', 
                '18f47j53', '18f6310', '18f6390', '18f6393', '18f63j11', 
                '18f63j90', '18f6410', '18f6490', '18f6493', '18f64j11', 
                '18f64j90', '18f6520', '18f6525', '18f6527', '18f6585', 
                '18f65j10', '18f65j11', '18f65j15', '18f65j50', '18f65j90', 
                '18f65j94', '18f65k22', '18f65k80', '18f65k90', '18f6620', 
                '18f6621', '18f6622', '18f6627', '18f6628', '18f6680', 
                '18f66j10', '18f66j11', '18f66j15', '18f66j16', '18f66j50', 
                '18f66j55', '18f66j60', '18f66j65', '18f66j90', '18f66j93', 
                '18f66j94', '18f66j99', '18f66k22', '18f66k80', '18f66k90', 
                '18f6720', '18f6722', '18f6723', '18f67j10', '18f67j11', 
                '18f67j50', '18f67j60', '18f67j90', '18f67j93', '18f67j94', 
                '18f67k22', '18f67k90', '18f8310', '18f8390', '18f8393', 
                '18f83j11', '18f83j90', '18f8410', '18f8490', '18f8493', 
                '18f84j11', '18f84j90', '18f8520', '18f8525', '18f8527', 
                '18f8585', '18f85j10', '18f85j11', '18f85j15', '18f85j50', 
                '18f85j90', '18f85j94', '18f85k22', '18f85k90', '18f8620', 
                '18f8621', '18f8622', '18f8627', '18f8628', '18f8680', 
                '18f86j10', '18f86j11', '18f86j15', '18f86j16', '18f86j50', 
                '18f86j55', '18f86j60', '18f86j65', '18f86j72', '18f86j90', 
                '18f86j93', '18f86j94', '18f86j99', '18f86k22', '18f86k90', 
                '18f8720', '18f8722', '18f8723', '18f87j10', '18f87j11', 
                '18f87j50', '18f87j60', '18f87j72', '18f87j90', '18f87j93', 
                '18f87j94', '18f87k22', '18f87k90', '18f95j94', '18f96j60', 
                '18f96j65', '18f96j94', '18f96j99', '18f97j60', '18f97j94', 
                '18fam']


    
#----------------------------------------------------------------------------
class SimPic():    
    def __init__(self, frame, hex_file, source_list, mcu_name, mcu_device):
        self.frame = frame
        self.mcu_name = mcu_name
        self.dev_name = mcu_device
        self.source_list = source_list
        self.hex_file = hex_file
        
        self.bank_addr = 0

        #self.get_mcu_name()
        #print self.mcu_name, self.dev_name
        self.sfr_addr = get_sfr_addr(self.dev_name)
        self.mem_sfr_map = {}
        self.reg_table = {}
        for k, v in self.sfr_addr.items():
            self.mem_sfr_map[v] = k
            self.reg_table[k] = 0
            
        self.addr_map_lst = pic_lst_scan.pic_lst_scan(source_list)
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
        self.status_bits_name = ['C', 'DC', 'Z', 'OV', 'N']

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
            for d in pic16_devices:
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
        self.wreg_addr = self.sfr_addr.get('WREG', 0x0FE8)
        self.bsr_addr = self.sfr_addr.get('BSR', 0xFE0) 
        
    #-------------------------------------------------------------------
    def init_memory(self):
        self.mem = [0] * 0x1000
        self.ext_mem = [0] * 64 * 1024
        self.code_space = [0] * 64 * 1024
        
    #-------------------------------------------------------------------
    def select_access_bank(self):
        self.log("     set bank")
    
    #-------------------------------------------------------------------
    def get_tblptr(self):    
        addr_h = self.get_sfr('TBLPTRH')
        addr_l = self.get_sfr('TBLPTRL')
        addr = (addr_h << 8) + addr_l
        return addr 
    
    #-------------------------------------------------------------------
    def set_tblptr(self, addr):    
        addr_h = (addr >> 8) & 0xff
        addr_l = addr & 0xff
        self.set_sfr('TBLPTRH', addr_h)
        self.set_sfr('TBLPTRL', addr_l)
        
    #-------------------------------------------------------------------
    def read_tbl(self, mode):
        #0000 0000 0000 1000   0x0008,TBLRD*    Table read
        #0000 0000 0000 1001   0x0009,TBLRD*+   Table read with postincrement
        #0000 0000 0000 1010   0x000A,TBLRD*-   Table read with postdecrement
        #0000 0000 0000 1011   0x000B,TBLRD+*   Table read with pre-increment            
        
        addr = self.get_tblptr()
        
        if mode == 3:
            addr += 1
        
        v = self.mem[addr]
        self.set_sfr('TABLAT', v)
        
        if mode == 1:
            addr += 1
        elif mode == 2:
            addr -= 1
            
        self.set_tblptr(addr)
        
    #-------------------------------------------------------------------
    def write_tbl(self, mode):
        #0000 0000 0000 1000   0x0008,TBLWR*    Table write
        #0000 0000 0000 1101   0x0009,TBLWR*+   Table write with postincrement
        #0000 0000 0000 1110   0x000A,TBLWR*-   Table write with postdecrement
        #0000 0000 0000 1111   0x000B,TBLWR+*   Table write with pre-increment
        addr = self.get_tblptr()
        
        if mode == 3:
            addr += 1
        
        v = self.mem[addr]
        self.set_sfr('TABLAT', v)
        
        if mode == 1:
            addr += 1
        elif mode == 2:
            addr -= 1
            
        self.set_tblptr(addr)
        
    
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
    def set_freg(self, banksel, addr, v):
        # banksel == 0, Select bank0
        # banksel == 1, Select bank according BSR
        if banksel == 1:
            addr += self.bank_addr
        #self.log("     set freg "+ hex(addr) + " = "+hex(v))
        #self.freg[addr] = v
        
        self.set_mem(addr, v)
        if addr == 3:
            self.status_reg = v
                    
        #self.mem[addr] = v
        #key = self.mem_sfr_map.get(addr, None)
        #if key:
        #    self.set_reg(key, v)
        
    #-------------------------------------------------------------------
    def get_freg(self, banksel, addr):
        # banksel == 0, Select bank0
        # banksel == 1, Select bank according BSR
        if banksel == 1:
            addr += self.bank_addr
            
        v = self.mem[addr]
        #self.log("     get freg " + hex(addr) + " = "+hex(v))
        return v
    
    #-------------------------------------------------------------------
    def set_reg(self, k, v):
        self.reg_table[k] = v
        
    #-------------------------------------------------------------------
    def get_reg(self, k):
        return self.reg_table.get(k, 0)
    
    #-------------------------------------------------------------------
    def set_wreg(self, v):
        #self.log("     set w = "+hex(v))
        self.wreg = v
        self.set_sfr('WREG', v)
        
    #-------------------------------------------------------------------
    def get_wreg(self):
        v = self.get_sfr('WREG')
        self.wreg = v
        #self.log("     get w = "+hex(v))
        return v
    
    #-------------------------------------------------------------------
    def store_wfreg(self, d, a, lsb, v):
        if v == 0:
            self.set_z(1)
        elif v & 0x80:
            self.set_n(1)
                
        if d == 0:
            self.set_wreg(v)
        else:
            self.set_freg(a, lsb, v)

    #-------------------------------------------------------------------
    def set_bsr(self, v):
        self.log("     set bsr = "+hex(v))
        self.set_sfr('BSR', v)
        self.bsr = v
        self.bank_addr = v * 256
        
    #-------------------------------------------------------------------
    def get_bsr(self):
        v = self.get_sfr('BSR')
        self.log("     get bsr = "+hex(v))
        return v
    
    #-------------------------------------------------------------------
    def set_fsr(self, i, msb, lsb):
        name = 'FSR' + str(i)
        name_h = name + 'H'
        name_l = name + 'L'
        self.set_sfr(name_h, msb)
        self.set_sfr(name_l, lsb)
        
    #-------------------------------------------------------------------
    def set_prod(self, v):
        self.log("     set prod = "+hex(v))
        self.set_sfr('PRODH', (v >> 8) & 0xff)
        self.set_sfr('PRODL', v & 0xff)
    
    #-------------------------------------------------------------------
    def get_status_reg(self, bit):
        # N OV Z DC C
        v = self.status_reg
        b = get_bit(v, bit)
        #self.log("     get status " + self.status_bits_name[bit] + " = "+hex(b))
        
        return b    
       
    #-------------------------------------------------------------------
    def set_status_reg(self, bit, v):
        # N OV Z DC C
        self.log("     set " + self.status_bits_name[bit] + " = "+hex(v))
        if v:
            self.status_reg = set_bit(self.status_reg, bit)
        else:
            self.status_reg = clear_bit(self.status_reg, bit)
        self.set_reg('STATUS', self.status_reg)
    
    #-------------------------------------------------------------------
    def clear_status_flags(self):
        # clear bit 0 - 5  N OV Z DC C
        self.status_reg = self.status_reg & 0xe0
        self.set_reg('STATUS', self.status_reg)
    
    #-------------------------------------------------------------------
    def set_n(self, v):
        self.set_status_reg(4, v)
        
    #-------------------------------------------------------------------
    def set_ov(self, v):
        self.set_status_reg(3, v)
        
    #-------------------------------------------------------------------
    def set_z(self, v):
        self.set_status_reg(2, v)

    #-------------------------------------------------------------------
    def set_dc(self, v):
        self.set_status_reg(1, v)
        
    #-------------------------------------------------------------------
    def set_c(self, v):
        self.set_status_reg(0, v)
        
    #-------------------------------------------------------------------
    def get_n(self):
        return self.get_status_reg(4)
    
    #-------------------------------------------------------------------
    def get_ov(self):
        return self.get_status_reg(3)
    
    #-------------------------------------------------------------------
    def get_z(self):
        return self.get_status_reg(2)
    
    #-------------------------------------------------------------------
    def get_dc(self):
        return self.get_status_reg(1)
    
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
    def ljump_rel(self, v):
        # bit 0-10, 0x7ff
        if v & 0x400:
            offset = (v & 0x3ff) - 0x400
        else:
            offset = v
            
        self.log("     jump_rel  "+str(offset) )
        self.set_pc(self.pc + offset)
        
    #-------------------------------------------------------------------
    def call(self, addr, fast):
        self.push(self.pc)
        self.set_pc(addr)
        self.stack_depth += 1
        
    #-------------------------------------------------------------------
    def ret(self, fast):
        addr = self.pop()
        self.set_pc(addr)
        self.stack_depth -= 1
        self.log("****** ret set pc = "+tohex(addr, 4), hex(self.get_reg('PC')))
        
    #-------------------------------------------------------------------
    def retfie(self, fast):
        # Return from interrupt.
        # Stack is popped and Top-of-Stack(TOS) is loaded into the PC.
        # Interrupts are enabled by setting either the high or low priority gloable interrupt enbale bit.
        # if s == 1, the contents of the shadow register WS, STATUSS and BSRS are 
        #            loaded into their corresponding registers - W, STATUS and BSR.
        # if s == 0, no update of these registers occurs(default)
        
        addr = self.pop()
        self.set_pc(addr)
        self.stack_depth -= 1
        # set GIE/GIEH or PEIE/GIEL = 1
        # GIE Global Interrupt Enable bit
        #     1 = Enables all un-masked interrupts
        #     0 = Disables all interrupts
        #a = self.sfr_addr['GIEH']
        #v = self.mem[a]
        #set_bit(v, 7)
        #self.mem[a] = v
        
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
        addr = self.pc * 2
        if addr < len(self.addr_map_lst):
            t = self.addr_map_lst[addr]
            if t != 0:
                self.c_file = t[0]
                self.c_line = t[1]
                self.asm_code = t[2]
        else:
            self.c_file = ""
            self.c_line = 0
            self.asm_code = ""
        
        lsb = self.code_space[addr]
        msb = self.code_space[addr + 1]
        opcode = (msb << 8) + lsb
        inst_len = 1
        #self.log('**************** ', hex(msb), hex(lsb))
        #inst_call,    #EC
        #inst_call,    #ED
        #inst_lfsr,    #EE
        #inst_goto,    #EF        
        if (msb & 0xc0) == 0xc0:
            inst_len = 2
        elif msb >= 0xEC and msb <= 0xEF:
            inst_len = 2

        self.pc = self.pc + inst_len
        self.set_reg('PC', self.pc)

        f = inst_handler[msb]
        s = get_pic16_inst_str(opcode, msb, lsb)
        
        self.log('\n------------------', tohex(self.pc, 4), tohex(opcode, 4), "   " + s + '   ------------------')
        #self.log("    ", tohex(addr/2, 2), hex(msb), hex(lsb), '<' + str(f)[10:20]+'>')
        #self.log("------- asm_code    ", self.c_line, self.asm_code)
        #self.log("------- get inst str", s)
        if inst_len == 2:
            lsb1 = self.code_space[addr + 2]
            msb1 = self.code_space[addr + 3]
            if msb1 & 0xf0 != 0xf0:
                self.log('Error following inst', hex(msb), hex(lsb), hex(msb1), hex(lsb1))
            else:
                f(self, msb, lsb, msb1, lsb1)
        else:
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
        
        #lsb = self.code_space[self.pc*2]
        #msb = self.code_space[self.pc*2 + 1]
        #opcode = (msb << 8) + lsb
        #self.log(hex(msb), hex(lsb))        
        #s = get_pic16_inst_str(opcode, msb, lsb)
        
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
    def step_c_line(self):
        if self.stopped:
            return False
        
        n = self.c_line
        f = self.c_file
        i = 1
        line = self.c_line
        #if line > 0:
            #line += 1
        #self.log('\n-------------- line = ' + str(line) + ',   ' + str(self.c_file) + ' -----------')        
        while self.c_line == n and self.c_file == f:
            i += 1
            
            #self.log(tohex(self.pc, 4), self.asm_code)
            
            self.load_inst()
            if i > 100:
                return 'not finished'
            
            if self.err:
                self.log('#simulation Error')
                return False
            if self.pc == 0 or self.stopped:
                self.log('#end of simulation')
                return False
            
        
        return True
    
    #-------------------------------------------------------------------
    def step_over(self):
        #self.log("step_over")

        if self.stopped:
            return False
        
        s0 = self.stack_depth
        if not self.step_c_line():
            return False
        s1 = self.stack_depth
        
        # check stack depth if same means at same function        
        if s1 <= s0:
            return True
        else:
            i = 0
            while self.stack_depth > s0:
                i += 1
                if i > 100:
                    return False
                if not self.step_c_line():
                    return False
        return True
        
    #-------------------------------------------------------------------
    def step_out(self):
        #self.log("step_out")
        if self.stopped:
            return False
        
        s0 = self.stack_depth
        
        # check stack depth if same means at same function
        while self.stack_depth >= s0:
            if not self.step_c_line():
                return False
            
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
        if f.find('p18f') >= 0:
            f1 = f.replace('.inc', '.sfr')
            convert_inc(src_path + f, dst_path + f1)
            
def test_sim():
    fn = "/home/athena/src/pic/test1/test.c"
    #fn = "/home/athena/src/pic/0004/uart_tx.hex"
    #fn = "/home/athena/src/pic/0001/test.hex"
    hex_fn = fn.replace('.c', '.hex')
    sim = SimPic(None, hex_fn, [fn])
    sim.start()
    
    for i in range(10):
        sim.step()    

#---- for testing -------------------------------------------------------------
if __name__ == '__main__':    
    test_sim()
    #convert_header_files()
    #set_pic16_inst_table()
    
    
    
