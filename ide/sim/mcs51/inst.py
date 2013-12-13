import define
    
global sim

def set_sim(s):
    global sim
    sim = s

def bits8(v):
    return v & 0xff
    
def bit(b):
    return 1 << b  # 1-based indexing

# Typical call:  if hasbit(x, bit(3)) : ...
def hasbit(x, bit):
    if x & (1 << bit):
        return 1
    else:
        return 0

def testbit(x, bit):
    return hasbit(x, bit)

def getbit(x, bit):
    # print("getbit", x, p, bit(p))
    return x & (1 << bit)

def setbit(x, bit):
    return x | (1 << bit)

def clearbit(v1, bit):
    v2 = ~(1 << bit)
    return v1 & v2

def bits_test(v1, v2):
    if v1 & v2:
        return 1
    else:
        return 0

def bits_and(v1, v2):
    return v1 & v2

def bits_or(v1, v2):
    return v1 | v2

def bits_xor(v1, v2):
    return v1 ^ v2

def bits_not(v):
    return ~v & 0xffff

def bits_lshift(v, n):  # <<
    return v << n

def bits_rshift(v, n):  # >>
    return v >> n

def int_to_byte(v):   
    if (v < 0) :
        v = 0x100 + v;        
    return v

def tonumber(s, d):
    if s is None or s == "" :
        return 0    
    return int("0x" + s, d)

def tostring(v):
    return str(v)

def int_to_word(v):    
    if (v < 0) :
        v = 0x10000 + v;        
    return v

def byte_to_int(v):
    if (bits_test(v, 0x80)) :
        #print(v, bits_and(v, 0x7f), bits_and(v, 0x7f) - 128)
        v = (v & 0x7f) - 128
        #print(v)    
    return v

def word_to_int(v):
    if (v > 0x7fff) :
        v = (v & 0x7fff) - 0x10000;
    return v

#def get_real_op(optype, opvalue):
    #if (op_type == OP_A) : 
        #return sim.a 
    #elif (op_type == OP_B) : 
        #return sim.b
    #elif (op_type == OP_C) : 
        #return sim.c
    #elif (op_type == OP_DATA) : 
        #return opvalue
    #elif (op_type == OP_IRAM) : 
        #return sim.get_mem(opvalue)
    #elif (op_type == OP_DPTR) : 
        #return sim.dptr
    #elif (op_type == OP_BITADDR) : 
        #return opvalue
    #elif (op_type == OP_RELADDR) : 
        #return opvalue
    #elif (op_type == OP_R0) : 
        #return sim.get_r(0)
    #elif (op_type == OP_R1) : 
        #return sim.get_r(1)
    #elif (op_type == OP_R2) : 
        #return sim.get_r(2)
    #elif (op_type == OP_R3) : 
        #return sim.get_r(3)
    #elif (op_type == OP_R4) : 
        #return sim.get_r(4)
    #elif (op_type == OP_R5) : 
        #return sim.get_r(5)
    #elif (op_type == OP_R6) : 
        #return sim.get_r(6)
    #elif (op_type == OP_R7) : 
        #return sim.get_r(7)
    #elif (op_type == OP_ATR0) : 
        #return sim.get_mem_r(0)
    #elif (op_type == OP_ATR1) : 
        #return sim.get_mem_r(1)
    #elif (op_type == OP_ATA) : 
        #return sim.get_mem(sim.a)
    #elif (op_type == OP_ATDPTR) : 
        #return sim.get_ext_mem(sim.get_dptr())
    #elif (op_type == OP_PC) : 
        #return sim.pc

    #return opvalue


def get_arth_inst_op2(inst, op1):
    inst = inst & 0xF

    if (inst == 0x04) :
        v2 = op1
    elif (inst == 0x05) : 
        v2 = sim.get_mem(op1)
    elif (inst == 0x06) : 
        v2 = sim.get_mem_r(0)
    elif (inst == 0x07) : 
        v2 = sim.get_mem_r(1)
    elif (inst == 0x08) : 
        v2 = sim.get_r(0)
    elif (inst == 0x09) : 
        v2 = sim.get_r(1)
    elif (inst == 0x0A) : 
        v2 = sim.get_r(2)
    elif (inst == 0x0B) : 
        v2 = sim.get_r(3)
    elif (inst == 0x0C) : 
        v2 = sim.get_r(4)
    elif (inst == 0x0D) : 
        v2 = sim.get_r(5)
    elif (inst == 0x0E) : 
        v2 = sim.get_r(6)
    elif (inst == 0x0F) : 
        v2 = sim.get_r(7)

    return v2


def inst_acall(inst_bytes, inst, op1):
    #--[[
    #Operation:  ACALL
    #Function:  Absolute Call Within 2K Block
    #Syntax:  ACALL code address
    #Instructions  OpCode  Bytes  Flags
    #ACALL page0  0x11  2  None
    #ACALL page1  0x31  2  None
    #ACALL page2  0x51  2  None
    #ACALL page3  0x71  2  None
    #ACALL page4  0x91  2  None
    #ACALL page5  0xB1  2  None
    #ACALL page6  0xD1  2  None
    #ACALL page7  0xF1  2  None
    #]]--
    addr = ((inst - 0x11) * 0x40) + op1
    sim.call(addr)


def inst_add(inst_bytes, inst, op1, op2, op3):
    #--[[
    #ADD A,#data  0x24  2  1  C, AC, OV
    #ADD A,iram_addr  0x25  2  1  C, AC, OV
    #ADD A,@R0  0x26  1  1  C, AC, OV
    #ADD A,@R1  0x27  1  1  C, AC, OV
    #ADD A,R0  0x28  1  1  C, AC, OV
    #ADD A,R1  0x29  1  1  C, AC, OV
    #ADD A,R2  0x2A  1  1  C, AC, OV
    #ADD A,R3  0x2B  1  1  C, AC, OV
    #ADD A,R4  0x2C  1  1  C, AC, OV
    #ADD A,R5  0x2D  1  1  C, AC, OV
    #ADD A,R6  0x2E  1  1  C, AC, OV
    #ADD A,R7  0x2F  1  1  C, AC, OV
    #--]]
    
    v1 = sim.a & 0xff
    v2 = get_arth_inst_op2(inst, op1) & 0xff
    sim.set_a(v1 + v2)
    sim.check_overflow(sim.a, v1, v2)


