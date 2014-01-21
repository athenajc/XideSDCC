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
        self.mhz = 2 * 1024 * 1024
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
            #if t != 0:
                #print(t)
        self.pc = 0
        self.c_line = 0
        self.asm_code = ""
        
        self.fsr = 0
        self.indf_addr = 0
        self.indf_bank = 0
        
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
        self.stopped = True
        
        # initial timer and interrupts
        self.int_enabled = False
        self.int_p_enabled = False
        self.tmr0_mode  = 1 # T0CS = 1:counter, 0:timer
        self.tmr0_enabled = False
        self.tmr1_enabled = False
        self.tmr2_enabled = False
        self.tmr0_value = 0
        self.tmr1_value = 0
        self.tmr2_value = 0
        self.tmr0_rate = 0
        self.wdt_rate = 0
        self.ticks = 0
        
        # initial usart
        self.usart_enabled = False
        self.baud_rate = 9600
        self.sbuf = []
        self.usart_rxbuf = []
        
        # for set freg value, table look at value setting handler
        self.init_freg_handler()
        
        
        self.pin_logs = {}
        self.pins = ['RA0','RA1','RA2','RA3','RA4','RA5','RA6','RA7',
                        'RB0','RB1','RB2','RB3','RB4','RB5','RB6','RB7',
                        'RC0','RC1','RC2','RC3','RC4','RC5','RC6','RC7',]
        self.pin_out = []
        p = self.pin_logs
        
        for s in self.pins:
            p[s] = [[0,0,0]]
            self.pin_out.append(s)
            
        self.time_stamp = 0
        
    #---------------------------------------------------------------
    def get_pin_log(self, pin):
        log = self.pin_logs.get(pin, [])
        return log
    
    ##---------------------------------------------------------------
    #def set_pin_log(self):
        #p = self.pin_logs
        #for name, lst in self.pin_logs.items():
            #addr = self.sfr_addr[name]
            #lst.append(random.randint(0,256))
            
    #-------------------------------------------------------------------
    def log(self, *args):
        #if self.c_line == 0:
        #    return
        #import inspect
        #s1 = inspect.stack()[1][3] + " "
        if not self.debug or self.step_mode:
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
        return pic_hex_scan(self.frame, self.hex_file, self.mcu_name, self.dev_name)
    
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
        
    ##-------------------------------------------------------------------
    #def get_mem(self, addr):
        #v = self.mem[addr]
        #if self.debug:
            #key = self.sfr_name[addr]
            #self.log("     get mem %s %02x is %02x" % (key, addr, v))
        #return v    
        
    ##-------------------------------------------------------------------
    #def set_mem(self, addr, v):
        
        #if self.debug:
            #key = self.sfr_name[addr]
            #self.log("     set mem %s %02x = %02x" % (key, addr, v))
            
        #if (v > 0xff) :
            #self.log(v, "> 0xff")
            ##v = bits_and(v, 0xff)
            #v = v & 0xff
        
        #if not addr in self.mem_access_list:
            #self.mem_access_list.append(addr)
            
        #self.mem[addr] = v

        #if addr == self.PCL:
            #self.update_pc_from_PCL()
        #elif addr == self.TMR0:
            #self.tmr0_value = v
        #return v
    
    ##-------------------------------------------------------------------
    #def mem_get_bit(self, addr, bit):       
        #v = self.get_mem(addr)

        #if v & (1 << bit):
            #if self.debug: 
                #self.log("     get bit %d of %02x is 1" % (bit, addr))
            #return 1
        #else:
            #if self.debug: 
                #self.log("     get bit %d of %02x is 0" % (bit, addr))
            #return 0
                
    ##-------------------------------------------------------------------
    #def mem_set_bit(self, addr, bit, b):
        #v = self.get_mem(addr)
        
        #if b == 1:
            #v |= 1 << bit
        #else:
            #v &= ~(1 << bit)
            
        #self.set_mem(addr, v)
               
    #-------------------------------------------------------------------
    def set_reg(self, k, v):
        """ for watch panel usage """
        addr = self.sfr_addr.get(k, -1)
        if addr == -1:
            self.log("Error set_reg", k)
            return
        self.mem[addr] = v
        
    #-------------------------------------------------------------------
    def get_reg(self, k):
        """ for watch panel usage """
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
    def set_freg_status(self, v, bit = None, b = None):
        self.status_reg = v
        
        if bit == 5 or bit == 6:
            bank = (v >> 5) & 0x3
            self.bank_addr = bank * 0x80
            if bit == 6:
                if self.debug:
                    self.log("     select bank %d, %02x" % (bank, self.bank_addr))
                    
        elif bit == 7:
            self.indf_bank = b
            
    #-------------------------------------------------------------------
    def set_freg_tmr0(self, v, bit = None, b = None):
        self.tmr0_value = v
    
    #-------------------------------------------------------------------
    def set_freg_pcl(self, v, bit = None, b = None):
        pch = self.freg[self.PCLATH]
        pcl = self.freg[self.PCL]
        pc = (pch << 8) | pcl
        self.set_pc(pc)
        
    #-------------------------------------------------------------------
    def set_freg_intcon(self, v, bit = None, b = None):
        # 7: GIE, 6:PEIE, 5:T0IE, 4:INTE, 3:RBIE, 2:T0IF, 1:INTF, 0:RBIF
        if bit == None:
            if v & BIT7 and self.int_enabled == False:
                self.int_enabled = True
                
        elif bit == 7:
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
    def set_baud_rate(self, x, brgh):
        # check TXSTA bit5 BRGH - High Baud Rate Select Bit
        if brgh: 
            m = 16
        else:
            m = 64
        self.baud_rate = self.mhz / (m * (x +1))
        
    #-------------------------------------------------------------------
    def set_freg_spbrg(self, v, bit = None, b = None):
        """ set usart baud rate """
        #This is the register which holds the baud rate generator value. It can be calculated using the below formula :
        #Baud Rate Calculation :
        #Desired Baud Rate = Fosc/(64(X+1)) where X is the SPBRG value.
        #If we choose BRGH (High baud rate bit in the TXSTA register) bit as high, the formula will be :
        #Desired Baud Rate = Fosc/(16(X+1))
        #Let's calculate the SPBRG value for Fosc=4MHz, Baud Rate=9600, BRGH=1 :
        #9600 = 4000000/(16(X+1))
        #SPBRG=X=((4000000/9600)-16)/16=25,04167~25
        #The error will be :
        #Baud Rate = 4000000/(16(25,04167+1))=9615
        #Error = (9615-9600)/9600=0,16%        
        
        # set baud rate
        self.set_baud_rate(v, self.freg[self.TXSTA] & BIT5)        
    
    #-------------------------------------------------------------------
    def set_freg_txsta(self, v, bit = None, b = None):
        """ for usart transmit """
        #0 CSRC - Clock Source Select Bit : Only works in synchronous mode.
        #         Selects Master(1)(Clock generated internally)/Slave(0)(Clock from external source)mode.
        #1 TX9 -  9-bit Transmit Enable Bit :
        #         This bit enables(1)/disables(0) the 9-bit transmission
        #2 TXEN - Transmit Enable Bit :
        #         Transmit Enable(1)/Disable(0) bit
        #3 SYNC - USART Mode :
        #         Synchronous(1)/Asynchronous(0)
        #5 BRGH - High Baud Rate Select Bit :
        #         Only works in Asynchronous mode. High(1)/Low(0) speed
        #6 TRMT - Transmit Status Bit :
        #         TSR empty(1)/full(0)
        #7 TX9D - 9th bit of transmit data. Can be Parity bit.
        
        if v & BIT2: 
            # set TXEN = 1
            # check if SPEN == 1
            if self.freg[self.RCSTA] & BIT0:
                self.usart_enabled |= 1
                
        if bit == 5:
            self.set_baud_rate(self.freg[self.SPBRG], b)
    
    #-------------------------------------------------------------------
    def set_freg_rcsta(self, v, bit = None, b = None):
        """ for usart receive """
        #0 SPEN - Serial Port Enable Bit :
        #         Enables(1)/Disables(0) serial port
        #1 RX9  - 9-bit Receive Enable Bit :
        #         Enables(1)/Disables(0) 9-bit reception
        #2 SREN - Single Receive Enable Bit :
        #         Only works in Synchronous Master Mode. Enables(1)/Disables(0)
        #3 CREN - Continous Receive Enable Bit :
        #         Enables(1)/Disables(0) continous receive
        #4 ADEN - Address Detect Enable Bit :
        #         Only wokrs in 9-bit Asynchronous mode. Enables(1)/Disables(0) address detection
        #5 FERR - Framing Error Bit :
        #         Set(1) when framing error occured
        #6 OERR - Overrun Error Bit :
        #         Set(1) when overrun error occured
        #7 RX9D - 9th bit of received data. Can be parity bit.
        if v & BIT2: 
            # set SREN = 1
            # check if SPEN == 1
            if self.freg[self.RCSTA] & BIT0:
                self.usart_enabled |= 2
                
    #-------------------------------------------------------------------
    def set_freg_txreg(self, v, bit = None, b = None):
        """ usart tx """
        #self.usart_txbuf.append(v)
        self.sbuf_list.append(v)
        
        # set TXIF
        self.freg[self.PIR1] |= BIT4
        
    #-------------------------------------------------------------------
    def set_freg_rcreg(self, v, bit = None, b = None):
        """ usart rx """
        self.usart_rxbuf.append(v)
        
    #-------------------------------------------------------------------
    def set_freg_fsr(self, v, bit = None, b = None):
        """ set fsr for indirect memory access """
        self.fsr = v
        if self.indf_bank:
            self.indf_addr = 0x100 + v
        else:
            self.indf_addr = v
            
    #-------------------------------------------------------------------
    def set_freg_port(self, v, bit = None, b = None, name=None):
        stamp = self.time_stamp
        if bit:
            lst = self.pin_logs[name + str(bit)]
            t0 = lst[0][0]
                
            lst.insert(0, [stamp, t0, b])
        else:
            for i in range(8):
                lst = self.pin_logs[name + str(i)]
                t0 = lst[0][0]
                lst.insert(0, [stamp, t0, (v >> i) & 1])
                
    #-------------------------------------------------------------------
    def set_freg_porta(self, v, bit = None, b = None):
        self.set_freg_port(v, bit, b, 'RA')
                
    #-------------------------------------------------------------------
    def set_freg_portb(self, v, bit = None, b = None):
        self.set_freg_port(v, bit, b, 'RB')
        
    #-------------------------------------------------------------------
    def set_freg_portc(self, v, bit = None, b = None):
        self.set_freg_port(v, bit, b, 'RC')
        
    #-------------------------------------------------------------------
    def init_freg_handler(self):
        self.freg_handler = {}
        fh = self.freg_handler
        fh[self.TMR0] = fh[0x101] = self.set_freg_tmr0
        fh[self.STATUS] = self.set_freg_status
        fh[self.INTCON] = self.set_freg_intcon
        fh[self.PCL] = self.set_freg_pcl
        fh[self.OPTION_REG] = fh[0x100 + self.OPTION_REG] = self.set_option_reg
        fh[self.FSR] = self.set_freg_fsr
        #fh[self.PORTA] = self.set_freg_porta
        fh[self.PORTB] = self.set_freg_portb
        #fh[self.PORTC] = self.set_freg_portc
        
        # usart module, not supported for all devices, so have to check exists at first
        self.usart_supported = False
        
        if hasattr(self, 'TXSTA'):
            self.usart_supported = True
            fh[self.TXSTA] = self.set_freg_txsta
            fh[self.RCSTA] = self.set_freg_rcsta
            fh[self.SPBRG] = self.set_freg_spbrg
            fh[self.TXREG] = self.set_freg_txreg
            fh[self.RCREG] = self.set_freg_rcreg

    #-------------------------------------------------------------------
    def set_freg(self, addr, v):
        # set bank addr
        if addr == 0:
            addr = self.indf_addr
        elif not addr in [2, 3, 4, 0xA, 0xB]:
            addr += self.bank_addr
        
        if self.debug:
            key = self.sfr_name[addr]
            self.log("     set freg %s %02x = %02x" % (key, addr, v))
        
        # store freg value
        self.freg[addr] = v
        
        if not addr in self.mem_access_list:
            self.mem_access_list.append(addr)
            
        # call freg handler by addr
        if addr in self.freg_handler:
            self.freg_handler[addr](v, None, None)
                       
    #-------------------------------------------------------------------
    def set_freg_bit(self, addr, bit, b):
        if addr == 0:
            addr = self.indf_addr
        elif not addr in [2, 3, 4, 0xA, 0xB]:
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
            
        if addr in self.freg_handler:
            self.freg_handler[addr](v, bit, b)

            
    #-------------------------------------------------------------------
    def get_freg(self, addr):
        if addr == 0:
            addr = self.indf_addr
        elif not addr in [2, 3, 4, 0xA, 0xB]:
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
                self.tmr0_mode = 0
            else:
                self.tmr0_enabled = False
                self.tmr0_mode  = 1
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
                    self.log("     select bank %d, %02x" % (bank, self.bank_addr))
                    
        elif bit == 7:
            self.indf_bank = v
            if v:
                self.indf_addr = 0x100 + self.fsr
            else:
                self.indf_addr = self.fsr
                    
    #-------------------------------------------------------------------
    def set_status_flags(self, z, dc=0, c=0):
        v = self.status_reg & 0xf8
        v |= c | (dc << 1) | (z << 2)
        self.freg[0x03] = self.status_reg = v
        
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
        k2 = k[0:2]
        if k == 'INT':
            if v == 1:
                self.freg[self.INTCON] |= BIT1
        elif k2 == 'RA':
            bit = int(k[2:3])
            if v:
                self.freg[self.PORTA] |= 1 << bit
                if bit == 4 and self.tmr0_mode == 1:
                    self.inc_tmr0()
            else:
                self.freg[self.PORTA] &= ~(1 << bit)
            
        elif k2 == 'RB':
            bit = int(k[2:3])
            if v:
                self.freg[self.PORTB] |= 1 << bit
            else:
                self.freg[self.PORTB] &= ~(1 << bit)
        elif k2 == 'RC':
            bit = int(k[2:3])
            if v:
                self.freg[self.PORTC] |= 1 << bit
            else:
                self.freg[self.PORTC] &= ~(1 << bit)
        elif k == 'uart':
            # set RI = 1
            self.set_freg_rcreg(v)
    
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
            if intcon & BIT4 and intcon & BIT1: # 4:INTE and 1:INTF
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
    def inc_tmr0(self):
        tmr0 = self.tmr0_value
        if tmr0 < 0xff:
            self.tmr0_value = tmr0 + 1
        elif tmr0 == 0xff:
            self.tmr0_value = self.freg[self.TMR0]
            # set T0IF : bit2 of INTCON 0xB
            self.freg[0xB] |= BIT2
        
    #-------------------------------------------------------------------
    def proc_tmr0(self):
        if self.tmr0_rate > 0:
            if self.ticks < self.tmr0_rate:
                return
        self.ticks = 0
        self.inc_tmr0()
        
    #-------------------------------------------------------------------
    def update_c_line(self):
        # get current program counter 
        addr = self.pc

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
            
    #-------------------------------------------------------------------
    def show_inst_log(self):
        # get current program counter 
        addr = self.inst_addr
        addr += addr
        lsb = self.code_space[addr]
        msb = self.code_space[addr + 1] & 0x3f
        
        #self.log('**************** ', hex(msb), hex(lsb))
       
        #self.log('**************** pc ', hex(self.pc))
        opcode = (msb << 8) + lsb
        s = get_pic14_inst_str(opcode, msb, lsb)
        self.log("--------- %04x %02x %02x <%s>" % (addr, msb, lsb, s))

        
    #-------------------------------------------------------------------
    def load_inst(self):
        self.time_stamp += 1
        self.ticks += 1
        if self.tmr0_enabled :
            self.proc_tmr0()
                            
        if self.int_enabled :
            self.proc_int()
            
        addr = self.inst_addr = self.pc
        addr += addr
        if addr >= 0x8000:
            self.err = True
            return
        lsb = self.code_space[addr]
        msb = self.code_space[addr + 1] & 0x3f
        
        self.pc += 1

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
        self.pc = 0
        self.cmd_queue = Queue.Queue()
        self.c_line = 0
        
        if self.debug:
            while self.c_line == 0:
                self.load_inst()
                self.update_c_line()
            
    #-------------------------------------------------------------------
    def step(self, count=1):
        if self.stopped:
            return False
        
        self.step_mode = None
        if self.debug:
            self.load_inst()
            self.update_c_line()
            self.show_inst_log()
        else:
            for i in range(count):
                self.load_inst()
                
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
            self.update_c_line()
            if i > 1000:
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
                
        
        
    
    
