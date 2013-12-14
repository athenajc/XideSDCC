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
import rst

class Obj():
    def __init__(self):
        pass
       
        
class Sim():
    def __init__(self, frame, file_path, source_list, command):
        self.frame = frame
        self.file_path = file_path
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
        
        self.ie = 0
        self.int_enabled = False
        self.int_flag = 0
        self.int_ext0 = 0
        self.int_ext1 = 0
        self.cur_int = None
        self.INT_EXT0 = 0
        self.INT_T0 = 1
        self.INT_EXT1 = 2
        self.INT_T1 = 3
        self.INT_UART = 4
        
        symbol_table.sort()
        self.symbol_table = symbol_table
        self.symbol_str = symbol_str #array_list(symbol_str, 256)
        self.op_str = op_str #array_list(op_str, 512)
        
        self.addr_map_lst = rst.rst_scan(source_list)
        self.c_line = 0
        self.asm_code = ""
        self.c_file = ""
        
        self.err = False
        #self.sfr = SfrDefine()
        self.a = 0
        self.b = 0
        self.dptr = 0
        self.pc = 0
        self.sp = 0
        self.mem = []
        self.stack = []
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
        self.code_space = [0] * 64 * 1024
        self.reg = [0] * 32
        
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
                'ri':   0x98,
                'ti':  0x99,
                'rb8': 0x9A,
                'tb8': 0x9B,
                'ren': 0x9C,
                'sm2': 0x9D,
                'sm1': 0x9E,
                'sm0': 0x9F,
                'r0':0,'r1':1,'r2':2,'r3':3,'r4':4,'r5':5,'r6':6,'r7':7,
            }
        self.SBUF = self.sfr_map['sbuf']
        self.RI  = self.sfr_map['ri']
        self.TI  = self.sfr_map['ti']
        
        self.addr_sfr = {}
        for k, v in self.sfr_map.items():
            self.addr_sfr[v] = k
            
        self.inst_handler = [
            [I_ACALL, inst_acall],
            [I_ADD,   inst_add],
            [I_ADDC,  inst_addc],
            [I_AJMP,  inst_ajmp],
            [I_ANL,   inst_anl],
            [I_CJNE,  inst_cjne],
            [I_CLR,   inst_clr],
            [I_CPL,   inst_cpl],
            [I_DA,    inst_da],
            [I_DEC,   inst_dec],
            [I_DIV,   inst_div],
            [I_DJNZ,  inst_djnz],
            [I_INC,   inst_inc],
            [I_JB,    inst_jb],
            [I_JBC,   inst_jbc],
            [I_JC,    inst_jc],
            [I_JMP,   inst_jmp],
            [I_JNB,   inst_jnb],
            [I_JNC,   inst_jnc],
            [I_JNZ,   inst_jnz],
            [I_JZ,    inst_jz],
            [I_LCALL, inst_lcall],
            [I_LJMP,  inst_ljmp],
            [I_MOV,   inst_mov],
            [I_MOVC,  inst_movc],
            [I_MOVX,  inst_movx],
            [I_MUL,   inst_mul],
            [I_NOP,   inst_nop],
            [I_ORL,   inst_orl],
            [I_POP,   inst_pop],
            [I_PUSH,  inst_push],
            [I_RET,   inst_ret],
            [I_RETI,  inst_reti],
            [I_RL,    inst_rl],
            [I_RLC,   inst_rlc],
            [I_RR,    inst_rr],
            [I_RRC,   inst_rrc],
            [I_SETB,  inst_setb],
            [I_SJMP,  inst_sjmp],
            [I_SUBB,  inst_subb],
            [I_SWAP,  inst_swap],
            [I_XCH,   inst_xch],
            [I_XCHD,  inst_xchd],
            [I_XRL,   inst_xrl],
            [I_UNDEF, inst_undef],
        ]        
        self.inst_handler = array_list(self.inst_handler, 256)
        
        text = read_whole_file(self.file_path)
        self.log(self.file_path + "\n")
        #frame.log(text + "\n")
        
        self.records = self.get_record_table(text, False)
        self.load_code(text)
        
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
    def check_overflow(self, v, v1, v2):
        self.c = 0
        self.ac = 0    
        self.ov = 0
    
        if (v > 0xff) :
            self.c = 1

        if (v > 0xf) :
            self.ac = 1

        if (v < -127 or v > 128) :  # check ov behavior
            self.ov = 1
            
    #-------------------------------------------------------------------
    def push(self, v):
        self.log("     push "+hex(v))
        self.stack.insert(0, v)
        self.sp = len(self.stack)
        self.set_sfr('sp', self.sp)
        # print("     #stack = "+tostring(#self.stack))
        
    #-------------------------------------------------------------------
    def pop(self):
        if len(self.stack) == 0:
            self.log("     pop empty")
            self.stopped = True
            return 0
        v = self.stack.pop(0)
        self.log("     pop "+hex(v))
        self.sp = len(self.stack)
        self.set_sfr('sp', self.sp)
        return v

    #-------------------------------------------------------------------
    def mem_get_bit(self, bitaddr):
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
        
        ## print(bitaddr, bits_rshift(bitaddr, 3), bitaddr % 8) 
        #if bitaddr == self.RI:
            #self.log(' get  RI')
            #return 1
        #if bitaddr == self.TI:
            #self.log(' get  TI sbuf = '+hex(self.mem[self.SBUF]))
            ##self.sbuf_list.append(self.mem[self.SBUF])
            ##return 1

        if v & (1 << bit):
            self.log("     get bit "+tohex(bitaddr, 4), 1)
            return 1
        else:
            self.log("     get bit "+tohex(bitaddr, 4), 0)
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
        else:
            # access SFR's bits
            bit = bitaddr & 7
            addr = bitaddr - bit
        
        #if bitaddr == self.TI or bitaddr == self.RI:
            ##self.log('@---------------- set TI addr = ' + hex(addr))
            #addr = self.SCON
            
        v = self.get_mem(addr)
        
        if b == 1:
            v = setbit(v, bit)
        else:
            v = clearbit(v, bit)
            
        self.set_mem(addr, v)
        
        if addr >= 0x80:
            # Access SFR
            if addr == self.PSW:
                self.set_psw(v, bit, b)
            elif addr == self.TCON:
                self.set_tcon(bit, b)
        
    #-------------------------------------------------------------------
    def get_code_space(self, addr):
        v = self.code_space[addr]
        self.log("     get code_space "+tohex(addr,4)+" = "+tohex(v, 0))
        return v
    
    #-------------------------------------------------------------------
    def get_ext_mem(self, addr):
        if addr < 0xff:
            v = self.mem[addr]
        else:
            v = self.ext_mem[addr]
        self.log("     get ext mem "+tohex(addr,4)+" = "+tohex(v, 0))
        return v
    
    #-------------------------------------------------------------------
    def set_ext_mem(self, addr, v):
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
        v = self.mem[addr]
        self.log("     get mem "+tohex(addr,4)+" = "+tohex(v, 0))
        return v    
    
    #-------------------------------------------------------------------
    def set_mem(self, addr, v):
        if addr == self.SBUF:
            self.log("******* set sbuf = " + tohex(v, 0))
        else:
            self.log("     set mem "+tohex(addr, 4)+" = "+tohex(v, 0))
        
        if (v > 0xff) :
            self.log(v, "> 0xff")
            v = bits_and(v, 0xff)
    
        self.mem[addr] = v
        
        # check if set sfr region
        if addr >= 0x80 and addr <= 0xFF:
            if addr == self.ACC:
                self.a = v
            elif addr == self.SBUF:
                self.set_sbuf(v)
            elif addr == self.PSW:
                self.psw = v
            elif addr == self.TL0 or addr == self.TH0:
                self.set_timer_count(0)
            elif addr == self.TL1 or addr == self.TH1:
                self.set_timer_count(1)
            elif addr == self.IE:
                self.set_ie(v)
        return v
        
    
    #-------------------------------------------------------------------
    # indirect addressing always access memory, not SFR
    def get_mem_r(self, i):
        addr = self.get_r(i)
        v = self.mem[addr]
            
        self.log("     get mem "+tohex(addr,4)+" = "+tohex(v, 0))
        return v    
    
    #-------------------------------------------------------------------
    # indirect addressing always access memory, not SFR
    def set_mem_r(self, i, v):
        addr = self.get_r(i)
        self.log("     set mem "+tohex(addr, 4)+" = "+tohex(v, 0))
        
        if (v > 0xff) :
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
        #self.mem[self.SBUF] = v
        self.sbuf_list.append(v)
                
    #-------------------------------------------------------------------
    def set_input(self, k, v):
        #EX1	IE.2	Enable/disable external interrupt 1.
        #EX0	IE.0	Enable/disable external interrupt 0.
        ie = self.mem[self.IE]
        
        if k == 'int0':
            if ie & BIT7 and ie & BIT0:
                tcon = self.mem[self.TCON]
                if v == 0 and (tcon & BIT0) == 0:
                    # TCON bit0 is 0 means low level trigger 
                    self.int_flag |= BIT0
                    self.mem[self.TCON] |= BIT1
                elif v == 0 and (tcon & BIT0) == 1:
                    # TCON bit0 is 1 means falling edge trigger 
                    if self.int_ext0 == 1:
                        self.int_flag |= BIT0
                        self.mem[self.TCON] |= BIT1
                self.int_ext0 = v
                
        elif k == 'int1':
            if ie & BIT7 and ie & BIT2:
                tcon = self.mem[self.TCON]
                if v == 0 and (tcon & BIT2) == 0:
                    # TCON bit2 is 0 means low level trigger timer1 int
                    self.int_flag |= BIT2
                    self.mem[self.TCON] |= BIT3
                elif v == 0 and (tcon & BIT2) == 1:
                    # TCON bit0 is 1 means falling edge trigger 
                    if self.int_ext1 == 1:
                        self.int_flag |= BIT2
                        self.mem[self.TCON] |= BIT3
                self.int_ext1 = v
                
        elif k == 'uart':
            # set RI = 1
            self.mem_set_bit(self.RI, 1)
            self.mem[self.SBUF] = v
            if ie & BIT7 and ie & BIT4:
                self.int_flag |= BIT4
                self.mem[self.TCON] |= BIT1
                
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
    def set_timer_count(self, index):
        if index == 0:
            tmod = self.mem[self.TMOD]
            th = self.mem[self.TH0]
            tl = self.mem[self.TL0]
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
            tmod = self.mem[self.TMOD]
            th = self.mem[self.TH1]
            tl = self.mem[self.TL1]
            # Mode select : bit 0, bit 1
            self.t1_mode = mode = tmod & 3
            if mode == 0:  # 13 bits, max 8192
                self.t1_count = (th << 5) | (tl & 0x1f)
            elif mode == 1: # 16 bits, max 65536
                self.t1_count = (th << 8) | tl
            elif mode == 2: # 8 bits, max 256
                self.t1_count = tl
                
    #-------------------------------------------------------------------
    def set_tmod(self, bit, v):
        #GATE	When TRx (in TCON) is set and GATE = 1, TIMER/COUNTERx will run only while INTx pin is high (hardware control). When GATE = 0, TIMER/COUNTERx will run only while TRx = 1 (software control).
        #C/T	Timer or Counter selector. Cleared for Timer operation (input from internal system clock). Set for counter operation (input from Tx input pin).
        #M1	Mode selector bit. (see note)
        #M0	Mode selector bit. (see note)      
        self.log("     set TMOD bit " + str(bit) + " = "+hex(v))
        pass
    
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
        self.log("     set TCON bit " + str(bit) + " = "+hex(v))
        if bit == 6: # TR1
            self.set_timer_count(0)
                
            self.t1_enabled = True
        elif bit == 4: # TR0 - trigger timer 0
            self.set_timer_count(1)
                
            self.t0_enabled = True
            
        
    #-------------------------------------------------------------------
    def get_a(self):
        return self.mem[0xE0]
        
    #-------------------------------------------------------------------
    def set_a(self, v):
        self.log1("     set a = "+hex(v))
        self.a = (v)
        #self.set_sfr('acc', v)
        self.mem[0xE0] = v
        
    #-------------------------------------------------------------------
    def set_b(self, v):
        self.log1("     set b = "+hex(v))
        self.b = (v)
        #self.set_sfr('b', v)
        self.mem[0xF0] = v
        
    #-------------------------------------------------------------------
    def set_c(self, v):
        self.log1("     set c = "+hex(v))
        if (v == 0) :
            self.c = 0
        else:
            self.c = 1
        #self.set_reg('c', v)
        self.mem_set_bit(0xD7, v)

    #-------------------------------------------------------------------
    def get_c(self, v):
        return self.mem_get_bit(0xD7)

    #-------------------------------------------------------------------
    def set_ov(self, v):
        self.log1("     set ov = "+hex(v))
        if (v == 0) :
            self.ov = 0
        else:
            self.ov = 1
        self.set_reg('ov', v)
        
    #-------------------------------------------------------------------
    def set_ac(self, v):
        self.log1("     set ac = "+hex(v))
        if (v == 0) :
            self.ac = 0
        else:
            self.ac = 1
        self.set_reg('ac', v)

    #-------------------------------------------------------------------
    def get_ac(self, v):
        return self.mem_get_bit(0xD6)

    #-------------------------------------------------------------------
    def set_reg(self, k, v):
        self.reg_table[k] = v
        
    #-------------------------------------------------------------------
    def get_reg(self, k):
        return self.reg_table[k]
    
    #-------------------------------------------------------------------
    # Set sfr will set reg table at same time
    def set_sfr(self, k, v):
        self.reg_table[k] = v
        addr = self.sfr_map[k]
        self.mem[addr] = v
        
    #-------------------------------------------------------------------
    def get_sfr(self, k):
        addr = self.sfr_map[k]
        return self.mem[addr]
        
    #-------------------------------------------------------------------
    def update_sfr(self):
        for k, v in self.sfr_map.items():
            self.set_reg(k, self.mem[v])

    #-------------------------------------------------------------------
    def set_r(self, i, v):        
        self.mem[self.bank_addr + i] = v
        return v
    
    #-------------------------------------------------------------------
    def get_r(self, i):
        v = self.mem[self.bank_addr + i]
        return v
    
    #-------------------------------------------------------------------
    def set_dptr(self, v):
        self.log("     set dptr = "+hex(v))
        self.dptr = (v)
        
        self.set_sfr('dpl', v & 0xff)
        self.set_sfr('dph', (v >> 8) & 0xff)
        self.set_reg('dptr', v)
        
    #-------------------------------------------------------------------
    def get_dptr(self):
        dpl = self.get_sfr('dpl')
        dph = self.get_sfr('dph')
        v = (dph << 8) | dpl
        self.dptr = v
        self.set_reg('dptr', v)
        return self.dptr
        
    #-------------------------------------------------------------------
    def set_pc(self, v):
        self.log("     set pc = "+tohex(v, 4))
        self.pc = v
        self.set_reg('pc', v)
        
    #-------------------------------------------------------------------
    def call_interrupt(self, i):
        #0 EXT0 0x0003
        #1 T0   0x000B
        #2 EXT1 0x0013
        #3 T1   0x001B
        #4 INTS 0x0023
        vectors = [0x3, 0x0B, 0x13, 0x1B, 0x23]
        self.cur_int = i
        addr = vectors[i]
        #print 'int', addr
        self.call(addr)
                
    #-------------------------------------------------------------------
    def jump(self, addr):
        self.set_pc(addr)
        
    #-------------------------------------------------------------------
    def jump_rel(self, v):
        offset = val8(v)
        if self.debug:
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
        
    #-------------------------------------------------------------------
    def reti(self):
        """ return function from interrupt """
        addr = self.pop()
        self.set_pc(addr)
        self.stack_depth -= 1
        
        # if IE all still enabled, re-enable interrupt
        if self.mem[self.IE] & BIT7:
            self.int_enabled = True
        else:
            self.int_enabled = False
            
        # if timer0 interrupt, clear TCON bit5 TF0
        if self.cur_int == self.INT_T0:
            self.mem[self.TCON] &= ~BIT5
        elif self.cur_int == self.INT_EXT0:
            self.mem[self.TCON] &= ~BIT1
        elif self.cur_int == self.INT_EXT1:
            self.mem[self.TCON] &= ~BIT3
            
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
    def array_list(self, table, n):
        lst = []
        for i in range(n):
            lst.append(0)
        for t in table:
            lst[t[0]] = t[1]
        return lst    
    
    #-------------------------------------------------------------------
    def get_op_str(self, optype, dd):
        op = ""
        
        optype_str = self.op_str[optype]
        
        if optype == OP_IRAM:
            v = int('0x'+dd, 16)
            for key, val in self.sfr_map.items():
                if val == v:
                    return key
            #op = self.sfr.get_str(v)
            #if op:
                #return op
            
        if dd != "" and type(dd) == "number" :
            dd = tohex(dd, 2)
    
        if (optype_str == "#op") :
            op = "#"+dd
        elif (optype_str == "op") :
            
            op = dd
        else:        
            op = optype_str

        return op
    
    #-------------------------------------------------------------------
    def get_inst_code(self, dd):
        inst_code = dd
        if (type(dd) is str) :
            inst_code = int("0x"+dd, 16)
        return inst_code
    
    #-------------------------------------------------------------------
    def get_inst_blen(self, dd):
        inst_code = self.get_inst_code(dd)
            
        sym = self.symbol_table[inst_code]
        #--print(i, dd, r.data[i])
        #--print(dd, string.format("%02X", r.data[i]))
        
        blen = sym[1]
        return blen
    
    #-------------------------------------------------------------------
    def parse_dddd(self, dd):

        inst_code = self.get_inst_code(dd[0])

        sym = self.symbol_table[inst_code]
        #--print(i, dd, r.data[i])
        #--print(dd, string.format("%02X", r.data[i]))
        
        blen = sym[1]
        inst = self.symbol_str[sym[2]]
        op_types = sym[3]
        op_n = len(op_types)

        op = ["", "", ""]
        
         #--print(dd, tohex(op_types[1]), tohex(op_types[2]), op_str[op_types[1]], op_str[op_types[2]])
        dd_i = 1
        for op_i in range(op_n):
            if op_types[op_i] > OP_ADDR:
                op[op_i] = self.get_op_str(op_types[op_i], "")
            else:
                op[op_i] = self.get_op_str(op_types[op_i], dd[dd_i])
                dd_i += 1
        op1 = op[0]
        op2 = op[1]
        op3 = op[2]
    
        if op_n > 0:
            if op_types[0] == OP_CODE and op_types[1] == OP_ADDR :
                op1 = self.get_op_str(op_types[0], dd[1])+op2
                op2 = ""
            if inst_code == 0x90:
                op1 = op1+op2
                op2 = ""
            
        #--print(tohex(sim.pc, 4), tohex(inst_code, 2), inst, op1+op2+op3) # , sym[5]
        inst_str = inst+"  "+str(op1)+","+str(op2)+","+str(op3)
        inst_lst = Inst(inst_code, op1, op2, op3)
        if blen == 1:
            dd1 = dd2 = dd3 = "  "
            dd0 = dd[0]
        elif blen == 2:
            dd0 = dd[0]
            dd1 = dd[1]
            dd2 = dd3 = "  "
        elif blen == 3:
            dd0 = dd[0]
            dd1 = dd[1]
            dd2 = dd[2]
            dd3 = "  "
        inst_lst.dd0 = dd0
        inst_lst.dd1 = dd1
        inst_lst.dd2 = dd2
        inst_lst.dd3 = dd3
        inst_lst.inst_str = inst
        inst_lst.op_n = op_n
        return blen, inst_str, inst_lst    
    
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
        if not self.int_enabled:
            return
        if self.int_flag == 0:
            return
        
        #do the interrupt work
        ip = self.mem[self.IP]
        flag = self.int_flag
        if ip != 0:
            # process high ip at first
            for i in range(0, 6):
                bit = 1 << i
                if flag & bit and ip & bit:
                    self.int_enabled = False
                    self.int_flag &= ~bit
                    self.call_interrupt(i)
                    return
            
        for i in range(0, 6):
            bit = 1 << i
            if flag & bit:
                self.int_enabled = False
                self.int_flag &= ~bit
                self.call_interrupt(i)
                return
        
    #-------------------------------------------------------------------
    def proc_timer(self):
        # do the timer work
        tcon = self.mem[self.TCON]
        # IE   bits  -  7:EA   6: -   5:ET2  4:ES   3:ET1  2:EX1  1:ET0  0:EX0
        # TCON bits  -  7:TR1  6:TR1  5:TF0  4:TR0  3:IE1  2:IT1  1:IE0  0:IT0
        # TR0 = tcon & BIT4
        # TR1 = tcon & BIT6
        # set TF0 tcon |= BIT5
        if tcon & BIT4 and self.t0_enabled and self.t0_count > 0:
            self.t0_count -= 1
            if self.t0_count <= 0:
                # set bit TF0 = 1
                self.mem[self.TCON] |= BIT5
                
                # trigger timer0 interrupt ET0 - BIT1
                if self.ie & BIT1:
                    self.int_flag |= BIT1
                
                # if mode = 2, reset initial count
                if self.t0_mode == 2:
                    # copy value from TH0 to TL0
                    self.t0_count = self.mem[self.TL0] = self.mem[self.TH0]
                
        if tcon & BIT6 and self.t1_enabled :
            self.t1_count -= 1
            if self.t1_count == 0:
                # set bit TF1 = 1
                self.mem[self.TCON] |= BIT7
                # trigger timer1 interrupt
                if self.ie & BIT3:
                    self.int_flag |= BIT3
                    

    #-------------------------------------------------------------------
    def load_and_debug_inst(self):
        self.proc_timer()
        self.proc_int()
        # get current program counter 
        addr = self.pc   
        self.inst_addr = self.pc
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
        self.log('------------', self.c_file, self.c_line)
        inst_code = self.code_space[addr]
        dd1 = self.code_space[addr + 1]
        dd2 = self.code_space[addr + 2]
        dd3 = self.code_space[addr + 3]
        #self.log(inst_code, dd1, dd2, dd3)
        
        sym = self.symbol_table[inst_code]
        op_n = sym[1]
        inst_map_code = sym[2]
        inst = self.symbol_str[inst_map_code]
        op_types = sym[3]
        s = tohex(inst_code, 2)+"    "+inst
        
        #if op_n > 0:
            #if op_types[0] == OP_CODE and op_types[1] == OP_ADDR :
                #op1 = self.get_op_str(op_types[0], dd1)+op2
                #op2 = ""            
                
        if (op_n == 1) :
            self.log("\n     -- ", op_n, s  ) 
        elif (op_n == 2) :
            self.log("\n     -- ", op_n, s, tohex(dd1, 2)) 
        elif (op_n == 3) :
            self.log("\n     -- ", op_n, s, tohex(dd1, 2), tohex(dd2, 2)) 
        elif (op_n == 4) :
            self.log("\n     -- ", op_n, s, tohex(dd1, 2), tohex(dd2, 2), tohex(dd3, 2)) 

            
        # move the program counter to the next instruction
        # self.set_pc(self.pc + blen)
        self.pc = self.pc + op_n
    
        f = self.inst_handler[inst_map_code]
        f(op_n, inst_code, dd1, dd2, dd3)
        
            
    #-------------------------------------------------------------------
    def load_inst(self):
        self.proc_timer()
        self.proc_int()
        
        # get current program counter 
        addr = self.pc   
        self.inst_addr = self.pc
        inst_code = self.code_space[addr]
        dd1 = self.code_space[addr + 1]
        dd2 = self.code_space[addr + 2]
        dd3 = self.code_space[addr + 3]
        sym = self.symbol_table[inst_code]
        op_n = sym[1]
        inst_map_code = sym[2]
            
        # move the program counter to the next instruction
        # self.set_pc(self.pc + blen)
        self.pc = self.pc + op_n
    
        f = self.inst_handler[inst_map_code]
        f(op_n, inst_code, dd1, dd2, dd3)
        
            
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
        
        if self.debug:
            while self.c_line == 0:
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
    
    #-------------------------------------------------------------------
    def pre_process_ihx_text(self, text):
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
    def get_record_table(self, text, printout):
        lst = self.pre_process_ihx_text(text)
        
        records = []
        line_index = 1
        
        prev_half_inst = []
        # for each line
        for item in lst:
            r = Obj()
    
            r.ll = item.bytes
            r.aaaa = item.addr
            r.tt = item.type
            r.insts = []
    
            #--print(index, r.ll, r.aaaa, r.tt, line) 
            if (printout) :
                print(aaaa, "; "+line)

            # dd start from position 10th
            i1 = 9
            
            # get all instruction data 
            i = 0
            j = 1

            while (i < r.ll) : 
                blen = self.get_inst_blen(item.dd[i])
                dd_lst = []
                for j in range(blen):
                    dd_lst.append(item.dd[i+j])
                    
                blen, dddd, inst = self.parse_dddd(dd_lst)
                
                if (printout) :
                    print("      "+dddd)
                
                r.insts.append(inst)

                line_index = line_index + 1
                i = i + blen
                i1 = i1 + 2*blen
    
            # add to records table
            records.append(r)
            
        return records
    
    #-------------------------------------------------------------------
    def get_records_string(self):
        count = len(self.records)
        s = ""
        map_list = rst.map_scan(self.file_path)

        lst = []
        for r in self.records:
            lst.append('%04X' % (r.aaaa))
        #print lst
        
        i = 0
        for r in self.records:
            addr = r.aaaa
            label = map_list.get_symbol(addr)
            if not label:
                s += '\nL' + str(i) + ': \n'
                i += 1
            
            #s += "     %04X-%04X %2d\n" % (r.aaaa, r.aaaa + r.ll - 1, len(r.insts))
            for dd in r.insts :
                label = map_list.get_symbol(addr)
                if label:         
                    s += '\n' + label + ': \n'
                    
                sym = self.symbol_table[dd.inst]
                inst = dd.inst_str #self.symbol_str[sym[2]]
                dd_str = "%2s %2s %2s %2s " % (dd.dd0, dd.dd1, dd.dd2, dd.dd3)
                if inst == 'lcall' or inst == 'ljmp ':
                    #idx = -1
                    #if dd.op1 in lst:
                        #idx = lst.index(dd.op1) 
                    label = map_list.get_symbol(int('0x' + dd.op1, 16))
                    if label:
                        s += "   %06X   %s  %s %s, (%s)\n" % (addr, dd_str, label, dd.inst_str, dd.op1)
                    else:
                        s += "   %06X   %s  %s, %s\n" % (addr, dd_str, dd.inst_str, dd.op1)
                elif inst == 'jb   ' or inst == 'jnb  ' :
                    offset = int('0x' + dd.op2, 16)
                    s += "   %06X   %s  %s, %s, %s  =%x\n" % (addr, dd_str, dd.inst_str, dd.op1, dd.op2, addr + sym[1] + offset)
                else:
                    
                    if dd.op_n == 3:
                        s += "   %06X   %s  %s %s, %s, %s\n" % (addr, dd_str, dd.inst_str, dd.op1, dd.op2, dd.op3)
                    elif dd.op_n == 2:
                        s += "   %06X   %s  %s %s, %s\n" % (addr, dd_str, dd.inst_str, dd.op1, dd.op2)
                    elif dd.op_n == 1:
                        s += "   %06X   %s  %s %s\n" % (addr, dd_str, dd.inst_str, dd.op1)
                    else:
                        s += "   %06X   %s  %s\n" % (addr, dd_str, dd.inst_str)
                addr += sym[1]

                    
        return s
    
#-------------------------------------------------------------------
def get_inst_blen(dd):
    inst_code = dd
    if (type(dd) is str) :
        inst_code = int("0x"+dd, 16)
        
    sym = self.symbol_table[inst_code]
    #--print(i, dd, r.data[i])
    #--print(dd, string.format("%02X", r.data[i]))
    
    blen = sym[1]
    return blen

#-------------------------------------------------------------------
def ihx_scan(frame, fn):
    #sim = Sim(frame)
    
    text = read_whole_file(fn)
    
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
        
    for r in lst:
        print tohex(r.addr,4), tohex(r.bytes,2), tohex(r.type,2), ':',
        for d in r.dd:
            print d,
        print ""
        
    #records = sim.get_record_table(text, True)


#---- for testing -------------------------------------------------------------
if __name__ == '__main__':    
    # temp_convert()
    # print_symbol_table()
    fn = "/home/athena/src/8051/t0/t0.ihx"
    ihx_scan(None, fn)
    #sim_run(fn)


