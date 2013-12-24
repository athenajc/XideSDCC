import os
import sys
import thread
import threading
import time
import Queue
import wx

from define import *
from table import *
from inst import *
from utils import *
from hex_scan import hex_scan, hex_scan_to_map
import rst

bits = [1,2,4,8,0x10,0x20,0x40,0x80]

       
        
class Sim():
    def __init__(self, frame, file_path, source_list, command):
        
        self.frame = frame
        self.hex_path = file_path
        self.file_path = file_path.replace('.ihx', '.c')
        self.source_list = source_list
        self.mode = command
        self.inst_addr = 0
        self.mcu_name = '8051'
        if command == 'debug':
            self.debug = True
        else:
            self.debug = False
        self.step_mode = None
        self.step_over_mode = False
        self.stack_depth = 0
        
        self.int_vectors = [0x3, 0x0B, 0x13, 0x1B, 0x23]
        self.ie = 0
        self.int_enabled = False
        self.int_flag = 0
        self.t0_input = 0
        self.t1_input = 0
        self.cur_int = None
        self.INT_EXT0 = 0
        self.INT_T0 = 1
        self.INT_EXT1 = 2
        self.INT_T1 = 3
        self.INT_UART = 4
        self.pin = [0] * 40
        
        symbol_table.sort()
        self.symbol_table = symbol_table
        self.symbol_str = symbol_str #array_list(symbol_str, 256)
        self.op_str = op_str #array_list(op_str, 512)
        
        self.op_n_lst = []
        for t in symbol_table:
            self.op_n_lst.append(t[1])
            
        self.addr_map_lst = rst.rst_scan(source_list)
        self.c_line = 0
        self.asm_code = ""
        self.c_file = ""
        
        self.err = False
        #self.sfr = SfrDefine()
        self.a = 0
        self.b = 0
        self.pc = 0
        self.c = 0
        self.ac = 0
        self.ov = 0
        self.psw = 0
        self.bank = 0
        self.bank_addr = 0
                
        self.P0    = 0x80
        self.SP    = 0x81
        self.DPL   = 0x82
        self.DPH   = 0x83
        self.PCON  = 0x87
        self.TCON  = 0x88
        self.TMOD  = 0x89
        self.TL0   = 0x8A
        self.TL1   = 0x8B
        self.TH0   = 0x8C
        self.TH1   = 0x8D
        self.P1    = 0x90
        self.SCON  = 0x98
        self.SBUF  = 0x99
        self.P2    = 0xA0
        self.IE    = 0xA8
        self.P3    = 0xB0
        self.IP    = 0xB8
        self.T2CON = 0xC8
        self.T2MOD = 0xC9
        self.RCAP2L= 0xCA
        self.RCAP2H= 0xCB
        self.TL2   = 0xCC
        self.TH2   = 0xCD
        self.PSW   = 0xD0
        self.ACC   = 0xE0
        self.A     = 0xE0
        self.B     = 0xF0
        
        #bits addressing
        self.RI  = 0x98
        self.TI  = 0x99
                
        self.B_RI  = 0x98
        self.B_TI  = 0x99
        self.B_RB8 = 0x9A
        self.B_TB8 = 0x9B
        self.B_REN = 0x9C
        self.B_SM2 = 0x9D
        self.B_SM1 = 0x9E
        self.B_SM0 = 0x9F
        
        self.sbuf_list = []
        self.mem = [0] * 256
        self.ext_mem = [0] * 64 * 1024
        self.code_space = [0] * 4 * 1024
        self.reg = [0] * 256
        
        # initial stack
        self.reg[self.SP] = 0x07
        self.stack = []
        self.sp_addr = 0x60
        
        self.t0_enabled = False
        self.t1_enabled = False
        self.t0_count = 0
        self.t1_count = 0
        self.t0_mode = 0
        self.t1_mdoe = 0
        
        self.reg_table = {
            'pc':0, 'dptr':0, 'sp':0, 
            'a':0, 'b':0, 'c':0, 'ac':0, 'ov':0,
            'r0':0,'r1':0,'r2':0,'r3':0,'r4':0,'r5':0,'r6':0,'r7':0,
            'p0':0, 'p1':0, 'p2':0, 'p3':0,  
            'dpl':0, 'dph':0,
            'pcon':0, 'tcon':0, 'tmod':0,
            'tl0':0,  'tl1':0,  'th0':0,  'th1':0, 'scon':0, 'sbuf':0,
            'ie':0,   'ip':0,   'psw':0,  'acc':0,
            'ri':0,   'ti':0,   'rb8':0,  'tb8':0, 'ren':0,  'sm0':0, 'sm1':0, 'sm2':0,
        }
        
        self.sfr_map = {
                'r0':0,'r1':1,'r2':2,'r3':3,'r4':4,'r5':5,'r6':6,'r7':7,
                'p0':   0x80,
                'p1':   0x90,
                'p2':   0xa0,
                'p3':   0xb0,
                'sp':   0x81,
                'dpl':  0x82,
                'dph':  0x83,
                'pcon': 0x87,
                'tcon': 0x88,
                'tmod': 0x89,
                'tl0':  0x8a,
                'tl1':  0x8b,
                'th0':  0x8c,
                'th1':  0x8d,
                'scon': 0x98,
                'sbuf': 0x99,
                'ie':   0xa8,
                'ip':   0xb8,
                'psw':  0xd0,
                'acc':  0xe0,
                'b':    0xf0,
            }

        self.addr_sfr = {}
        for k, v in self.sfr_map.items():
            self.addr_sfr[v] = k
            
        text = read_whole_file(self.hex_path)
        self.log(self.hex_path + "\n")

        self.code_map = hex_scan_to_map(self.hex_path, text, self.mcu_name)
        self.load_code(text)
        
    #-------------------------------------------------------------------
    def disassembly(self):
        return hex_scan(self.hex_path, self.mcu_name)
    
    #-------------------------------------------------------------------
    def log1(self, *args):
        pass
    
    #-------------------------------------------------------------------
    def log(self, *args):
        if not self.debug or self.c_line == 0:
            return
        if self.step_mode != None:
            return
        msg = " "
        for t in args:
            msg = msg + str(t) + " "
        s = get_hh_mm_ss() + msg + "\n"
        #print s
        self.frame.log(s)
        
    #-------------------------------------------------------------------
    def push(self, v):
        if self.debug:
            self.log("     push "+hex(v))
        #self.stack.insert(0, v)
        sp_addr = self.reg[self.SP]
        sp_addr += 1
        self.reg[sp_addr] = v
        self.reg[self.SP] = sp_addr
        #print 'push', hex(sp_addr), v
        # print("     #stack = "+tostring(#self.stack))
        
    #-------------------------------------------------------------------
    def pop(self):
        #v1 = self.stack.pop(0)
        sp_addr = self.reg[self.SP]
        v = self.reg[sp_addr]
        sp_addr -= 1
        self.reg[self.SP] = sp_addr
        #print 'pop', hex(sp_addr), v
        if self.debug:
            self.log("     pop "+hex(v))
        return v

    #-------------------------------------------------------------------
    def mem_get_bit(self, bitaddr):
        # mem 0x80 - 0x8F
        if bitaddr < 0x80:
            # 0x20 - 0x2F
            bit = bitaddr & 7
            addr = (bitaddr >> 3) + 0x20
            v = self.mem[addr]
        else:
            # access SFR's bits
            bit = bitaddr & 7
            addr = bitaddr - bit
            v = self.reg[addr]

        if v & (1 << bit):
            return 1
        else:
            return 0
        
    #-------------------------------------------------------------------
    def mem_get_nbit(self, bitaddr):
        # mem 0x80 - 0x8F
        if bitaddr < 0x80:
            # 0x20 - 0x2F
            bit = bitaddr & 7
            addr = (bitaddr >> 3) + 0x20
        else:
            # access SFR's bits
            bit = bitaddr & 7
            addr = bitaddr - bit
            
        v = self.get_mem(addr)

        if v & (1 << bit):
            return 0
        else:
            return 1
        
    #-------------------------------------------------------------------
    def mem_set_bit(self, bitaddr, b):
        # mem 0x80 - 0x8F
        if bitaddr < 0x80:
            # 0x20 - 0x2F
            bit = bitaddr & 7
            addr = (bitaddr >> 3) + 0x20
            v = self.mem[addr]
        else:
            # access SFR's bits
            bit = bitaddr & 7
            addr = bitaddr - bit
            v = self.reg[addr]
                   
        if b == 1:
            v |= (1 << bit)
        else:
            v &= ~(1 << bit)
            
        self.set_mem(addr, v)
        
        if addr >= 0x80:
            # Access SFR
            if addr == self.PSW:
                self.set_psw(v, bit, b)
            elif addr == 0x88:
                self.set_tcon(bit, b)
        
    #-------------------------------------------------------------------
    def get_code_space(self, addr):
        v = self.code_space[addr]
        if self.debug:
            self.log("     get code_space "+tohex(addr,4)+" = "+tohex(v, 0))
        return v
    
    #-------------------------------------------------------------------
    def get_ext_mem(self, addr):
        if addr < 0xff:
            v = self.mem[addr]
        else:
            v = self.ext_mem[addr]
        if self.debug:
            self.log("     get ext mem "+tohex(addr,4)+" = "+tohex(v, 0))
        return v
    
    #-------------------------------------------------------------------
    def set_ext_mem(self, addr, v):
        if self.debug:
            self.log("     set ext mem "+tohex(addr, 4)+" = "+tohex(v, 0))
        if (v > 0xffff) :
            self.log(v, "> 0xffff")
            v = bits_and(v, 0xffff)
        if addr < 0xff:
            self.mem[addr] = v
        else:    
            self.ext_mem[addr] = v
        return v
    
    #-------------------------------------------------------------------
    def get_mem(self, addr):
        if addr < 0x80:
            v = self.mem[addr]
        else:
            v = self.reg[addr]
        if self.debug:
            self.log("     get mem "+tohex(addr,4)+" = "+tohex(v, 0))
        return v    

    #-------------------------------------------------------------------
    def set_mem(self, addr, v):
        if self.debug:
            self.log("     set mem "+tohex(addr, 4)+" = "+tohex(v, 0))
        
        v &= 0xff        
        
        # check if set sfr region
        if addr >= 0x80:
            self.reg[addr] = v
            if addr == self.SP:
                print addr, v
            if addr == 0x8A or addr == 0x8C:
                self.set_timer_count(0)
            elif addr == 0x8B or addr == 0x8D:
                self.set_timer_count(1)
            elif addr == 0x99:
                self.set_sbuf(v)
            elif addr == 0xA8:
                self.set_ie(v)
            elif addr == 0xE0:
                self.a = v
            elif addr == 0xD0:
                self.psw = v
        else:
            self.mem[addr] = v
            
        return v
        
    
    #-------------------------------------------------------------------
    # indirect addressing always access memory, not SFR
    def get_mem_r(self, i):
        addr = self.get_r(i)
        v = self.mem[addr]
        if self.debug:
            self.log("     get mem "+tohex(addr,4)+" = "+tohex(v, 0))
        return v    
    
    #-------------------------------------------------------------------
    # indirect addressing always access memory, not SFR
    def set_mem_r(self, i, v):
        addr = self.get_r(i)

        if self.debug:
            self.log("     set mem "+tohex(addr, 4)+" = "+tohex(v, 0))
        
        if (v > 0xff) :
            if self.debug:
                self.log(v, "> 0xff")
            v = bits_and(v, 0xff)
    
        self.mem[addr] = v
        
        # check if set sfr region
        if addr >= 0x80 and addr < 0xFF:
            if addr == self.ACC:
                self.a = v
        
        return v
            
    #-------------------------------------------------------------------
    def set_psw(self, psw, bit, v):
        #/* PSW */
        #__sbit __at 0xD0 P          ;
        #__sbit __at 0xD1 FL         ;
        #__sbit __at 0xD2 OV         ;
        #__sbit __at 0xD3 RS0        ;
        #__sbit __at 0xD4 RS1        ;
        #__sbit __at 0xD5 F0         ;
        #__sbit __at 0xD6 AC         ;
        #__sbit __at 0xD7 CY         ;
        self.psw = psw
        if bit == 3 or bit == 4:
            self.bank = (psw >> 3) & 3
            self.bank_addr = self.bank * 8
        elif bit == 7:
            self.c = v
        elif bit == 6:
            self.ac = v
        elif bit == 2:
            self.ov = v
            
    #-------------------------------------------------------------------
    def set_sbuf(self, v):
        #scon = self.mem[self.SCON]
        # check if TI and RI both 0
        #if (scon & 3) == 0 and sbuf != 0: 
        self.mem_set_bit(self.TI, 1)
        self.sbuf_list.append(v)
        
    #-------------------------------------------------------------------
    def check_if_trigger_timer0(self):
        # TMOD : 3:GATE   2:C/T   1:M1   0:M0
        tmod = self.reg[0x89]
        tcon = self.reg[0x88]
        if tmod & BIT3 and tcon & BIT4:
            self.trigger_timer(0)
            
    #-------------------------------------------------------------------
    def check_if_trigger_timer1(self):
        # TMOD : 7:GATE   6:C/T   5:M1   4:M0
        tmod = self.reg[0x89]
        tcon = self.reg[0x88]
        if tmod & BIT7 and tcon & BIT6:
            self.trigger_timer(1)
            
    #-------------------------------------------------------------------
    def set_input(self, k, v):
        #EX1	IE.2	Enable/disable external interrupt 1.
        #EX0	IE.0	Enable/disable external interrupt 0.
        ie = self.reg[0xA8]
        
        if k == 'int0':
            if ie & BIT7 and ie & BIT0:
                tcon = self.reg[0x88]
                if v == 1 and (tcon & BIT0) == 0:
                    # TCON bit0 is 0 means low level trigger 
                    if self.pin[12] == 0:
                        self.int_flag |= BIT0
                        self.reg[0x88] |= BIT1
                        self.check_if_trigger_timer0()
                elif v == 0 and (tcon & BIT0) == 1:
                    # TCON bit0 is 1 means falling edge trigger 
                    if self.pin[12] == 1:
                        self.int_flag |= BIT0
                        self.reg[0x88] |= BIT1
                        self.check_if_trigger_timer0()
                self.pin[12] = v
                
        elif k == 'int1':
            if ie & BIT7 and ie & BIT2:
                tcon = self.reg[0x88]
                if v == 1 and (tcon & BIT2) == 0:
                    # TCON bit2 is 0 means low level trigger timer1 int
                    if self.pin[13] == 0:
                        self.int_flag |= BIT2
                        self.reg[0x88] |= BIT3
                        self.check_if_trigger_timer1()
                elif v == 0 and (tcon & BIT2) == 1:
                    # TCON bit0 is 1 means falling edge trigger 
                    if self.pin[13] == 1:
                        self.int_flag |= BIT2
                        self.reg[0x88] |= BIT3
                        self.check_if_trigger_timer1()
                self.pin[13] = v
                
        elif k == 'uart':
            # set RI = 1
            self.mem_set_bit(self.RI, 1)
            self.reg[self.SBUF] = v
            if ie & BIT7 and ie & BIT4:
                self.int_flag |= BIT4
                self.reg[0x88] |= BIT1
                
        elif k == 't0':
            if self.pin[14] == 1 and v == 0:
                self.t0_input += 1
            self.pin[14] = v
        elif k == 't1':
            if self.pin[15] == 1 and v == 0:
                self.t1_input += 1
            self.pin[15] = v
            
    #-------------------------------------------------------------------
    def set_ie(self, v):
        #IE: Interrupt Enable Register (bit addressable)
       
        #If the bit is 0, the corresponding interrupt is disabled. If the bit is 1, the corresponding interrupt is enabled.
        
        #(msb) |EA|-|ET2|ES|ET1|EX1|ET0|EX0| (lsb)
        
        #Symbol	Position	Name & Significance
        #EA	IE.7	Disables all interrupts. If EA = 0, no interrupt will be acknowledged. If EA = 1, each interrupt source is individually enabled or disabled by setting or clearing its enable bit.
        #-	IE.6	Not implemented.
        #ET2	IE.5	Enable/disable Timer 2 overflow or capture interrupt. (8052 only).
        #ES	IE.4	Enable/disable serial port interrupt.
        #ET1	IE.3	Enable/disable Timer 1 overflow interrupt.
        #EX1	IE.2	Enable/disable external interrupt 1.
        #ET0	IE.1	Enable/disable Timer 0 overflow interrupt.
        #EX0	IE.0	Enable/disable external interrupt 0.
        #INTERRUPT SOURCE	VECTOR ADDRESS
        #IE0	0003H
        #TF0	000BH
        #IE1	0013H
        #TF1	001BH
        #RI & TI	0023H
        #TF2 & EXF2 (8052 only)	002BH
        self.ie = v
        if v & BIT7:
            self.int_enabled = True
        else:
            self.int_enabled = False

    
    #-------------------------------------------------------------------
    def set_ip(self, bit, v):
        #IP: Interrupt Priority Register (bit addressable)
       
        #If the bit is 0, the corresponding interrupt has a lower priority and if the bit is 1, the corresponding interrupt has a higher priority.
       
        #(msb) |-|-|PT2|PS|PT1|PX1|PT0|PX0| (lsb)
       
        #Symbol	Position	Name & Significance
        #-	IP.7	Not implemented.
        #-	IP.6	Not implemented.
        #PT2	IP.5	Defines the Timer 2 interrupt priority level (8052 only).
        #PS	IP.4	Defines the serial port interrupt priority level.
        #PT1	IP.3	Defines Timer 1 interrupt priority level.
        #PX1	IP.2	Defines External interrupt 1 priority level.
        #PT0	IP.1	Defines Timer 0 interrupt priority level.
        #PX0	IP.0	Defines External interrupt 0 priority level.
        pass

    #-------------------------------------------------------------------
    def set_tmod(self, bit, v):
        #GATE	When TRx (in TCON) is set and GATE = 1, TIMER/COUNTERx will run only while INTx pin is high (hardware control). When GATE = 0, TIMER/COUNTERx will run only while TRx = 1 (software control).
        #C/T	Timer or Counter selector. Cleared for Timer operation (input from internal system clock). Set for counter operation (input from Tx input pin).
        #M1	Mode selector bit. (see note)
        #M0	Mode selector bit. (see note)      
        if self.debug:
            self.log("     set TMOD bit " + str(bit) + " = "+hex(v))
        pass
    
    #-------------------------------------------------------------------
    def set_timer_count(self, index):
        if index == 0:
            tmod = self.reg[0x89]
            th = self.reg[self.TH0]
            tl = self.reg[self.TL0]
            # Mode select : bit 0, bit 1
            self.t0_mode = mode = tmod & 3
            if mode == 0:  # 13 bits, max 8192
                self.t0_count = (th << 5) | (tl & 0x1f)
            elif mode == 1: # 16 bits, max 65536
                self.t0_count = (th << 8) | tl
            elif mode == 2: # 8 bits, max 256
                self.t0_count = tl
            elif mode == 3: # 8 bits, max 256
                self.t0_count = tl
                
        elif index == 1:
            tmod = self.reg[0x89] >> 4
            th = self.reg[self.TH1]
            tl = self.reg[self.TL1]
            # Mode select : bit 0, bit 1
            self.t1_mode = mode = tmod & 3
            if mode == 0:  # 13 bits, max 8192
                self.t1_count = (th << 5) | (tl & 0x1f)
            elif mode == 1: # 16 bits, max 65536
                self.t1_count = (th << 8) | tl
            elif mode == 2: # 8 bits, max 256
                self.t1_count = tl
                
    #-------------------------------------------------------------------
    def trigger_timer(self, i):
        if i == 0:
            self.set_timer_count(0)
            self.t0_enabled = True
        elif i == 1:
            self.set_timer_count(1)
            self.t1_enabled = True
            
    #-------------------------------------------------------------------
    def set_tcon(self, bit, v):
        #TF1	TCON.7	Timer 1 overflow flag. Set by hardware when Timer/Counter 1 overflows. Cleared by hardware as processor vectors to the interrupt service routine.
        #TR1	TCON.6	Timer 1 run control bit. Set/cleared by software to turn Timer/Counter 1 On/Off.
        #TF0	TCON.5	Timer 0 overflow flag. Set by hardware when Timer/Counter 0 overflows. Cleared by hardware as processor vectors to the interrupt service routine.
        #TR0	TCON.4	Timer 0 run control bit. Set/cleared by software to turn Timer/Counter 0 On/Off.
        #IE1	TCON.3	External Interrupt 1 edge flag. Set by hardware when external interrupt edge is detected. Cleared by hardware when interrupt is processed.
        #IT0	TCON.2	Interrupt 1 type control bit. Set/cleared by software to specify falling edge/low level triggered external interrupts.
        #IE0	TCON.1	External Interrupt 0 edge flag. Set by hardware when external interrupt edge is detected. Cleared by hardware when interrupt is processed.
        #IT0	TCON.0	Interrupt 0 type control bit. Set/cleared by software to specify falling edge/low level triggered external interrupts.        
        if self.debug:
            self.log("     set TCON bit " + str(bit) + " = "+hex(v))
            
        if bit == 6: # TR1
            # if not Gate set, trigger at once
            if self.reg[0x89] & BIT7 == 0:
                self.trigger_timer(1)
        elif bit == 4: # TR0 - trigger timer 0
            # if not Gate set, trigger at once
            if self.reg[0x89] & BIT3 == 0:
                self.trigger_timer(0)
        
    #-------------------------------------------------------------------
    def get_a(self):
        return self.reg[0xE0]
        
    #-------------------------------------------------------------------
    def set_a(self, v):
        #self.log1("     set a = "+hex(v))
        v &= 0xff
        self.a = v
        #self.set_sfr('acc', v)
        self.reg[0xE0] = v
        
    #-------------------------------------------------------------------
    def add_a(self, v, c):
        #self.log1("     set a = "+hex(v))
        v += c
        self.ac = self.ov = self.c = 0
        
        #/* PSW */
        #__sbit __at 0xD2 OV         ;
        #__sbit __at 0xD6 AC         ;
        #__sbit __at 0xD7 CY         ;
        psw = self.reg[0xD0] & 0xC4  # clear bit2, 6, 7 at first
        
        a = self.reg[0xE0]
        if (a & 0xf) + (v & 0xf) > 0xf:
            self.ac = 1
            psw |= BIT6
            
        v += a
        if v > 0xff:
            self.ov = 1
            self.c = 1
            v &= 0xff
            psw |= BIT7 | BIT2
            
        self.reg[0xD0] = self.psw = psw
        self.reg[0xE0] = self.a = v

    #-------------------------------------------------------------------
    def set_b(self, v):
        #self.log1("     set b = "+hex(v))
        self.b = v
        #self.set_sfr('b', v)
        self.reg[0xF0] = v
        
    #-------------------------------------------------------------------
    def set_c(self, v):
        #self.log1("     set c = "+hex(v))
        if v == 0 :
            self.c = 0
            self.reg[0xD0] &= BIT7
        else:
            self.c = 1
            self.reg[0xD0] |= BIT7
            
    #-------------------------------------------------------------------
    def get_c(self, v):
        return (self.reg[0xD0] >> 7) & 1

    #-------------------------------------------------------------------
    def set_ov(self, v):
        #self.log1("     set ov = "+hex(v))
        if (v == 0) :
            self.ov = 0
            self.reg[0xD0] &= BIT2
        else:
            self.ov = 1
            self.reg[0xD0] |= BIT2
        
    #-------------------------------------------------------------------
    def set_ac(self, v):
        #self.log1("     set ac = "+hex(v))
        if (v == 0) :
            self.ac = 0
            self.reg[0xD0] &= BIT6
        else:
            self.ac = 1
            self.reg[0xD0] |= BIT6

    #-------------------------------------------------------------------
    def get_ac(self, v):
        return (self.reg[0xD0] >> 6) & 1
        
    #-------------------------------------------------------------------
    def get_reg(self, k):
        return self.reg_table[k]
        
    #-------------------------------------------------------------------
    def update_sfr(self):
        self.reg_table['dptr'] = (self.reg[self.DPH] << 8) + self.reg[self.DPL]
        self.reg_table['pc'] = self.pc
        for k, v in self.sfr_map.items():
            if v < 0x80:
                self.reg_table[k] = self.mem[v]
            else:
                self.reg_table[k] = self.reg[v]

    #-------------------------------------------------------------------
    def set_r(self, i, v):
        i &= 0x7
        self.mem[self.bank_addr + i] = v
        return v
    
    #-------------------------------------------------------------------
    def get_r(self, i):
        i &= 0x7
        return self.mem[self.bank_addr + i]
    
    #-------------------------------------------------------------------
    # DPH 0x83  
    # DPL 0x82
    def inc_dptr(self):
        dph = self.DPH
        dpl = self.DPL
        l = self.reg[dpl] + 1
        if l > 0xff:
            l &= 0xff
            h = (self.reg[dph] + 1) & 0xff
            self.reg[dph] = h
            
        self.reg[dpl] = l
                
    #-------------------------------------------------------------------
    def set_dptr(self, h, l):
        self.reg[0x83] = h
        self.reg[0x82] = l
        
    #-------------------------------------------------------------------
    def get_dptr(self):
        return (self.reg[0x83] << 8) | self.reg[0x82]
        
    #-------------------------------------------------------------------
    def set_pc(self, v):
        if self.debug:
            self.log("     set pc = "+tohex(v, 4))
        self.pc = v
        
    #-------------------------------------------------------------------
    def call_interrupt(self, i):
        #0 EXT0 0x0003
        #1 T0   0x000B
        #2 EXT1 0x0013
        #3 T1   0x001B
        #4 INTS 0x0023
        self.cur_int = i
        addr = self.int_vectors[i]
        #print 'int', addr
        self.call(addr)
                
    #-------------------------------------------------------------------
    def jump(self, addr):
        self.set_pc(addr)
        
    #-------------------------------------------------------------------
    def jump_rel(self, v):
        if v & 0x80:
            v = -(0xff - (v - 1))

        if self.debug:
            self.log("     jump_rel  "+str(v) )
        self.pc += v
        
    #-------------------------------------------------------------------
    def call(self, addr):
        pc = self.pc
        pcl = pc & 0xff
        pch = (pc >> 8) & 0xff
        self.push(pcl)
        self.push(pch)
        
        self.set_pc(addr)
        self.stack_depth += 1
        
    #-------------------------------------------------------------------
    def ret(self):
        #if self.stack_depth == 0:
        #    err = True
        pch = self.pop()
        pcl = self.pop()
        addr = (pch << 8) | pcl
        self.set_pc(addr)
        self.stack_depth -= 1
        
    #-------------------------------------------------------------------
    def reti(self):
        """ return function from interrupt """
        self.ret()
        
        # if IE all still enabled, re-enable interrupt
        if self.reg[0xA8] & BIT7:
            self.int_enabled = True
        else:
            self.int_enabled = False
            
        # if timer0 interrupt, clear TCON bit5 TF0
        if self.cur_int == self.INT_T0:
            self.reg[0x88] &= ~BIT5
        elif self.cur_int == self.INT_EXT0:
            self.reg[0x88] &= ~BIT1
        elif self.cur_int == self.INT_EXT1:
            self.reg[0x88] &= ~BIT3
            
    #-------------------------------------------------------------------
    def array_list(self, table, n):
        lst = []
        for i in range(n):
            lst.append(0)
        for t in table:
            lst[t[0]] = t[1]
        return lst   
    
    #-------------------------------------------------------------------
    def code_space_fill(self, addr, sz, ddstr):
        i1 = 0
        i2 = 2
        #--print(tohex(addr, 4), tohex(sz, 2), ddstr)
        for i in range(sz):
            dd = ddstr[i1:i2]
            #self.log(hex(addr+i), dd)
            self.code_space[addr + i] = int("0x" + dd, 16)
            #self.log(tohex(addr + i, 4), dd, tohex(self.reg[addr + i], 2))
            i1 += 2
            i2 += 2
                    
    #-------------------------------------------------------------------
    def load_code(self, text):    
        # for each line, :llaaaatt
        for line in text.split('\n'):
            ll   = line[1:3]
            aaaa = line[3:7]
            tt   = line[7:9]
    
            llen = tonumber(ll, 16)
            addr = tonumber(aaaa, 16)
            ttype = tonumber(tt, 16)
            
            if (ttype == 0) :
                self.code_space_fill(addr, llen, line[9: 10 + llen*2])
                
        #for debug print code space
        #j = 0
        #addr = 0
        #for i in range(0x20) :
            #a = addr + j
            #s = ""
            #for k in range(7) :
                #t = tohex(self.code_space[a+k], 2)+"  "
                #s = s +t
    
            #print(s)
            #j = j + 8
            
    #-------------------------------------------------------------------
    def proc_int(self):
        #do the interrupt work
        ip = self.reg[self.IP]
        flag = self.int_flag
        
        if ip != 0:
            # process high ip at first
            for i in range(6):
                bit = bits[i]
                if flag & bit and ip & bit:
                    self.int_enabled = False
                    self.int_flag &= ~bit
                    self.call_interrupt(i)
                    return
            
        for i in range(6):
            bit = bits[i]
            if flag & bit:
                self.int_enabled = False
                self.int_flag &= ~bit
                self.call_interrupt(i)
                return
        
    #-------------------------------------------------------------------
    def proc_timer0(self):
        # do the timer work
        # IE   bits  -  7:EA   6: -   5:ET2  4:ES   3:ET1  2:EX1  1:ET0  0:EX0
        # TCON bits  -  7:TR1  6:TR1  5:TF0  4:TR0  3:IE1  2:IT1  1:IE0  0:IT0
        # TR0 = tcon & BIT4
        # TR1 = tcon & BIT6
        # set TF0 tcon |= BIT5
        if self.reg[0x88] & BIT4 and self.t0_count > 0:
            # check C/T counter/Timer
            if self.reg[0x89] & BIT2 == 0:
                self.t0_count -= 1
            elif self.t0_input > 0:
                self.t0_count -= 1
                self.t0_input = 0
                
            if self.t0_count <= 0:
                # set bit TF0 = 1
                self.reg[0x88] |= BIT5
                
                # trigger timer0 interrupt ET0 - BIT1
                if self.ie & BIT1:
                    self.int_flag |= BIT1
                
                # if mode = 2, reset initial count
                if self.t0_mode == 2:
                    # copy value from TH0 to TL0
                    self.t0_count = self.reg[self.TL0] = self.reg[self.TH0]
                    
    #-------------------------------------------------------------------
    def proc_timer1(self):
        # do the timer work
        if self.reg[0x88] & BIT6 :
            # check C/T counter/Timer
            if self.reg[0x89] & BIT6 == 0:
                self.t1_count -= 1
            elif self.t1_input > 0:
                self.t1_count -= 1
                self.t1_input = 0
                
            if self.t1_count == 0:
                # set bit TF1 = 1
                self.reg[0x88] |= BIT7
                # trigger timer1 interrupt
                if self.ie & BIT3:
                    self.int_flag |= BIT3
                    

    #-------------------------------------------------------------------
    def load_and_debug_inst(self):
        if self.t0_enabled :
            self.proc_timer0()
            
        if self.t1_enabled:
            self.proc_timer1()
            
        if self.int_enabled:
            self.proc_int()
        # get current program counter 
        self.inst_addr = addr = self.pc
        
        if addr < len(self.addr_map_lst):
            t = self.addr_map_lst[addr]
            if t != 0:
                if t[0] == "":
                    self.c_file = self.file_path
                else:
                    self.c_file = t[0]
                self.c_line = t[1]
                self.asm_code = t[2]
        else:
            self.c_file = ""
            self.c_line = 0
            self.asm_code = ""
        self.log('------------', self.c_file, self.c_line)
        rom = self.code_space
        inst_code = rom[addr]
        
        op_n = self.op_n_lst[inst_code]
        if op_n > 1:
            dd1 = rom[addr + 1]
            if op_n > 2:
                dd2 = rom[addr + 2]
                dd3 = rom[addr + 3]
            else:
                dd2 = dd3 = 0
        else:
            dd1 = dd2 = dd3 = 0

        s = self.code_map.get(addr, "")
        if s != "":
            self.log(s)
            
        # move the program counter to the next instruction
        # self.set_pc(self.pc + blen)
        self.pc = self.pc + op_n
    
        f = inst_handler[inst_code]
        f(self, inst_code, dd1, dd2, dd3)
        
            
    #-------------------------------------------------------------------
    def load_inst(self):
        if self.t0_enabled :
            self.proc_timer0()
            
        if self.t1_enabled:
            self.proc_timer1()
            
        if self.int_enabled and self.int_flag :
            self.proc_int()
        
        # get current program counter 
        self.inst_addr = addr = self.pc
        #print hex(addr), 'sp', self.reg[self.SP]
        rom = self.code_space
        inst_code = rom[addr]
        
        op_n = self.op_n_lst[inst_code]
        if op_n > 1:
            dd1 = rom[addr + 1]
            if op_n > 2:
                dd2 = rom[addr + 2]
                dd3 = rom[addr + 3]
            else:
                dd2 = dd3 = 0
        else:
            dd1 = dd2 = dd3 = 0
            
            
        # move the program counter to the next instruction
        self.pc += op_n
    
        inst_handler[inst_code](self, inst_code, dd1, dd2, dd3)
        
            
    #-------------------------------------------------------------------
    def enable_debug(self, flag):
        self.debug = flag
        
    #-------------------------------------------------------------------
    def start(self):
        self.stopped = False
        self.running = True
        set_sim(self)

        self.mode = 'run'
        self.pc = 0x0
        self.cmd_queue = Queue.Queue()
        
        i = 100000
        if self.debug:
            while self.c_line == 0:
                i -= 1
                if i == 0:
                    break
                self.load_and_debug_inst()
            
    #-------------------------------------------------------------------
    def step(self, count = 1):
        if self.stopped:
            return False
        
        self.step_mode = None
        
        if self.debug:
            self.load_and_debug_inst()
        else:
            for i in range(count):
                self.load_inst()
                if self.err or self.pc == 0:
                    break
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
            if self.debug:
                self.load_and_debug_inst()
            else:
                self.load_inst()
            if i > 100:
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
    

#---- for testing -------------------------------------------------------------
if __name__ == '__main__':    
    # temp_convert()
    # print_symbol_table()
    fn = "/home/athena/src/8051/t0/t0.ihx"
    ihx_scan(None, fn)
    #sim_run(fn)