def inst_addc(inst_bytes, inst, op1, op2, op3):
    #--[[
    #ADDC A,#data  0x34  2  C, AC, OV
    #ADDC A,iram addr  0x35  2  C, AC, OV
    #ADDC A,@R0  0x36  1  C, AC, OV
    #ADDC A,@R1  0x37  1  C, AC, OV
    #ADDC A,R0  0x38  1  C, AC, OV
    #ADDC A,R1  0x39  1  C, AC, OV
    #ADDC A,R2  0x3A  1  C, AC, OV
    #ADDC A,R3  0x3B  1  C, AC, OV
    #ADDC A,R4  0x3C  1  C, AC, OV
    #ADDC A,R5  0x3D  1  C, AC, OV
    #ADDC A,R6  0x3E  1  C, AC, OV
    #ADDC A,R7  0x3F  1  C, AC, OV
    #--]]
    
    v1 = bits8(sim.a)
    v2 = bits8(get_arth_inst_op2(inst, op1))

    sim.set_a(v1 + v2 + sim.c)
    sim.check_overflow(sim.a, v1, v2)


def inst_ajmp(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  AJMP
    #Function:  Absolute Jump Within 2K Block
    #Syntax:  AJMP code address
    #Instructions  OpCode  Bytes  Flags
    #AJMP page0  0x01  2  None
    #AJMP page1  0x21  2  None
    #AJMP page2  0x41  2  None
    #AJMP page3  0x61  2  None
    #AJMP page4  0x81  2  None
    #AJMP page5  0xA1  2  None
    #AJMP page6  0xC1  2  None
    #AJMP page7  0xE1  2  None
    #]]--
    addr = ((inst - 0x01) * 0x40) + op1
    sim.jump(addr)


def inst_anl(inst_bytes, inst, op1, op2, op3):
    # ANL does a bitwise "AND" operation between operand1 and operand2, 
    # leaving the resulting value in operand1.
    if     (inst == 0x52):
        sim.set_mem(op1, bits_and(sim.get_mem(op1), sim.a))  # ANL iram addr,A  0x52  2  None
    elif (inst == 0x53) : sim.set_mem(op1, bits_and(sim.get_mem(op1), op2))    # ANL iram addr,#data  0x53  3  None
    elif (inst == 0x54) : sim.set_a(bits_and(sim.a, op1))             # ANL A,#data  0x54  2  None
    elif (inst == 0x55) : sim.set_a(bits_and(sim.a, sim.get_mem(op1)))    # ANL A,iram addr  0x55  2  None
    elif (inst == 0x56) : sim.set_a(bits_and(sim.a, sim.get_mem_r(0))) # ANL A,@R0  0x56  1  None
    elif (inst == 0x57) : sim.set_a(bits_and(sim.a, sim.get_mem_r(1))) # ANL A,@R1  0x57  1  None
    elif (inst == 0x58) : sim.set_a(bits_and(sim.a, sim.get_r(0)))  # ANL A,R0  0x58  1  None
    elif (inst == 0x59) : sim.set_a(bits_and(sim.a, sim.get_r(1)))  # ANL A,R1  0x59  1  None
    elif (inst == 0x5A) : sim.set_a(bits_and(sim.a, sim.get_r(2)))  # ANL A,R2  0x5A  1  None
    elif (inst == 0x5B) : sim.set_a(bits_and(sim.a, sim.get_r(3)))  # ANL A,R3  0x5B  1  None
    elif (inst == 0x5C) : sim.set_a(bits_and(sim.a, sim.get_r(4)))  # ANL A,R4  0x5C  1  None
    elif (inst == 0x5D) : sim.set_a(bits_and(sim.a, sim.get_r(5)))  # ANL A,R5  0x5D  1  None
    elif (inst == 0x5E) : sim.set_a(bits_and(sim.a, sim.get_r(6)))  # ANL A,R6  0x5E  1  None
    elif (inst == 0x5F) : sim.set_a(bits_and(sim.a, sim.get_r(7)))  # ANL A,R7  0x5F  1  None
    elif (inst == 0x82) : sim.set_c(bits_and(sim.c, sim.mem_get_bit(op1)))  # ANL C,bit addr  0x82  2  C
    elif (inst == 0xB0) : sim.set_c(bits_and(sim.c, sim.mem_get_nbit(op1)))  # ANL C,/bit addr  0xB0  2  C
    

def inst_cjne(inst_bytes, inst, op1, op2, op3):
    # Operation:  CJNE
    # Function:  Compare and Jump If Not Equal
    # Syntax:  CJNE operand1,operand2,reladdr    

    if     (inst == 0xB4) : # CJNE A,#data,reladdr  0xB4  3  C
        v1 = sim.a
        v2 = op1
    elif (inst == 0xB5) :  # CJNE A,iram addr,reladdr  0xB5  3  C
        v1 = sim.a
        v2 = sim.get_mem(op1)
    elif (inst == 0xB6) :  # CJNE @R0,#data,reladdr  0xB6  3  C
        v1 = sim.get_mem_r(0)
        v2 = op1
    elif (inst == 0xB7) : # CJNE @R1,#data,reladdr  0xB7  3  C
        v1 = sim.get_mem_r(1)
        v2 = op1
    elif (inst == 0xB8) : # CJNE R0,#data,reladdr  0xB8  3  C
        v1 = sim.get_r(0) 
        v2 = op1
    elif (inst == 0xB9) : # CJNE R1,#data,reladdr  0xB9  3  C
        v1 = sim.get_r(1)
        v2 = op1
    elif (inst == 0xBA) : # CJNE R2,#data,reladdr  0xBA  3  C
        v1 = sim.get_r(2)
        v2 = op1
    elif (inst == 0xBB) : # CJNE R3,#data,reladdr  0xBB  3  C
        v1 = sim.get_r(3)
        v2 = op1
    elif (inst == 0xBC) : # CJNE R4,#data,reladdr  0xBC  3  C
        v1 = sim.get_r(4)
        v2 = op1
    elif (inst == 0xBD) : # CJNE R5,#data,reladdr  0xBD  3  C
        v1 = sim.get_r(5)
        v2 = op1
    elif (inst == 0xBE) : # CJNE R6,#data,reladdr  0xBE  3  C
        v1 = sim.get_r(6)
        v2 = op1
    elif (inst == 0xBF) : # CJNE R7,#data,reladdr  0xBF  3  C
        v1 = sim.get_r(7)
        v2 = op1

    
    # The Carry bit (C) is set if operand1 is less than operand2, otherwise it is cleared.
    if (v1 < v2) : 
        sim.set_c(1) 
    else :
        sim.set_c(0)
    
    # print("cjne", v1, v2, op1, op2)
    # compares the value of operand1 and operand2 and branches to the indicated relative address 
    # if operand1 and operand2 are not equal. 
    # If the two operands are equal program flow continues with the instruction following the CJNE instruction.
    if (v1 != v2) :
        sim.jump_rel(op2)


def inst_clr(inst_bytes, inst, op1, op2, op3):
    # [[
    #CLR bit addr  0xC2  2  None
    #CLR C  0xC3  1  C
    #CLR A  0xE4  1  None
    #]]
    if (inst == 0xC2) :
        sim.mem_set_bit(op1, 0)
    elif (inst == 0xC3) :
        sim.set_c(0)
    elif (inst == 0xE4) :
        sim.set_a(0)


def inst_cpl(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  CPL
    #Function:  Complement Register
    #Syntax:  CPL operand
    #Instructions  OpCode  Bytes  Flags
    #CPL A  0xF4  1  None
    #CPL C  0xB3  1  C
    #CPL bit addr  0xB2  2  None
    #]]
    if (inst == 0xF4) :
        sim.set_a(~sim.a & 0xff)
    elif (inst == 0xB3) :
        sim.set_c(~sim.c & 0xff)
    elif (inst == 0xB2) :
        sim.mem_set_bit(op1, sim.mem_get_nbit(op1))  # op1 is bit addr


def inst_da(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  DA
    #Function:  Decimal Adjust Accumulator
    #Syntax:  DA A
    #Instructions  OpCode  Bytes  Flags
    #DA  0xD4  1  C

    #IF (A3-0 > 9) OR (AC = 1)
      #A = A + 6
    #IF (A7-4 > 9) OR (C = 1)
      #A = A + 60h
    #]]
    
    a = sim.a
    a3_0 = a & 0xf
    a7_4 = (a >> 4) & 0xf
    
    if (a3_0 > 9 or sim.ac == 1) :
        sim.set_a(a + 6)

    if (a7_4 > 9 or sim.ac == 1) :
        sim.set_a(a + 0x60)

def dec(v):
    if v == 0 : 
        return 0xff
    else :
        return v - 1


def inst_dec(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  DEC
    #Function:  Decrement Register
    #Syntax:  DEC register
    #Instructions  OpCode  Bytes  Flags
    #DEC A  0x14  1  None
    #DEC iram addr  0x15  2  None
    #DEC @R0  0x16  1  None
    #DEC @R1  0x17  1  None
    #DEC R0  0x18  1  None
    #DEC R1  0x19  1  None
    #DEC R2  0x1A  1  None
    #DEC R3  0x1B  1  None
    #DEC R4  0x1C  1  None
    #DEC R5  0x1D  1  None
    #DEC R6  0x1E  1  None
    #DEC R7  0x1F  1  None
    #]]
    if (inst == 0x14) :     
        sim.set_a(dec(sim.a))
    elif (inst == 0x15) : 
        sim.set_mem(op1, dec(sim.get_mem(op1)))
    elif (inst == 0x16) : 
        sim.set_mem_r(0, dec(sim.get_mem_r(0)))
    elif (inst == 0x17) : 
        sim.set_mem_r(1, dec(sim.get_mem_r(1)))
    elif (inst == 0x18) : 
        sim.set_r(0, dec(sim.get_r(0)))
    elif (inst == 0x19) : 
        sim.set_r(1, dec(sim.get_r(1)))
    elif (inst == 0x1A) : 
        sim.set_r(2, dec(sim.get_r(2)))
    elif (inst == 0x1B) : 
        sim.set_r(3, dec(sim.get_r(3)))
    elif (inst == 0x1C) : 
        sim.set_r(4, dec(sim.get_r(4)))
    elif (inst == 0x1D) : 
        sim.set_r(5, dec(sim.get_r(5)))
    elif (inst == 0x1E) : 
        sim.set_r(6, dec(sim.get_r(6)))
    elif (inst == 0x1F) : 
        sim.set_r(7, dec(sim.get_r(7)))


def inst_div(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  DIV
    #Function:  Divide Accumulator by B
    #Syntax:  DIV AB
    #Instructions  OpCode  Bytes  Flags
    #DIV AB  0x84  1  C, OV
    #]]
    
    if (sim.b == 0) :
        sim.set_ov(1)
    else :       
        v2 = sim.a % sim.b
        v1 = (sim.a - v2) / sim.b
        
        sim.set_a(v1)
        sim.set_b(v2)

        sim.set_ov(0)


def inst_djnz(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  DJNZ
    #Function:  Decrement and Jump if Not Zero
    #Syntax:  DJNZ register,reladdr
    #Instructions  OpCode  Bytes  Flags
    #DJNZ iram addr,reladdr  0xD5  3  None
    #DJNZ R0,reladdr  0xD8  2  None
    #DJNZ R1,reladdr  0xD9  2  None
    #DJNZ R2,reladdr  0xDA  2  None
    #DJNZ R3,reladdr  0xDB  2  None
    #DJNZ R4,reladdr  0xDC  2  None
    #DJNZ R5,reladdr  0xDD  2  None
    #DJNZ R6,reladdr  0xDE  2  None
    #DJNZ R7,reladdr  0xDF  2  None

    #PC = PC + 2
    #(direct) = (direct) - 1
    #IF (direct) <> 0
      #PC = PC + offset

    #PC = PC + 2
    #Rn = Rn - 1
    #IF Rn <> 0
      #PC = PC + offset
    #]]
    
    if (inst == 0xD5) : v = sim.set_mem(op1, dec(sim.get_mem(op1)))
    elif (inst == 0xD8) : v = sim.set_r(0, dec(sim.get_r(0)))
    elif (inst == 0xD9) : v = sim.set_r(1, dec(sim.get_r(1)))
    elif (inst == 0xDA) : v = sim.set_r(2, dec(sim.get_r(2)))
    elif (inst == 0xDB) : v = sim.set_r(3, dec(sim.get_r(3)))
    elif (inst == 0xDC) : v = sim.set_r(4, dec(sim.get_r(4)))
    elif (inst == 0xDD) : v = sim.set_r(5, dec(sim.get_r(5)))
    elif (inst == 0xDE) : v = sim.set_r(6, dec(sim.get_r(6)))
    elif (inst == 0xDF) : v = sim.set_r(7, dec(sim.get_r(7)))
    #end
    #--print(v, op1, op2)
    if (v != 0) :
        if (inst == 0xD5) :
            sim.jump_rel(op2)
        else:
            sim.jump_rel(op1)


def inc(v):
    if (v == 0xff) : 
        return 0
    else :
        return v + 1


def inc16(v):
    if (v == 0xffff) : 
        return 0
    else :
        return v + 1


def inst_inc(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Instructions  OpCode  Bytes  Flags
    #INC A  0x04  1  None
    #INC iram addr  0x05  2  None
    #INC @R0  0x06  1  None
    #INC @R1  0x07  1  None
    #INC R0  0x08  1  None
    #INC R1  0x09  1  None
    #INC R2  0x0A  1  None
    #INC R3  0x0B  1  None
    #INC R4  0x0C  1  None
    #INC R5  0x0D  1  None
    #INC R6  0x0E  1  None
    #INC R7  0x0F  1  None
    #INC DPTR  0xA3  1  None
    #]]
    if (inst == 0x04) :   sim.set_a(inc(sim.a))
    elif (inst == 0x05) : sim.set_mem(op1, inc(sim.get_mem(op1)))
    elif (inst == 0x06) : sim.set_mem_r(0, inc(sim.get_mem_r(0)))
    elif (inst == 0x07) : sim.set_mem_r(1, inc(sim.get_mem_r(1)))
    elif (inst == 0x08) : sim.set_r(0, inc(sim.get_r(0)))
    elif (inst == 0x09) : sim.set_r(1, inc(sim.get_r(1)))
    elif (inst == 0x0A) : sim.set_r(2, inc(sim.get_r(2)))
    elif (inst == 0x0B) : sim.set_r(3, inc(sim.get_r(3)))
    elif (inst == 0x0C) : sim.set_r(4, inc(sim.get_r(4)))
    elif (inst == 0x0D) : sim.set_r(5, inc(sim.get_r(5)))
    elif (inst == 0x0E) : sim.set_r(6, inc(sim.get_r(6)))
    elif (inst == 0x0F) : sim.set_r(7, inc(sim.get_r(7)))
    elif (inst == 0xA3) : sim.set_dptr(inc16(sim.get_dptr()))


def inst_jb(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  JB
    #Function:  Jump if Bit Set
    #Syntax:  JB bit addr, reladdr
    #Instructions  OpCode  Bytes  Flags
    #JB bit addr,reladdr  0x20  3  None
    
    #PC = PC + 3
    #IF (bit) = 1
        #PC = PC + offset
    #]]    
    #--print("jb  - bit", op1, bit, sim.pc, op2, tohex(sim.pc + op2))
    if sim.mem_get_bit(op1) :
        sim.jump_rel(op2)


def inst_jbc(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  JBC
    #Function:  Jump if Bit Set and Clear Bit
    #Syntax:  JB bit addr, reladdr
    #Instructions  OpCode  Bytes  Flags
    #JBC bit addr,reladdr  0x10  3  None

    #PC = PC + 3
    #IF (bit) = 1
      #(bit) = 0
      #PC = PC + offset
    #]]
    #sim.log('mem_get bit '+ hex(op1))
    if (sim.mem_get_bit(op1)) :
        #sim.mem_set_bit(op1, 0)
        sim.jump_rel(op2)


def inst_jc(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  JC
    #Function:  Jump if Carry Set
    #Syntax:  JC reladdr
    #Instructions  OpCode  Bytes  Flags
    #JC reladdr  0x40  2  None

    #PC = PC + 2
    #IF C = 1
      #PC = PC + offset
    #]]
    if (sim.c) :        
        sim.jump_rel(op1)


def inst_jmp(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  JMP
    #Function:  Jump to Data Pointer + Accumulator
    #Syntax:  JMP @A+DPTR
    #Instructions  OpCode  Bytes  Flags
    #JMP @A+DPTR  0x73  1  None

    #PC = PC + DPTR
    #]]
    sim.jump(sim.a + sim.get_dptr())


def inst_jnb(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  JNB
    #Function:  Jump if Bit Not Set
    #Syntax:  JNB bit addr,reladdr
    #Instructions  OpCode  Bytes  Flags
    #JNB bit addr,reladdr  0x30  3  None
    #]]
    
    bit = sim.mem_get_bit(op1)
    if (bit == 0) :
        sim.jump_rel(op2)


def inst_jnc(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  JNC
    #Function:  Jump if Carry Not Set
    #Syntax:  JNC reladdr
    #Instructions  OpCode  Bytes  Flags
    #JNC reladdr  0x50  2  None
    #]]
    if (sim.c == 0) :        
        sim.jump_rel(op1)


def inst_jnz(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  JNZ
    #Function:  Jump if Accumulator Not Zero
    #Syntax:  JNZ reladdr
    #Instructions  OpCode  Bytes  Flags
    #JNZ reladdr  0x70  2  None
    #]]
    if (sim.a != 0) :        
        sim.jump_rel(op1)


def inst_jz(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  JZ
    #Function:  Jump if Accumulator Zero
    #Syntax:  JNZ reladdr
    #Instructions  OpCode  Bytes  Flags
    #JZ reladdr  0x60  2  None
    #]]
    if (sim.a == 0) :
        sim.jump_rel(op1)


def inst_lcall(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  LCALL
    #Function:  Long Call
    #Syntax:  LCALL code addr
    #Instructions  OpCode  Bytes  Flags
    #LCALL code addr  0x12  3  None
   
    #PC = PC + 3
    #SP = SP + 1
    #(SP) = PC[7-0]
    #SP = SP + 1
    #(SP) = PC[15-8]
    #PC = addr16
    #]]
    #print("inst_lcall", inst_bytes, hex((op1 * 256) + op2))
    sim.call((op1 * 256) + op2)


def inst_ljmp(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  LJMP
    #Function:  Long Jump
    #Syntax:  LJMP code addr
    #Instructions  OpCode  Bytes  Flags
    #LJMP code addr  0x02  3  None

    #PC = addr16
    #]]

    sim.jump((op1 * 256) + op2)


def inst_mov(inst_bytes, inst, op1, op2, op3):
    # Description: MOV copies the value of operand2 into operand1. 
    # The value of operand2 is not affected. 
    # Both operand1 and operand2 must be in Internal RAM. 
    # No flags are affected unless the instruction is moving the value of a bit into the carry bit 
    # in which case the carry bit is affected or unless the instruction is moving a value into the PSW register 
    # (which contains all the program flags).

    # ** Note: In the case of "MOV iram addr,iram addr", 
    # the operand inst_bytes of the instruction are stored in reverse order. 
    # That is, the instruction consisting of the inst_bytes 0x85, 0x20, 0x50 
    # means "Move the contents of Internal RAM location 0x20 to 
    # Internal RAM location 0x50" whereas the opposite would be generally presumed.

    # print("mov ", tohex(inst, 2), tohex(op1, 2), tohex(op2, 2))
    if   (inst == 0x76) : sim.set_mem_r(0, op1)       # MOV @R0,#data  0x76  2  None        
    elif (inst == 0x77) : sim.set_mem_r(1, op1)   # MOV @R1,#data  0x77  2  None
    elif (inst == 0xF6) : sim.set_mem_r(0, sim.a) # MOV @R0,A  0xF6  1  None
    elif (inst == 0xF7) : sim.set_mem_r(1, sim.a) # MOV @R1,A  0xF7  1  None
    elif (inst == 0xA6) : sim.set_mem_r(0, sim.get_mem(op1)) # MOV @R0,iram addr  0xA6  2  None       
    elif (inst == 0xA7) : sim.set_mem_r(1, sim.get_mem(op1)) # MOV @R1,iram addr  0xA7  2  None
    elif (inst == 0x74) : sim.set_a(op1) # MOV A,#data  0x74  2  None
    elif (inst == 0xE6) : sim.set_a(sim.get_mem_r(0)) # MOV A,@R0  0xE6  1  None
    elif (inst == 0xE7) : sim.set_a(sim.get_mem_r(1)) # MOV A,@R1  0xE7  1  None
    elif (inst == 0xE8) : sim.set_a(sim.get_r(0)) # MOV A,R0  0xE8  1  None
    elif (inst == 0xE9) : sim.set_a(sim.get_r(1)) # MOV A,R1  0xE9  1  None
    elif (inst == 0xEA) : sim.set_a(sim.get_r(2)) # MOV A,R2  0xEA  1  None
    elif (inst == 0xEB) : sim.set_a(sim.get_r(3)) # MOV A,R3  0xEB  1  None
    elif (inst == 0xEC) : sim.set_a(sim.get_r(4)) # MOV A,R4  0xEC  1  None
    elif (inst == 0xED) : sim.set_a(sim.get_r(5)) # MOV A,R5  0xED  1  None
    elif (inst == 0xEE) : sim.set_a(sim.get_r(6)) # MOV A,R6  0xEE  1  None
    elif (inst == 0xEF) : sim.set_a(sim.get_r(7)) # MOV A,R7  0xEF  1  None
    elif (inst == 0xE5) : sim.set_a(sim.get_mem(op1)) # MOV A,iram addr  0xE5  2  None

    elif (inst == 0x90) : sim.set_dptr((op1 * 256) + op2) # MOV DPTR,#data16  0x90  3  None
    elif (inst == 0x78) : sim.set_r(0, op1) # MOV R0,#data  0x78  2  None
    elif (inst == 0x79) : sim.set_r(1, op1) # MOV R1,#data  0x79  2  None
    elif (inst == 0x7A) : sim.set_r(2, op1) # MOV R2,#data  0x7A  2  None
    elif (inst == 0x7B) : sim.set_r(3, op1) # MOV R3,#data  0x7B  2  None
    elif (inst == 0x7C) : sim.set_r(4, op1) # MOV R4,#data  0x7C  2  None
    elif (inst == 0x7D) : sim.set_r(5, op1) # MOV R5,#data  0x7D  2  None
    elif (inst == 0x7E) : sim.set_r(6, op1) # MOV R6,#data  0x7E  2  None
    elif (inst == 0x7F) : sim.set_r(7, op1) # MOV R7,#data  0x7F  2  None
    elif (inst == 0xF8) : sim.set_r(0, sim.a) # MOV R0,A  0xF8  1  None
    elif (inst == 0xF9) : sim.set_r(1, sim.a) # MOV R1,A  0xF9  1  None
    elif (inst == 0xFA) : sim.set_r(2, sim.a) # MOV R2,A  0xFA  1  None
    elif (inst == 0xFB) : sim.set_r(3, sim.a) # MOV R3,A  0xFB  1  None
    elif (inst == 0xFC) : sim.set_r(4, sim.a) # MOV R4,A  0xFC  1  None
    elif (inst == 0xFD) : sim.set_r(5, sim.a) # MOV R5,A  0xFD  1  None
    elif (inst == 0xFE) : sim.set_r(6, sim.a) # MOV R6,A  0xFE  1  None
    elif (inst == 0xFF) : sim.set_r(7, sim.a) # MOV R7,A  0xFF  1  None
    elif (inst == 0xA8) : sim.set_r(0, sim.get_mem(op1)) # MOV R0,iram addr  0xA8  2  None
    elif (inst == 0xA9) : sim.set_r(1, sim.get_mem(op1)) # MOV R1,iram addr  0xA9  2  None
    elif (inst == 0xAA) : sim.set_r(2, sim.get_mem(op1)) # MOV R2,iram addr  0xAA  2  None
    elif (inst == 0xAB) : sim.set_r(3, sim.get_mem(op1)) # MOV R3,iram addr  0xAB  2  None
    elif (inst == 0xAC) : sim.set_r(4, sim.get_mem(op1)) # MOV R4,iram addr  0xAC  2  None
    elif (inst == 0xAD) : sim.set_r(5, sim.get_mem(op1)) # MOV R5,iram addr  0xAD  2  None
    elif (inst == 0xAE) : sim.set_r(6, sim.get_mem(op1)) # MOV R6,iram addr  0xAE  2  None
    elif (inst == 0xAF) : sim.set_r(7, sim.get_mem(op1)) # MOV R7,iram addr  0xAF  2  None
    
    elif (inst == 0x75) : sim.set_mem(op1, op2) # MOV iram addr,#data  0x75  3  None
    elif (inst == 0x86) : sim.set_mem(op1, sim.get_mem_r(0)) # MOV iram addr,@R0  0x86  2  None
    elif (inst == 0x87) : sim.set_mem(op1, sim.get_mem_r(1)) # MOV iram addr,@R1  0x87  2  None
    elif (inst == 0x88) : sim.set_mem(op1, sim.get_r(0)) # MOV iram addr,R0  0x88  2  None
    elif (inst == 0x89) : sim.set_mem(op1, sim.get_r(1)) # MOV iram addr,R1  0x89  2  None
    elif (inst == 0x8A) : sim.set_mem(op1, sim.get_r(2)) # MOV iram addr,R2  0x8A  2  None
    elif (inst == 0x8B) : sim.set_mem(op1, sim.get_r(3)) # MOV iram addr,R3  0x8B  2  None
    elif (inst == 0x8C) : sim.set_mem(op1, sim.get_r(4)) # MOV iram addr,R4  0x8C  2  None
    elif (inst == 0x8D) : sim.set_mem(op1, sim.get_r(5)) # MOV iram addr,R5  0x8D  2  None
    elif (inst == 0x8E) : sim.set_mem(op1, sim.get_r(6)) # MOV iram addr,R6  0x8E  2  None
    elif (inst == 0x8F) : sim.set_mem(op1, sim.get_r(7)) # MOV iram addr,R7  0x8F  2  None
    elif (inst == 0xF5) : sim.set_mem(op1, sim.a) # MOV iram addr,A  0xF5  2  None
    elif (inst == 0x85) : sim.set_mem(op2, sim.get_mem(op1)) # MOV iram addr,iram addr  0x85  3  None

    elif (inst == 0xA2) : 
        sim.set_c(sim.mem_get_bit(op1)) # MOV C,bit addr  0xA2  2  C

    elif (inst == 0x92) : 
        sim.mem_set_bit(op1, sim.c) # MOV bit addr,C  0x92  2  None


def inst_movc(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  MOVC
    #Function:  Move Code Byte to Accumulator
    #Syntax:  MOVC A,@A+register
    #Instructions  OpCode  Bytes  Flags
    #MOVC A,@A+DPTR  0x93  1  None
    #MOVC A,@A+PC  0x83  1  None
    #]]
    if (inst == 0x93) :
        addr = sim.a + sim.get_dptr()
    elif (inst == 0x83) :
        addr = sim.a + sim.pc
        
    sim.set_a(sim.get_code_space(addr))


def inst_movx(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  MOVX
    #Function:  Move Data To/From External Memory (XRAM)
    #Syntax:  MOVX operand1,operand2
    #Instructions  OpCode  Bytes  Flags
    #MOVX @DPTR,A  0xF0  1  None
    #MOVX @R0,A  0xF2  1  None
    #MOVX @R1,A  0xF3  1  None
    #MOVX A,@DPTR  0xE0  1  None
    #MOVX A,@R0  0xE2  1  None
    #MOVX A,@R1  0xE3  1  None
    #]]
    if (inst == 0xF0)   : sim.set_ext_mem(sim.get_dptr(), sim.a)     #MOVX @DPTR,A  0xF0  1  None
    elif (inst == 0xF2) : sim.set_ext_mem(sim.get_r(0), sim.a)       #MOVX @R0,A    0xF2  1  None
    elif (inst == 0xF3) : sim.set_ext_mem(sim.get_r(1), sim.a)
    elif (inst == 0xE0) :  #MOVX A,@DPTR  0xE0  1  None
        addr = sim.get_dptr()
        v = sim.get_ext_mem(addr)
        sim.set_a(v)
    elif (inst == 0xE2) : sim.set_a(sim.get_ext_mem(sim.get_r(0)))
    elif (inst == 0xE3) : sim.set_a(sim.get_ext_mem(sim.get_r(1)))
    

def inst_mul(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  MUL
    #Function:  Multiply Accumulator by B
    #Syntax:  MUL AB
    #MUL AB  0xA4  1  C, OV
    #MUL AB
    #BA = A * B
    #]]
    v = sim.a * sim.b

    if (v > 0xff) :
        sim.set_ov(1)
    else:
        sim.set_ov(0)

    sim.set_b((v >> 8) & 0xff)
    sim.set_a(v & 0xff)


def inst_orl(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  ORL
    #Function:  Bitwise OR
    #Syntax:  ORL operand1,operand2
    #Instructions  OpCode  Bytes  Flags
    #ORL iram addr,A  0x42  2  None
    #ORL iram addr,#data  0x43  3  None
    #ORL A,#data  0x44  2  None
    #ORL A,iram addr  0x45  2  None
    #ORL A,@R0  0x46  1  None
    #ORL A,@R1  0x47  1  None
    #ORL A,R0  0x48  1  None
    #ORL A,R1  0x49  1  None
    #ORL A,R2  0x4A  1  None
    #ORL A,R3  0x4B  1  None
    #ORL A,R4  0x4C  1  None
    #ORL A,R5  0x4D  1  None
    #ORL A,R6  0x4E  1  None
    #ORL A,R7  0x4F  1  None
    #ORL C,bit addr  0x72  2  C
    #ORL C,/bit addr  0xA0  2  C
    #]]

    if (inst == 0x72) :
        sim.set_c(bits_or(sim.c, sim.mem_get_bit(op1)) )
        return

    if (inst == 0xA0) :
        sim.set_c(bits_or(sim.c, sim.mem_get_nbit(op1)))
        return
       
    if (inst == 0x42) :
        v1 = sim.get_mem(op1)
        v2 = sim.a
    elif (inst == 0x43) :
        v1 = sim.get_mem(op1)
        v2 = op2

    elif (inst >= 0x44 and inst <= 0x4F) :
        v1 = sim.a
        if (inst == 0x44) : v2 = op1
        elif (inst == 0x45) : v2 = sim.get_mem(op1)
        elif (inst == 0x46) : v2 = sim.get_mem_r(0)
        elif (inst == 0x47) : v2 = sim.get_mem_r(1)
        elif (inst == 0x48) : v2 = sim.get_r(0)
        elif (inst == 0x49) : v2 = sim.get_r(1)
        elif (inst == 0x4A) : v2 = sim.get_r(2)
        elif (inst == 0x4B) : v2 = sim.get_r(3)
        elif (inst == 0x4C) : v2 = sim.get_r(4)
        elif (inst == 0x4D) : v2 = sim.get_r(5)
        elif (inst == 0x4E) : v2 = sim.get_r(6)
        elif (inst == 0x4F) : v2 = sim.get_r(7)

    #--print("bits_or", v1, v2)
    sim.set_a(bits_or(v1, v2))


def inst_pop(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  POP
    #Function:  Pop Value From Stack
    #Syntax:  POP
    #Instructions  OpCode  Bytes  Flags
    #POP iram addr  0xD0  2  None
    #]]
    v = sim.pop()
    if op1 <= 7:
        sim.set_r(op1, v)
    else:
        sim.set_mem(op1, v)

def inst_push(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  PUSH
    #Function:  Push Value Onto Stack
    #Syntax:  PUSH
    #Instructions  OpCode  Bytes  Flags
    #PUSH iram addr  0xC0  2  None
    #]]
    if op1 <= 7:
        sim.push(sim.get_r(op1))
    else:
        sim.push(sim.get_mem(op1))


def inst_ret(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  RET
    #Function:  Return From Subroutine
    #Syntax:  RET
    #Instructions  OpCode  Bytes  Flags
    #RET  0x22  1  None

    #PC15-8 = (SP)
    #SP = SP - 1
    #PC7-0 = (SP)
    #SP = SP - 1
    #]]
    sim.ret()

def inst_reti(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  RETI
    #Function:  Return From Interrupt
    #Syntax:  RETI
    #Instructions  OpCode  Bytes  Flags
    #RETI  0x32  1  None

    #PC15-8 = (SP)
    #SP = SP - 1
    #PC7-0 = (SP)
    #SP = SP - 1
    #]]
    sim.reti()

def inst_nop(inst_bytes, inst, op1, op2, op3):
    pass
    # nop is no operation, so... nothing to do

def inst_rl(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  RL
    #Function:  Rotate Accumulator Left
    #Syntax:  RL A
    #Instructions  OpCode  Bytes  Flags
    #RL A  0x23  1  None

    #An+1 = An WHERE n = 0 TO 6
    #A0 = A7
    #]]

    # get A7
    a7 = getbit(sim.a, 7)
    
    # do the rotation
    v = sim.a << 1
    
    # get bit 7-1, 0xfe = b'11111110
    v = bits_and(v, 0xfe)  
    
    # A0 = A7
    if (a7) :
        v = bits_or(v, 1)
    
    # store to A
    sim.set_a(v)

def inst_rlc(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  RLC
    #Function:  Rotate Accumulator Left Through Carry
    #Syntax:  RLC A
    #Instructions  OpCode  Bytes  Flags
    #RLC A  0x33  1  C

    #An+1 = AN WHERE N = 0 TO 6
    #A0 = C
    #C = A7
    #]]

    # do the rotate
    v = sim.a << 1
    
    # A0 = C
    a0 = sim.c
    
    # C = A7, because rotated, now is A8
    sim.set_c(getbit(v, 8))

    # store to A    
    sim.set_a((v & 0xfe) | a0)


def inst_rr(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  RR
    #Function:  Rotate Accumulator Right
    #Syntax:  RR A
    #Instructions  OpCode  Bytes  Flags
    #RR A  0x03  1  None

    #An = An+1 where n = 0 to 6
    #A7 = A0
    #]]    

    # get A0
    a0 = getbit(sim.a, 0)

    # do the rotate
    v = sim.a >> 1
    
    # get bit 6-0 only      
    v = bits_and(v, 0x7f) 

    # A7 = A0
    if (a0 != 0) :
        v = bits_or(v, 0x80)

    # store to A
    sim.set_a(v)


def inst_rrc(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  RRC
    #Function:  Rotate Accumulator Right Through Carry
    #Syntax:  RRC A
    #Instructions  OpCode  Bytes  Flags
    #RRC A  0x13  1  C

    #An = An+1 where n = 0 to 6
    #A7 = C
    #C = A0
    #]]
    
    # A7 = c
    a7 = sim.c

    # C = A0    
    sim.set_c(getbit(sim.a, 0))

    # do the rotate
    v = sim.a >> 1
    
    # get bit 0-6
    v = bits_and(v, 0x7f)

    # or with a7
    v = bits_or(v, a7)

    # store to A
    sim.set_a(v)


def inst_setb(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  SETB
    #Function:  Set Bit
    #Syntax:  SETB bit addr
    #Instructions  OpCode  Bytes  Flags
    #SETB C  0xD3  1  C
    #SETB bit addr  0xD2  2  None
    #]]
    if (inst == 0xD2) :
        sim.mem_set_bit(op1, 1)
    elif (inst == 0xD3) :
        sim.setc(1)


def inst_sjmp(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  SJMP
    #Function:  Short Jump
    #Syntax:  SJMP reladdr
    #Instructions  OpCode  Bytes  Flags
    #SJMP reladdr  0x80  2  None

    #PC = PC + 2
    #PC = PC + offset
    #]]
    sim.jump_rel(op1)

def inst_subb(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  SUBB
    #Function:  Subtract from Accumulator With Borrow
    #Syntax:  SUBB A,operand
    #Instructions  OpCode  Bytes  Flags
    #SUBB A,#data  0x94  2  C, AC, OV
    #SUBB A,iram addr  0x95  2  C, AC, OV
    #SUBB A,@R0  0x96  1  C, AC, OV
    #SUBB A,@R1  0x97  1  C, AC, OV
    #SUBB A,R0  0x98  1  C, AC, OV
    #SUBB A,R1  0x99  1  C, AC, OV
    #SUBB A,R2  0x9A  1  C, AC, OV
    #SUBB A,R3  0x9B  1  C, AC, OV
    #SUBB A,R4  0x9C  1  C, AC, OV
    #SUBB A,R5  0x9D  1  C, AC, OV
    #SUBB A,R6  0x9E  1  C, AC, OV
    #SUBB A,R7  0x9F  1  C, AC, OV
    #]]
    
    v1 = sim.a
    v2 = get_arth_inst_op2(inst, op1)
    if v1 >= v2 + sim.c:
        sim.set_a(v1 - sim.c - v2)
        sim.set_c(0)
    else:        
        sim.set_a(v1 - sim.c + 256 - v2)
        sim.set_c(1)
        #sim.check_overflow(sim.a, v1, v2)

def inst_swap(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  SWAP
    #Function:  Swap Accumulator Nibbles
    #Syntax:  SWAP A
    #Instructions  OpCode  Bytes  Flags
    #SWAP A  0xC4  1  None
    #A3-0 swap A7-4
    #]]
    a = sim.a
    a_3_0 = (a << 4) & 0xf0
    a_7_4 = (a >> 4) & 0x0f

    a = bits_or(a_3_0, a_7_4)

    sim_set_a(a)

def inst_xch(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  XCH
    #Function:  Exchange Bytes
    #Syntax:  XCH A,register
    #Instructions  OpCode  Bytes  Flags
    #XCH A,@R0  0xC6  1  None
    #XCH A,@R1  0xC7  1  None
    #XCH A,R0  0xC8  1  None
    #XCH A,R1  0xC9  1  None
    #XCH A,R2  0xCA  1  None
    #XCH A,R3  0xCB  1  None
    #XCH A,R4  0xCC  1  None
    #XCH A,R5  0xCD  1  None
    #XCH A,R6  0xCE  1  None
    #XCH A,R7  0xCF  1  None
    #XCH A,iram addr  0xC5  2  None

    #A swap (Ri)
    #]]
   
    v1 = sim.a
    if     (inst == 0xC5) :      #XCH A,iram addr  0xC5  2  None
        v2 = sim.get_mem(op1)
        sim.set_mem(op1, v1)
    elif (inst == 0xC6) :        #XCH A,@R0  0xC6  1  None
        v2 = sim.get_mem_r(0)   
        sim.set_mem_r(0, v1)
    elif (inst == 0xC7) :        #XCH A,@R1  0xC7  1  None
        v2 = sim.get_mem_r(1)   
        sim.set_mem_r(1, v1)
    elif (inst == 0xC8) : 
        v2 = sim.get_r(0)  
        sim.set_r(0, v1)
    elif (inst == 0xC9) : 
        v2 = sim.get_r(1)  
        sim.set_r(1, v1)
    elif (inst == 0xCA) : 
        v2 = sim.get_r(2)  
        sim.set_r(2, v1)
    elif (inst == 0xCB) : 
        v2 = sim.get_r(3)  
        sim.set_r(3, v1)
    elif (inst == 0xCC) : 
        v2 = sim.get_r(4)  
        sim.set_r(4, v1)
    elif (inst == 0xCD) : 
        v2 = sim.get_r(5)  
        sim.set_r(5, v1)
    elif (inst == 0xCE) : 
        v2 = sim.get_r(6)  
        sim.set_r(6, v1)
    elif (inst == 0xCF) : 
        v2 = sim.get_r(7)  
        sim.set_r(7, v1)    

    sim.set_a(v2)


def inst_xchd(inst_bytes, inst, op1, op2, op3):
    #--[[
    #Operation:  XCHD
    #Function:  Exchange Digit
    #Syntax:  XCHD A,[@R0/@R1]
    #Instructions  OpCode  Bytes  Flags
    #XCHD A,@R0  0xD6  1  None
    #XCHD A,@R1  0xD7  1  None
    #A3-0 swap (Ri)3-0
    #]]
    a = sim.a    
    a_3_0 = bits_and(sim.a, 0x0f)
    a_7_4 = bits_and(sim.a, 0xf0)

    # get address by instruction
    if (inst == 0xD6) :
        addr = sim.get_r(0)
    elif (inst == 0xD7) :
        addr = sim.get_r(1)
    
    r = sim.get_mem(addr)
    r_3_0 = bits_and(v2, 0x0f)
    r_7_4 = bits_and(v2, 0xf0)
    
    # A3-0 swap (Ri)3-0
    a = bits_or(a_7_4, r_3_0)
    r = bits_or(r_7_4, a_3_0)  

    sim.set_a(a)
    sim.set_mem(addr, r)


def inst_xrl(inst_bytes, inst, op1, op2, op3):
    #Operation:  XRL
    #Function:  Bitwise Exclusive OR
    #Syntax:  XRL operand1,operand2
    #Instructions  OpCode  Bytes  Flags
    #XRL iram addr,A  0x62  2  None
    #XRL iram addr,#data  0x63  3  None
    #XRL A,#data  0x64  2  None
    #XRL A,iram addr  0x65  2  None
    #XRL A,@R0  0x66  1  None
    #XRL A,@R1  0x67  1  None
    #XRL A,R0  0x68  1  None
    #XRL A,R1  0x69  1  None
    #XRL A,R2  0x6A  1  None
    #XRL A,R3  0x6B  1  None
    #XRL A,R4  0x6C  1  None
    #XRL A,R5  0x6D  1  None
    #XRL A,R6  0x6E  1  None
    #XRL A,R7  0x6F  1  None
    #A = A XOR immediate    

    if  (inst == 0x62) : 
        sim.set_mem(op1, sim.get_mem(op1) ^ sim.a)
    elif (inst == 0x63) : 
        sim.set_mem(op1, sim.get_mem(op1) ^ op2)
    elif (inst == 0x64) : 
        sim.set_a(sim.a ^ op1)
    elif (inst == 0x65) : 
        sim.set_a(sim.a ^ sim.get_mem(op1))
    elif (inst == 0x66) : 
        sim.set_a(sim.a ^ sim.get_mem_r(0))
    elif (inst == 0x67) : 
        sim.set_a(sim.a ^ sim.get_mem_r(1))
    elif (inst == 0x68) : 
        sim.set_a(sim.a ^ sim.get_r(0))
    elif (inst == 0x69) : 
        sim.set_a(sim.a ^ sim.get_r(1))
    elif (inst == 0x6A) : 
        sim.set_a(sim.a ^ sim.get_r(2))
    elif (inst == 0x6B) : 
        sim.set_a(sim.a ^ sim.get_r(3))
    elif (inst == 0x6C) : 
        sim.set_a(sim.a ^ sim.get_r(4))
    elif (inst == 0x6D) : 
        sim.set_a(sim.a ^ sim.get_r(5))
    elif (inst == 0x6E) : 
        sim.set_a(sim.a ^ sim.get_r(6))
    elif (inst == 0x6F) : 
        sim.set_a(sim.a ^ sim.get_r(7))


def inst_undef(inst_bytes, inst, op1, op2, op3):
    pass
