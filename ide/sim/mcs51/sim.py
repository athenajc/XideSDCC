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
        self.step_over_mode = False
        self.stack_depth = 0
        
        symbol_table.sort()
        self.symbol_table = symbol_table
        self.symbol_str = symbol_str #array_list(symbol_str, 256)
        self.op_str = op_str #array_list(op_str, 512)
        
        self.addr_map_lst = rst.rst_scan(source_list)
        self.c_line = 0
        self.asm_code = ""
        
        self.err = False
        #self.sfr = SfrDefine()
        self.a = 0
        self.b = 0
        self.dptr = 0
        self.pc = 0
        self.sp = 0
        self.mem = []
        self.stack = []
        self.r0 = 0
        self.r1 = 0
        self.r2 = 0
        self.r3 = 0
        self.r4 = 0
        self.r5 = 0
        self.r6 = 0
        self.r7 = 0
        self.c = 0
        self.ac = 0
        self.ov = 0
        
        #self.SP = 0x81
        #self.DPL  = 0x82
        #self.DPH  = 0x83
        #self.PCON = 0x87
        #self.TCON = 0x88
        #self.TMOD = 0x89
        #self.TL0 =  0x8A
        #self.TL1 = 0x8B
        #self.TH0 = 0x8C
        #self.TH1 =  0x8D
        #self.SCON = 0x98
        #self.SBUF = 0x99
        
        #self.RI  = 0x98
        #self.TI  = 0x99
        #self.RB8 = 0x9A
        #self.TB8 = 0x9B
        #self.REN = 0x9C
        #self.SM2 = 0x9D
        #self.SM1 = 0x9E
        #self.SM0 = 0x9F
        
        self.sbuf_list = []
        self.mem = [0] * 4096
        self.ext_mem = [0] * 64 * 1024
        self.code_space = [0] * 64 * 1024
        
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
            }
        self.SBUF = self.sfr_map['sbuf']
        self.RI  = self.sfr_map['ri']
        self.TI  = self.sfr_map['ti']
        
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
        if self.c_line == 0:
            return
        msg = " "
        for t in args:
            msg = msg + str(t) + " "
        s = get_hh_mm_ss() + msg + "\n"
        #print s
        self.frame.log(s)
        
    #-------------------------------------------------------------------
    def get_uart_put_ch(self):
        sbuf = self.get_sfr('sbuf')
        if sbuf != 0:    
            self.set_sfr('sbuf', 0)
            self.mem_set_bit(self.TI, 1)
            
        return sbuf
    
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
        return v
    
    #-------------------------------------------------------------------
    def set_a(self, v):
        self.log1("     set a = "+hex(v))
        self.a = (v)
        self.set_reg('a', v)
        
    #-------------------------------------------------------------------
    def set_b(self, v):
        self.log1("     set b = "+hex(v))
        self.b = (v)
        self.set_sfr('b', v)
        
    #-------------------------------------------------------------------
    def set_c(self, v):
        self.log1("     set c = "+hex(v))
        if (v == 0) :
            self.c = 0
        else:
            self.c = 1
        self.set_reg('c', v)
        
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
        k = 'r' + str(i)
        self.log1("     set "+k+" = "+hex(v))
        self.set_reg(k, v)
        
        if (i == 0) : self.r0 = v
        elif (i == 1) : self.r1 = v
        elif (i == 2) : self.r2 = v
        elif (i == 3) : self.r3 = v
        elif (i == 4) : self.r4 = v
        elif (i == 5) : self.r5 = v
        elif (i == 6) : self.r6 = v
        elif (i == 7) : self.r7 = v
        return v
    
    #-------------------------------------------------------------------
    def get_r(self, i):
        if (i == 0) : v = self.r0
        elif (i == 1) : v = self.r1
        elif (i == 2) : v = self.r2
        elif (i == 3) : v = self.r3
        elif (i == 4) : v = self.r4
        elif (i == 5) : v = self.r5
        elif (i == 6) : v = self.r6
        elif (i == 7) : v = self.r7
        self.log1("     get r"+str(i)+" = "+hex(v))
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
    def jump(self, addr):
        self.set_pc(addr)
        
    #-------------------------------------------------------------------
    def jump_rel(self, v):
        offset = byte_to_int(v)
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
    def load_inst(self):
        # get current program counter 
        addr = self.pc   
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
        #end
        
        #self.parse_dddd(inst_code, dd1, dd2, dd3)
    
        # move the program counter to the next instruction
        # self.set_pc(self.pc + blen)
        self.pc = self.pc + op_n
    
        f = self.inst_handler[inst_map_code]
        f(op_n, inst_code, dd1, dd2, dd3)
        
        ch = self.get_uart_put_ch()
        if ch != 0:
            self.sbuf_list.append(ch)
            
    #-------------------------------------------------------------------
    def start(self):
        self.stopped = False
        self.running = True
        set_sim(self)

        self.mode = 'run'
        self.pc = 0x0
        self.cmd_queue = Queue.Queue()
        
        while self.c_line == 0:
            self.load_inst()
            
    #-------------------------------------------------------------------
    def step(self):
        if self.stopped:
            return False
        
        self.log(tohex(self.pc, 4), self.asm_code)
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
        
        while self.c_line == n and self.c_file == f:
            self.log(tohex(self.pc, 4), self.asm_code)
            self.load_inst()
            
            if self.err:
                self.log('#simulation Error')
                return False
            if self.pc == 0 or self.stopped:
                self.log('#end of simulation')
                return False
            
        self.log('-------------- ' + str(self.c_file) + ', line = ' + str(self.c_line) + ' -----------\n')
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
            while self.stack_depth > s0:
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
        #self.thread.stop()
        #self.thread.join()

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
                        s += "   %04X   %s  %s %s, (%s)\n" % (addr, dd_str, label, dd.inst_str, dd.op1)
                    else:
                        s += "   %04X   %s  %s, %s\n" % (addr, dd_str, dd.inst_str, dd.op1)
                elif inst == 'jb   ' or inst == 'jnb  ' :
                    offset = int('0x' + dd.op2, 16)
                    s += "   %04X   %s  %s, %s, %s  =%x\n" % (addr, dd_str, dd.inst_str, dd.op1, dd.op2, addr + sym[1] + offset)
                else:
                    
                    if dd.op_n == 3:
                        s += "   %04X   %s  %s %s, %s, %s\n" % (addr, dd_str, dd.inst_str, dd.op1, dd.op2, dd.op3)
                    elif dd.op_n == 2:
                        s += "   %04X   %s  %s %s, %s\n" % (addr, dd_str, dd.inst_str, dd.op1, dd.op2)
                    elif dd.op_n == 1:
                        s += "   %04X   %s  %s %s\n" % (addr, dd_str, dd.inst_str, dd.op1)
                    else:
                        s += "   %04X   %s  %s\n" % (addr, dd_str, dd.inst_str)
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


