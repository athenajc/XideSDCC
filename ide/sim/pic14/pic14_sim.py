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
from pic14_devices import *


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
        for k in self.sfr_addr:
            v = self.sfr_addr[k]
            setattr(self, k, v)
            #print k, v
        
        #print self.sfr_addr
        self.sfr_name = {}
        for v in range(512):
            self.sfr_name[v] = ""
            
        for k, v in self.sfr_addr.items():
            self.sfr_name[v] = k
        
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
        self.sp = 0
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
        self.debug = False
        
        self.int_enabled = False
        self.int_p_enabled = False
        self.tmr0_enabled = False
        self.tmr1_enabled = False
        self.tmr2_enabled = False
        self.tmr0_rate = 0
        self.wdt_rate = 0
        self.ticks = 0
        
    #-------------------------------------------------------------------
    def log(self, *args):
        #if self.c_line == 0:
        #    return
        #import inspect
        #s1 = inspect.stack()[1][3] + " "
        if not self.debug:
            return
        
        msg = " "
        for t in args:
            msg = msg + str(t) + " "
        s = get_hh_mm_ss() + msg + "\n"
        if self.frame == None:
            pass #print msg
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
        return pic_hex_scan(self.frame, self.hex_file, self.mcu_name, self.addr_map_lst)
    
    #-------------------------------------------------------------------
    def init_registers(self):
        self.status_reg = 0
        self.pc = 0
        self.wreg = 0
        
    #-------------------------------------------------------------------
    def init_memory(self):
        self.mem = [0] * 0x1000
        self.ext_mem = [0] * 64 * 1024
        self.code_space = [0] * 64 * 1024
        self.freg = self.mem #[0] * 128 * 4
        
    #-------------------------------------------------------------------
    def select_access_bank(self):
        if self.debug:
            self.log("     set bank")
        
    #-------------------------------------------------------------------
    def get_mem(self, addr):
        v = self.mem[addr]
        if self.debug:
            key = self.sfr_name[addr]
            self.log("     get mem "+hex(addr) + " " + key +" = "+hex(v))
        return v    
    #-------------------------------------------------------------------
    #def update_pc_from_PCL(self):
        #pch = self.get_sfr('PCLATH')
        #pcl = self.get_sfr('PCL')
        #v = (pch << 8) | pcl
        #self.set_pc(v)
        
    #-------------------------------------------------------------------
    def set_mem(self, addr, v):
        
        if self.debug:
            key = self.sfr_name[addr]
            self.log("     set mem " + hex(addr) + " " + key + " = " + hex(v))
        if (v > 0xff) :
            self.log(v, "> 0xff")
            #v = bits_and(v, 0xff)
            v = v & 0xff
        
        if not addr in self.mem_access_list:
            self.mem_access_list.append(addr)
            
        self.mem[addr] = v
        
        #if key != "":
            #self.log('     set_reg ', key, v)
        #    self.set_reg(key, v)

        if addr == self.PCL:
            self.update_pc_from_PCL()
            
        return v
    #-------------------------------------------------------------------
    def update_pc_from_PCL(self):
        pch = self.freg[self.PCLATH]
        pcl = self.freg[self.PCL]
        v = (pch << 8) | pcl
        self.set_pc(v)
        
    ##-------------------------------------------------------------------
    #def set_mem(self, addr, v):
        
        #if self.debug:
            #key = self.mem_sfr_map.get(addr, "")
            #self.log("     set mem " + hex(addr) + " " + key + " = " + hex(v))
            
        #if (v > 0xff) :
            #self.log(v, "> 0xff")
            #v = v & 0xff
        
        #if not addr in self.mem_access_list:
            #self.mem_access_list.append(addr)
            
        #self.mem[addr] = v
        
        #if addr == self.PCL:
            ##self.log('     set_reg ', key, v)
            #self.update_pc_from_PCL()
                
        #return v

    #-------------------------------------------------------------------
    def mem_get_bit(self, addr, bit):       
        v = self.get_mem(addr)

        if v & (1 << bit):
            if self.debug: 
                self.log("     get bit %d of %02x is 1" % (bit, addr))
            return 1
        else:
            if self.debug: 
                self.log("     get bit %d of %02x is 0" % (bit, addr))
            return 0
                
    #-------------------------------------------------------------------
    def mem_set_bit(self, addr, bit, b):
        v = self.get_mem(addr)
        
        if b == 1:
            v |= 1 << bit
        else:
            v &= ~(1 << bit)
            
        self.set_mem(addr, v)
               
    #-------------------------------------------------------------------
    def set_reg(self, k, v):
        addr = self.sfr_addr.get(k, -1)
        if addr == -1:
            self.log("Error set_reg", k)
            return
        self.mem[addr] = v
        
    #-------------------------------------------------------------------
    def get_reg(self, k):
        addr = self.sfr_addr.get(k, -1)
        if addr == -1:
            if k == 'PC':
                return self.pc
            elif k == 'SP':
                return self.sp
            else:
                return 0xFF
        v = self.mem[addr]

        return v
    
    #-------------------------------------------------------------------
    def set_freg(self, addr, v):
        if not addr in [2, 3, 4, 0xA, 0xB]:
            addr += self.bank_addr
        
        if self.debug:
            key = self.sfr_name[addr]
            self.log("     set freg %s %02x = %02x" % (key, addr, v))
            
        self.freg[addr] = v
        if addr == 3:
            self.status_reg = v
        elif addr == 1 or addr == 0x101:
            pass
        elif addr == 0x81 or addr == 0x181:
            self.set_option_reg(v)
        elif addr == self.PCL:
            #self.log('     set_reg ', key, v)
            self.update_pc_from_PCL()
                    
    #-------------------------------------------------------------------
    def set_freg_bit(self, addr, bit, b):
        if not addr in [2, 3, 4, 0xA, 0xB]:
            addr += self.bank_addr
        
        if self.debug:
            key = self.sfr_name[addr]
            self.log("     set freg %s %02x bit %d = %d" % (key, addr, bit, b))
            
        v = self.freg[addr]
        if b == 0:
            v &= ~(1 << bit)
        else:
            v |= 1 << bit
        self.freg[addr] = v
        
        if not addr in self.mem_access_list:
            self.mem_access_list.append(addr)
        
        if addr == 3:
            self.status_reg = v
        elif addr == 0xB:
            self.set_intcon(v, bit, b)
        elif addr == 0x81 or addr == 0x181:
            self.set_option_reg(v, bit, b)
            
    #-------------------------------------------------------------------
    def get_freg(self, addr):
        if not addr in [2, 3, 4, 0xA, 0xB]:
            addr += self.bank_addr

        v = self.freg[addr]
        if self.debug:
            key = self.sfr_name[addr]
            self.log("     get freg %s %02x is %02x" % (key, addr, v))
            
        return v
    
    #-------------------------------------------------------------------
    def set_wreg(self, v):
        if self.debug:
            self.log("     set w = %02x" % (v))
        self.wreg = v
        
    #-------------------------------------------------------------------
    def get_wreg(self):
        v = self.wreg
        if self.debug:
            self.log("     get w = %02x" % (v))
        return v
    
    #-------------------------------------------------------------------
    def set_intcon(self, v, bit, b):
        # 7: GIE, 6:PEIE, 5:T0IE, 4:INTE, 3:RBIE, 2:T0IF, 1:INTF, 0:RBIF
        if bit == 7:
            if b == 1:
                self.int_enabled = True
            else:
                self.int_enabled = False
        elif bit == 6:
            if b == 1:
                self.int_p_enabled = True
            else:
                self.int_p_enabled = False
        
    #-------------------------------------------------------------------
    def set_option_reg(self, v, bit=-1, b=None):
        #bit 7:
        #RBPU: PORTB Pull-up Enable bit
        #0 = PORTB pull-ups are disabled
        #1 = PORTB pull-ups are enabled (by individual port latch values). 
         
        #bit 6
        #INTEDG: Interrupt Edge Select bit
        #1 = Interrupt on rising edge of RB0/INT pin
        #0 = Interrupt on falling edge of RB0/INT pin
         
        #bit 5
        #T0CS: TMR0 Clock Source Select bit
        #1 = Transition on RA4/T0CKI pin
        #0 = Internal instruction cycle clock (CLKOUT)
         
        #bit 4:
        #T0SE: TMR0 Source Edge Select bit
        #1 = Increment on high-to-low transition on RA4/T0CKI pin
        #0 = Increment on low-to-high transition on RA4/T0CKI pin
         
        #bit 3:
        #PSA: Prescaler Assignment bit
        #1 = Prescaler assigned to the WDT
        #0 = Prescaler assigned to TMR0
        #bit 2,1,0:
        #PS2:PS0: Prescaler Rate Select bits 
         
        #Bit Value  TMR0 Rate   WDT Rate
        #  000        1 : 2         1 : 1
        #  001        1 : 4         1 : 2
        #  010        1 : 8         1 : 4
        #  011        1 : 16        1 : 8
        #  100        1 : 32        1 : 16
        #  101        1 : 64        1 : 32
        #  110        1 : 128       1 : 64
        #  111        1 : 256       1 : 128
        
        if bit == 5:
            #T0CS
            if b == 0:
                self.tmr0_enabled = True
            else:
                self.tmr0_enabled = False
        elif bit < 3:
            psa = v & BIT3
            i = v & 7
            if psa == 0: # TMR0
                self.tmr0_rate = 1 << (i + 1) 
                self.wdt_rate = 0
            else:
                # WDT rate
                self.wdt_rate = 1 << i
                self.tmr0_rate = 0

    #-------------------------------------------------------------------
    def set_prod(self, v):
        if self.debug:
            self.log("     set prod = %02x" % (v))
        self.freg[self.PRODH] = (v >> 8) & 0xff
        self.freg[self.PRODL] = v & 0xff

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
        if self.debug:
            if name:
                self.log("     set status %s bit %d = %d" % (name, bit, v))
            else:
                self.log("     set status bit %d = %d" % (bit, v))

        if v:
            self.status_reg |= 1 << bit
        else:
            self.status_reg &= ~(1 << bit)
        #self.set_freg(3, self.status_reg)
        self.freg[0x03] = self.status_reg
        
        if bit == 5 or bit == 6:
            bank = (self.status_reg >> 5) & 0x3
            self.bank_addr = bank * 0x80
            if bit == 6:
                if self.debug:
                    self.log("     select bank %d, %02x", (bank, self.bank_addr))
                
    #-------------------------------------------------------------------
    def clear_status_reg_flags(self):
        v = self.status_reg & 0xf0
        self.freg[0x03] = self.status_reg = v
        
    #-------------------------------------------------------------------
    def get_status_reg(self, bit):
        v = self.status_reg
        b = get_bit(v, bit)
        if self.debug:
            self.log("     get status bit %d is %x" % (bit, b))
        
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
        return self.status_reg & 1

    #-------------------------------------------------------------------
    def get_z(self):
        return (self.status_reg >> 2) & 1
    
    #-------------------------------------------------------------------
    def get_dc(self):
        return (self.status_reg >> 1) & 1
    
    #-------------------------------------------------------------------
    def set_input(self, k, v):
        # INTCON, PIE1, PIE2
        intcon = self.freg[0xB]
        
        if k == 'int0':
            if intcon & BIT4:
                self.reg[0xB] |= BIT2
                
        elif k == 'int1':
            pass
        elif k == 'uart':
            # set RI = 1
            pass
    
    #-------------------------------------------------------------------
    def push(self, v):
        if self.debug:
            self.log("     push %02x" % (v))
        self.sp = len(self.stack)
        self.stack.insert(0, v)
        # print("     #stack = "+tostring(#self.stack))
        
    #-------------------------------------------------------------------
    def pop(self):
        if len(self.stack) == 0:
            self.log("     pop empty")
            self.stopped = True
            return 0
        v = self.stack.pop(0)
        self.sp = len(self.stack)
        if self.debug:
            self.log("     pop %02x" % (v))
        return v

    #-------------------------------------------------------------------
    def set_pc(self, v):
        #PCL      0FF9
        #PCLATH   0FFA
        #PCLATU   0FFB
        if self.debug:
            self.log("     set pc = %04x" % (v))
        self.pc = v
        
        self.freg[self.PCL] = v & 0xff
        
    #-------------------------------------------------------------------
    def call_interrupt(self, i):
        #0 EXT0 0x0003
        #1 T0   0x000B
        #2 EXT1 0x0013
        #3 T1   0x001B
        #4 INTS 0x0023
        self.cur_int = i
        addr = 0x0004 #self.int_vectors[i]
        #print 'int', addr
        self.call(addr)
        
    #-------------------------------------------------------------------
    def jump(self, addr):
        self.set_pc(addr)
        
    #-------------------------------------------------------------------
    def jump_rel(self, v):
        offset = val8(v)
        if self.debug:
            self.log("     jump_rel %d" % (offset) )
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
        
        #if self.freg[self.INTCON] & BIT7:
        self.freg[self.INTCON] |= BIT7
        self.int_enabled = True
        
    #-------------------------------------------------------------------
    def skip_next_inst(self):
        if self.debug:
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
    def proc_int(self):
        intcon = self.freg[0xB]
        if intcon & BIT7 == 0:
            return
        if intcon & 7:  #T0IF, 
            if intcon & BIT4 and intcon & BIT1:
                # RB0/INT flag
                self.int_enabled = False
                self.call_interrupt(1)
                return
            if intcon & BIT5 and intcon & BIT2:
                self.int_enabled = False
                self.call_interrupt(2)
                return
            if intcon & BIT3 and intcon & BIT0:
                self.int_enabled = False
                self.call_interrupt(0)
                return
            
    #-------------------------------------------------------------------
    def proc_tmr0(self):
        if self.tmr0_rate > 0:
            if self.ticks < self.tmr0_rate:
                return
        self.ticks = 0
        #if self.freg[0xB] & BIT2:
        #    return
        tmr0 = self.freg[0x01]
        if tmr0 < 0xff:
            tmr0 += 1
        elif tmr0 == 0xff:
            tmr0 = 0
            # set T0IF : bit2 of INTCON 0xB
            self.freg[0xB] |= BIT2
        self.freg[0x01] = tmr0
            
    #-------------------------------------------------------------------
    def load_inst(self):
        self.ticks += 1
        if self.tmr0_enabled :
            self.proc_tmr0()
            
        #if self.t1_enabled:
            #self.proc_timer1()
            
        if self.int_enabled :
            self.proc_int()
            
        # get current program counter 
        addr = self.pc
        self.inst_addr = self.pc
        if self.debug:
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
        
        #self.log('**************** ', hex(msb), hex(lsb))
        
        # self.set_pc(self.pc + blen)
        self.pc = self.pc + 1
        
        #self.log('**************** pc ', hex(self.pc))
        f = inst_handler[msb]
        if self.debug:
            opcode = (msb << 8) + lsb
            s = get_pic14_inst_str(opcode, msb, lsb)
            self.log("--------- %04x %02x %02x <%s>" % (addr, msb, lsb, s))
            
        #self.log("asm_code    ", self.c_line, self.asm_code)
        #self.log("     ", s)
        f(self, msb, lsb)
        
        #ch = self.get_uart_put_ch()
        #if ch != 0:
            #self.sbuf_list.append(ch)
            
    #-------------------------------------------------------------------
    def load_inst_no_log(self):
        addr = self.pc+self.pc
        lsb = self.code_space[addr]
        msb = self.code_space[addr + 1] & 0x3f
        
        self.pc = self.pc + 1

        f = inst_handler[msb]
        f(self, msb, lsb)
            
    #-------------------------------------------------------------------
    def enable_debug(self, flag):
        self.debug = flag
        
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
    def step(self, count=1):
        if self.stopped:
            return False
        
        self.step_mode = None
        if self.debug:
            self.load_inst()
        else:
            for i in range(count):
                self.ticks += 1
                if self.tmr0_enabled :
                    self.proc_tmr0()
                                    
                if self.int_enabled :
                    self.proc_int()
                addr = self.pc+self.pc
                lsb = self.code_space[addr]
                msb = self.code_space[addr + 1] & 0x3f
                
                self.pc += 1
        
                f = inst_handler[msb]
                f(self, msb, lsb)
                
                if self.err or self.pc == 0:
                    break            
        
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
                
        
        
    
    
