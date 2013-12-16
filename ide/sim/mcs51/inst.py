import define
from utils import *


#--------------------------------------------------------------------------------
def inst_acall(sim, inst, op1):
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

#--------------------------------------------------------------------------------
def inst_add_24(sim, inst, op1, op2, op3):
    #ADD A,#data  0x24  2  1  C, AC, OV   
    sim.add_a(op1, 0)
    
#----------------------------------------------------------------
def inst_add_25(sim, inst, op1, op2, op3):
    #ADD A,iram_addr  0x25  2  1  C, AC, OV
    v1 = sim.a 
    v2 = sim.get_mem(op1)
    v = v1 + v2
    sim.set_a(v)
    sim.check_overflow(v, v1, v2)
    
#----------------------------------------------------------------
def inst_add_26(sim, inst, op1, op2, op3):
    #ADD A,@R0  0x26  1  1  C, AC, OV
    v2 = sim.get_mem_r(0)
    sim.add_a(v2, 0)
    
#----------------------------------------------------------------
def inst_add_27(sim, inst, op1, op2, op3):
    #ADD A,@R1  0x27  1  1  C, AC, OV
    v2 = sim.get_mem_r(1)
    sim.add_a(v2, 0)
    
#----------------------------------------------------------------
def inst_add_28_2F(sim, inst, op1, op2, op3):
    #ADD A,R0  0x28  1  1  C, AC, OV
    v2 = sim.get_r(inst)
    sim.add_a(v2, 0)

#--------------------------------------------------------------------------------
def inst_addc_34(sim, inst, op1, op2, op3):
    #ADDC A,#data  0x34  2  1  C, AC, OV   
    v2 = op1
    sim.add_a(v2, sim.c)
    
def inst_addc_35(sim, inst, op1, op2, op3):
    #ADDC A,iram_addr  0x35  2  1  C, AC, OV
    v2 = sim.get_mem(op1)
    sim.add_a(v2, sim.c)

def inst_addc_36(sim, inst, op1, op2, op3):
    #ADD A,@R0  0x36  1  1  C, AC, OV
    v2 = sim.get_mem_r(0)
    sim.add_a(v2, sim.c)
    
def inst_addc_37(sim, inst, op1, op2, op3):
    #ADDC A,@R1  0x37  1  1  C, AC, OV
    v2 = sim.get_mem_r(0)
    sim.add_a(v2, sim.c)
    
def inst_addc_38_3F(sim, inst, op1, op2, op3):
    #ADDC A,R0  0x38  1  1  C, AC, OV
    v2 = sim.get_r(inst)
    sim.add_a(v2, sim.c)
    
#--------------------------------------------------------------------------------
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
def inst_ajmp(sim, inst, op1, op2, op3):
    addr = ((inst - 0x01) * 0x40) + op1
    sim.jump(addr)

#--------------------------------------------------------------------------------
# ANL does a bitwise "AND" operation between operand1 and operand2, 
# leaving the resulting value in operand1.
def inst_anl_52(sim, inst, op1, op2, op3):
    sim.set_mem(op1, bits_and(sim.get_mem(op1), sim.a))  # ANL iram addr,A  0x52  2  None
    
def inst_anl_53(sim, inst, op1, op2, op3):
    sim.set_mem(op1, bits_and(sim.get_mem(op1), op2))    # ANL iram addr,#data  0x53  3  None
    
def inst_anl_54(sim, inst, op1, op2, op3):
    sim.set_a(bits_and(sim.a, op1))             # ANL A,#data  0x54  2  None
    
def inst_anl_55(sim, inst, op1, op2, op3):
    sim.set_a(bits_and(sim.a, sim.get_mem(op1)))    # ANL A,iram addr  0x55  2  None
    
def inst_anl_56(sim, inst, op1, op2, op3):
    sim.set_a(bits_and(sim.a, sim.get_mem_r(0))) # ANL A,@R0  0x56  1  None

def inst_anl_57(sim, inst, op1, op2, op3):    
    sim.set_a(bits_and(sim.a, sim.get_mem_r(1))) # ANL A,@R1  0x57  1  None
    
def inst_anl_58_5F(sim, inst, op1, op2, op3):
    sim.set_a(bits_and(sim.a, sim.get_r(inst)))  # ANL A,R0  0x58  1  None    
    
def inst_anl_82(sim, inst, op1, op2, op3):
    sim.set_c(bits_and(sim.c, sim.mem_get_bit(op1)))  # ANL C,bit addr  0x82  2  C
    
def inst_anl_B0(sim, inst, op1, op2, op3):
    sim.set_c(bits_and(sim.c, sim.mem_get_nbit(op1)))  # ANL C,/bit addr  0xB0  2  C
    
#--------------------------------------------------------------------------------
# Operation:  CJNE
# Function:  Compare and Jump If Not Equal
# Syntax:  CJNE operand1,operand2,reladdr   
# The Carry bit (C) is set if operand1 is less than operand2, otherwise it is cleared.
def inst_cjne_B4(sim, inst, op1, op2, op3):
    # CJNE A,#data,reladdr  0xB4  3  C
    v1 = sim.a
    v2 = op1
    
    if (v1 < v2) : 
        sim.set_c(1) 
    else :
        sim.set_c(0)
    
    # compares the value of operand1 and operand2 and branches to the indicated relative address 
    # if operand1 and operand2 are not equal. 
    # If the two operands are equal program flow continues with the instruction following the CJNE instruction.
    if (v1 != v2) :
        sim.jump_rel(op2)
        
        
def inst_cjne_B5(sim, inst, op1, op2, op3):
    # CJNE A,iram addr,reladdr  0xB5  3  C
    v1 = sim.a
    v2 = sim.get_mem(op1)

    if (v1 < v2) : 
        sim.set_c(1) 
    else :
        sim.set_c(0)

    if (v1 != v2) :
        sim.jump_rel(op2)
        
def inst_cjne_B6(sim, inst, op1, op2, op3):
    # CJNE @R0,#data,reladdr  0xB6  3  C
    v1 = sim.get_mem_r(0)
    v2 = op1

    if (v1 < v2) : 
        sim.set_c(1) 
    else :
        sim.set_c(0)

    if (v1 != v2) :
        sim.jump_rel(op2)
        
def inst_cjne_B7(sim, inst, op1, op2, op3):
    # CJNE @R1,#data,reladdr  0xB7  3  C
    v1 = sim.get_mem_r(1)
    v2 = op1

    if (v1 < v2) : 
        sim.set_c(1) 
    else :
        sim.set_c(0)

    if (v1 != v2) :
        sim.jump_rel(op2)
        
def inst_cjne_B8_BF(sim, inst, op1, op2, op3):
    # CJNE R0,#data,reladdr  0xB8  3  C
    v1 = sim.get_r(inst)
    v2 = op1

    if (v1 < v2) : 
        sim.set_c(1) 
    else :
        sim.set_c(0)

    if (v1 != v2) :
        sim.jump_rel(op2)

#--------------------------------------------------------------------------------
def inst_clr_C2(sim, inst, op1, op2, op3):
    #CLR bit addr  0xC2  2  None
    sim.mem_set_bit(op1, 0)
        
def inst_clr_C3(sim, inst, op1, op2, op3):
    #CLR C  0xC3  1  C
    sim.set_c(0)
     
def inst_clr_E4(sim, inst, op1, op2, op3):
    #CLR A  0xE4  1  None
    sim.set_a(0)

#--------------------------------------------------------------------------------
def inst_cpl_F4(sim, inst, op1, op2, op3):
    #Operation:  CPL
    #Function:  Complement Register
    #Syntax:  CPL operand
    #Instructions  OpCode  Bytes  Flags
    #CPL A  0xF4  1  None
    sim.set_a(comp8(sim.a))

def inst_cpl_B3(sim, inst, op1, op2, op3):
    #CPL C  0xB3  1  C
    if sim.c == 1:
        sim.set_c(0)
    else:
        sim.set_c(1)

def inst_cpl_B2(sim, inst, op1, op2, op3):
    #CPL bit addr  0xB2  2  None
    sim.mem_set_bit(op1, sim.mem_get_nbit(op1))  # op1 is bit addr
        
#--------------------------------------------------------------------------------
def inst_da(sim, inst, op1, op2, op3):
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
        
    
#--------------------------------------------------------------------------------
#Operation:  DEC
#Function:  Decrement Register
#Syntax:  DEC register

def dec(v):
    if v == 0 : 
        return 0xff
    else :
        return v - 1
    
def inst_dec_14(sim, inst, op1, op2, op3):
    sim.set_a(dec(sim.a))

def inst_dec_15(sim, inst, op1, op2, op3):
    sim.set_mem(op1, dec(sim.get_mem(op1)))
    
def inst_dec_16(sim, inst, op1, op2, op3):
    sim.set_mem_r(0, dec(sim.get_mem_r(0)))
    
def inst_dec_17(sim, inst, op1, op2, op3):
    sim.set_mem_r(1, dec(sim.get_mem_r(1)))
    
def inst_dec_18_1F(sim, inst, op1, op2, op3):
    sim.set_r(inst, dec(sim.get_r(inst)))
    

#--------------------------------------------------------------------------------
def inst_div(sim, inst, op1, op2, op3):
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
        
#--------------------------------------------------------------------------------
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
def inst_djnz_D5(sim, inst, op1, op2, op3):
    v = sim.set_mem(op1, dec(sim.get_mem(op1)))
    if (v != 0) :
        sim.jump_rel(op2)
 
            
def inst_djnz_D8_DF(sim, inst, op1, op2, op3):
    v = sim.set_r(inst, dec(sim.get_r(inst)))

    if (v != 0) :
        sim.jump_rel(op1)

#--------------------------------------------------------------------------------
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

#--------------------------------------------------------------------------------
def inst_inc_04(sim, inst, op1, op2, op3):
    sim.set_a(inc(sim.a))
    
def inst_inc_05(sim, inst, op1, op2, op3):
    sim.set_mem(op1, inc(sim.get_mem(op1)))
    
def inst_inc_06(sim, inst, op1, op2, op3):
    sim.set_mem_r(0, inc(sim.get_mem_r(0)))
    
def inst_inc_07(sim, inst, op1, op2, op3):
    sim.set_mem_r(1, inc(sim.get_mem_r(1)))
    
def inst_inc_08_0F(sim, inst, op1, op2, op3):
    sim.set_r(inst, inc(sim.get_r(inst)))
    
def inst_inc_A3(sim, inst, op1, op2, op3):
    sim.inc_dptr()
    
    
#--------------------------------------------------------------------------------
def inst_jb(sim, inst, op1, op2, op3):
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

#--------------------------------------------------------------------------------
def inst_jbc(sim, inst, op1, op2, op3):
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

#--------------------------------------------------------------------------------
def inst_jc(sim, inst, op1, op2, op3):
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

#--------------------------------------------------------------------------------
def inst_jmp(sim, inst, op1, op2, op3):
    #--[[
    #Operation:  JMP
    #Function:  Jump to Data Pointer + Accumulator
    #Syntax:  JMP @A+DPTR
    #Instructions  OpCode  Bytes  Flags
    #JMP @A+DPTR  0x73  1  None

    #PC = PC + DPTR
    #]]
    sim.jump(sim.a + sim.get_dptr())

#--------------------------------------------------------------------------------
def inst_jnb(sim, inst, op1, op2, op3):
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

#--------------------------------------------------------------------------------
def inst_jnc(sim, inst, op1, op2, op3):
    #--[[
    #Operation:  JNC
    #Function:  Jump if Carry Not Set
    #Syntax:  JNC reladdr
    #Instructions  OpCode  Bytes  Flags
    #JNC reladdr  0x50  2  None
    #]]
    if (sim.c == 0) :
        sim.jump_rel(op1)

#--------------------------------------------------------------------------------
def inst_jnz(sim, inst, op1, op2, op3):
    #--[[
    #Operation:  JNZ
    #Function:  Jump if Accumulator Not Zero
    #Syntax:  JNZ reladdr
    #Instructions  OpCode  Bytes  Flags
    #JNZ reladdr  0x70  2  None
    #]]
    if (sim.a != 0) :
        sim.jump_rel(op1)

#--------------------------------------------------------------------------------
def inst_jz(sim, inst, op1, op2, op3):
    #--[[
    #Operation:  JZ
    #Function:  Jump if Accumulator Zero
    #Syntax:  JNZ reladdr
    #Instructions  OpCode  Bytes  Flags
    #JZ reladdr  0x60  2  None
    #]]
    if (sim.a == 0) :
        sim.jump_rel(op1)

#--------------------------------------------------------------------------------
def inst_lcall(sim, inst, op1, op2, op3):
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
    #print("inst_lcall", sim, hex((op1 * 256) + op2))
    sim.call((op1 * 256) + op2)

#--------------------------------------------------------------------------------
def inst_ljmp(sim, inst, op1, op2, op3):
    #--[[
    #Operation:  LJMP
    #Function:  Long Jump
    #Syntax:  LJMP code addr
    #Instructions  OpCode  Bytes  Flags
    #LJMP code addr  0x02  3  None

    #PC = addr16
    #]]
    sim.jump((op1 * 256) + op2)
    

#--------------------------------------------------------------------------------
# Description: MOV copies the value of operand2 into operand1. 
# The value of operand2 is not affected. 
# Both operand1 and operand2 must be in Internal RAM. 
# No flags are affected unless the instruction is moving the value of a bit into the carry bit 
# in which case the carry bit is affected or unless the instruction is moving a value into the PSW register 
# (which contains all the program flags).

# ** Note: In the case of "MOV iram addr,iram addr", 
# the operand sim of the instruction are stored in reverse order. 
# That is, the instruction consisting of the sim 0x85, 0x20, 0x50 
# means "Move the contents of Internal RAM location 0x20 to 
# Internal RAM location 0x50" whereas the opposite would be generally presumed.

# print("mov ", tohex(inst, 2), tohex(op1, 2), tohex(op2, 2))


def inst_mov_76(sim, inst, op1, op2, op3):
    sim.set_mem_r(0, op1)       # MOV @R0,#data  0x76  2  None        
    
def inst_mov_77(sim, inst, op1, op2, op3):
    sim.set_mem_r(1, op1)   # MOV @R1,#data  0x77  2  None
    
def inst_mov_F6(sim, inst, op1, op2, op3):
    sim.set_mem_r(0, sim.a) # MOV @R0,A  0xF6  1  None
    
def inst_mov_F7(sim, inst, op1, op2, op3):
    sim.set_mem_r(1, sim.a) # MOV @R1,A  0xF7  1  None
    
def inst_mov_A6(sim, inst, op1, op2, op3):
    sim.set_mem_r(0, sim.get_mem(op1)) # MOV @R0,iram addr  0xA6  2  None       

def inst_mov_A7(sim, inst, op1, op2, op3):
    sim.set_mem_r(1, sim.get_mem(op1)) # MOV @R1,iram addr  0xA7  2  None

def inst_mov_74(sim, inst, op1, op2, op3):
    sim.set_a(op1) # MOV A,#data  0x74  2  None
    
def inst_mov_E6(sim, inst, op1, op2, op3):
    sim.set_a(sim.get_mem_r(0)) # MOV A,@R0  0xE6  1  None
    
def inst_mov_E7(sim, inst, op1, op2, op3):
    sim.set_a(sim.get_mem_r(1)) # MOV A,@R1  0xE7  1  None
    
def inst_mov_E8_EF(sim, inst, op1, op2, op3):
    sim.set_a(sim.get_r(inst)) # MOV A,R0  0xE8  1  None
    
    
def inst_mov_E5(sim, inst, op1, op2, op3):
    sim.set_a(sim.get_mem(op1)) # MOV A,iram addr  0xE5  2  None

def inst_mov_90(sim, inst, op1, op2, op3):
    sim.set_dptr(op1, op2) # MOV DPTR,#data16  0x90  3  None

def inst_mov_78_7F(sim, inst, op1, op2, op3):
    sim.set_r(inst - 0x78, op1) # MOV R0,#data  0x78  2  None
    
def inst_mov_F8_FF(sim, inst, op1, op2, op3):
    sim.set_r(inst - 0xF8, sim.a) # MOV R0,A  0xF8  1  None
    
def inst_mov_A8_AF(sim, inst, op1, op2, op3):
    sim.set_r(inst - 0xA8, sim.get_mem(op1)) # MOV R0,iram addr  0xA8  2  None
    
def inst_mov_88_8F(sim, inst, op1, op2, op3):
    sim.set_mem(op1, sim.get_r(inst)) # MOV iram addr,R0  0x88  2  None
    
def inst_mov_75(sim, inst, op1, op2, op3):
    sim.set_mem(op1, op2) # MOV iram addr,#data  0x75  3  None
    
def inst_mov_86(sim, inst, op1, op2, op3):
    sim.set_mem(op1, sim.get_mem_r(0)) # MOV iram addr,@R0  0x86  2  None
    
def inst_mov_87(sim, inst, op1, op2, op3):
    sim.set_mem(op1, sim.get_mem_r(1)) # MOV iram addr,@R1  0x87  2  None
    
def inst_mov_F5(sim, inst, op1, op2, op3):
    sim.set_mem(op1, sim.a) # MOV iram addr,A  0xF5  2  None
    
def inst_mov_85(sim, inst, op1, op2, op3):
    sim.set_mem(op2, sim.get_mem(op1)) # MOV iram addr,iram addr  0x85  3  None
    
def inst_mov_A2(sim, inst, op1, op2, op3):
    sim.set_c(sim.mem_get_bit(op1)) # MOV C,bit addr  0xA2  2  C

def inst_mov_92(sim, inst, op1, op2, op3):
    sim.mem_set_bit(op1, sim.c) # MOV bit addr,C  0x92  2  None

#--------------------------------------------------------------------------------
#--[[
#Operation:  MOVC
#Function:  Move Code Byte to Accumulator
#Syntax:  MOVC A,@A+register
#Instructions  OpCode  Bytes  Flags
#MOVC A,@A+DPTR  0x93  1  None
#MOVC A,@A+PC  0x83  1  None
#]]

def inst_movc_93(sim, inst, op1, op2, op3):
    addr = sim.a + sim.get_dptr()
    sim.set_a(sim.get_code_space(addr))
    
def inst_movc_83(sim, inst, op1, op2, op3):
    addr = sim.a + sim.pc
    sim.set_a(sim.get_code_space(addr))

#--------------------------------------------------------------------------------
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
def inst_movx_F0(sim, inst, op1, op2, op3):
    sim.set_ext_mem(sim.get_dptr(), sim.a)     #MOVX @DPTR,A  0xF0  1  None
    
def inst_movx_F2(sim, inst, op1, op2, op3):
    sim.set_ext_mem(sim.get_r(0), sim.a)       #MOVX @R0,A    0xF2  1  None
    
def inst_movx_F3(sim, inst, op1, op2, op3):
    sim.set_ext_mem(sim.get_r(1), sim.a)
    
def inst_movx_E0(sim, inst, op1, op2, op3):
    #MOVX A,@DPTR  0xE0  1  None
    addr = sim.get_dptr()
    v = sim.get_ext_mem(addr)
    sim.set_a(v)
    
def inst_movx_E2(sim, inst, op1, op2, op3):
    sim.set_a(sim.get_ext_mem(sim.get_r(0)))
    
def inst_movx_E3(sim, inst, op1, op2, op3):
    sim.set_a(sim.get_ext_mem(sim.get_r(1)))
    
#--------------------------------------------------------------------------------
def inst_mul(sim, inst, op1, op2, op3):
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

#--------------------------------------------------------------------------------
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

def inst_orl_42(sim, inst, op1, op2, op3):
    #ORL iram addr,A  0x42  2  None
    sim.set_a(sim.get_mem(op1) | sim.a)
        
def inst_orl_43(sim, inst, op1, op2, op3):
    #ORL iram addr,#data  0x43  3  None
    sim.set_a(sim.get_mem(op1) | op2)
    
def inst_orl_44(sim, inst, op1, op2, op3):
    #ORL A,#data  0x44  2  None
    sim.set_a(sim.a | op1)
    
def inst_orl_45(sim, inst, op1, op2, op3):
    #ORL A,iram addr  0x45  2  None
    sim.set_a(sim.a | sim.get_mem(op1))
    
def inst_orl_46(sim, inst, op1, op2, op3):
    #ORL A,@R0  0x46  1  None
    sim.set_a(sim.a | sim.get_mem_r(0))
    
def inst_orl_47(sim, inst, op1, op2, op3):
    #ORL A,@R1  0x47  1  None
    sim.set_a(sim.a | sim.get_mem_r(1))
    
def inst_orl_48_4F(sim, inst, op1, op2, op3):
    #ORL A,R0  0x48  1  None
    sim.set_a(sim.a | sim.get_r(inst))

def inst_orl_72(sim, inst, op1, op2, op3):
    sim.set_c(sim.c | sim.mem_get_bit(op1))
    
def inst_orl_A0(sim, inst, op1, op2, op3):
    sim.set_c(sim.c | sim.mem_get_nbit(op1))

    
#--------------------------------------------------------------------------------
def inst_pop(sim, inst, op1, op2, op3):
    #--[[
    #Operation:  POP
    #Function:  Pop Value From Stack
    #Syntax:  POP
    #Instructions  OpCode  Bytes  Flags
    #POP iram addr  0xD0  2  None
    #]]
    v = sim.pop()
    sim.set_mem(op1, v)
    
#--------------------------------------------------------------------------------
def inst_push(sim, inst, op1, op2, op3):
    #--[[
    #Operation:  PUSH
    #Function:  Push Value Onto Stack
    #Syntax:  PUSH
    #Instructions  OpCode  Bytes  Flags
    #PUSH iram addr  0xC0  2  None
    #]]
    sim.push(sim.get_mem(op1))

#--------------------------------------------------------------------------------
def inst_ret(sim, inst, op1, op2, op3):
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

#--------------------------------------------------------------------------------
def inst_reti(sim, inst, op1, op2, op3):
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

#--------------------------------------------------------------------------------
def inst_nop(sim, inst, op1, op2, op3):
    pass
    # nop is no operation, so... nothing to do

#--------------------------------------------------------------------------------
def inst_rl(sim, inst, op1, op2, op3):
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
    v = v & 0xfe
    
    # A0 = A7
    if (a7) :
        v = bits_or(v, 1)
    
    # store to A
    sim.set_a(v)

#--------------------------------------------------------------------------------
def inst_rlc(sim, inst, op1, op2, op3):
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

#--------------------------------------------------------------------------------
def inst_rr(sim, inst, op1, op2, op3):
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
    v = v & 0x7f

    # A7 = A0
    if (a0 != 0) :
        v = v | 0x80

    # store to A
    sim.set_a(v)

#--------------------------------------------------------------------------------
def inst_rrc(sim, inst, op1, op2, op3):
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
    a7 = sim.c << 7

    # C = A0    
    sim.set_c(getbit(sim.a, 0))

    # do the rotate
    #v = sim.a >> 1
    
    # get bit 0-6
    #v = v & 0x7f

    # or with a7
    #v = v | a7
    
    v = ((sim.a >> 1) & 0x7f) | a7
    
    # store to A
    sim.set_a(v)

#--------------------------------------------------------------------------------
#--[[
#Operation:  SETB
#Function:  Set Bit
#Syntax:  SETB bit addr
#Instructions  OpCode  Bytes  Flags
#SETB C  0xD3  1  C
#SETB bit addr  0xD2  2  None
#]]
def inst_setb_D2(sim, inst, op1, op2, op3):
    sim.mem_set_bit(op1, 1)
    
def inst_setb_D3(sim, inst, op1, op2, op3):
    sim.set_c(1)
        
#--------------------------------------------------------------------------------
#--[[
#Operation:  SJMP
#Function:  Short Jump
#Syntax:  SJMP reladdr
#Instructions  OpCode  Bytes  Flags
#SJMP reladdr  0x80  2  None

#PC = PC + 2
#PC = PC + offset
#]]
def inst_sjmp(sim, inst, op1, op2, op3):
    sim.jump_rel(op1)

#--------------------------------------------------------------------------------
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
    
def subb(sim, v2):
    v1 = sim.a
    if v1 >= v2 + sim.c:
        sim.set_a(v1 - sim.c - v2)
        sim.set_c(0)
    else:        
        sim.set_a(v1 - sim.c + 256 - v2)
        sim.set_c(1)
        
def inst_subb_94(sim, inst, op1, op2, op3):
    #SUBB A,#data  0x94  2  C, AC, OV
    subb(sim, op1)
    
def inst_subb_95(sim, inst, op1, op2, op3):
    #SUBB A,iram addr  0x95  2  C, AC, OV
    subb(sim, sim.get_mem(op1))
    
def inst_subb_96(sim, inst, op1, op2, op3):
    #SUBB A,@R0  0x96  1  C, AC, OV
    subb(sim, sim.get_mem_r(0))
    
def inst_subb_97(sim, inst, op1, op2, op3):
    #SUBB A,@R1  0x97  1  C, AC, OV
    subb(sim, sim.get_mem_r(1))

def inst_subb_98_9F(sim, inst, op1, op2, op3):
    #SUBB A,R0  0x98  1  C, AC, OV
    subb(sim, sim.get_r(inst))

        
#--------------------------------------------------------------------------------
def inst_swap(sim, inst, op1, op2, op3):
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

#--------------------------------------------------------------------------------
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
   
def inst_xch_C5(sim, inst, op1, op2, op3):
    #XCH A,iram addr  0xC5  2  None
    v1 = sim.a
    v2 = sim.get_mem(op1)
    sim.set_mem(op1, v1)
    sim.set_a(v2)
    
def inst_xch_C6(sim, inst, op1, op2, op3):
    #XCH A,@R0  0xC6  1  None
    v1 = sim.a
    v2 = sim.get_mem_r(0)   
    sim.set_mem_r(0, v1)
    sim.set_a(v2)

def inst_xch_C7(sim, inst, op1, op2, op3):
    #XCH A,@R1  0xC7  1  None
    v1 = sim.a
    v2 = sim.get_mem_r(1)   
    sim.set_mem_r(1, v1)
    sim.set_a(v2)
    
def inst_xch_C8_CF(sim, inst, op1, op2, op3):
    #XCH A,R0  0xC8  1  None
    v1 = sim.a
    v2 = sim.get_r(inst)
    sim.set_r(inst, v1)
    sim.set_a(v2)
    
        
#--------------------------------------------------------------------------------
def inst_xchd(sim, inst, op1, op2, op3):
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

#--------------------------------------------------------------------------------
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

def inst_xrl_62(sim, inst, op1, op2, op3):
    #XRL iram addr,A  0x62  2  None
    sim.set_mem(op1, sim.get_mem(op1) ^ sim.a)
    
def inst_xrl_63(sim, inst, op1, op2, op3):
    #XRL iram addr,#data  0x63  3  None
    sim.set_mem(op1, sim.get_mem(op1) ^ op2)
    
def inst_xrl_64(sim, inst, op1, op2, op3):
    #XRL A,#data  0x64  2  None
    sim.set_a(sim.a ^ op1)
    
def inst_xrl_65(sim, inst, op1, op2, op3):
    #XRL A,iram addr  0x65  2  None
    sim.set_mem(op1, sim.get_mem(op1) ^ sim.a)
    
def inst_xrl_66(sim, inst, op1, op2, op3):
    #XRL A,@R0  0x66  1  None
    sim.set_a(sim.a ^ sim.get_mem_r(0))
    
def inst_xrl_67(sim, inst, op1, op2, op3):
    #XRL A,@R1  0x67  1  None
    sim.set_a(sim.a ^ sim.get_mem_r(1))

def inst_xrl_68_6F(sim, inst, op1, op2, op3):
    #XRL A,R0  0x68  1  None
    sim.set_a(sim.a ^ sim.get_r(inst - 0x68))
    

#--------------------------------------------------------------------------------
def inst_undef(sim, inst, op1, op2, op3):
    pass

#def temp():
    
    #t1 =  """
    #I_NOP,   I_AJMP,  I_LJMP,  I_RR,    I_INC,   I_INC,   I_INC,   I_INC,   I_INC,   I_INC,   I_INC,   I_INC,   I_INC,   I_INC,   I_INC,   I_INC,
    #I_JBC,   I_ACALL, I_LCALL, I_RRC,   I_DEC,   I_DEC,   I_DEC,   I_DEC,   I_DEC,   I_DEC,   I_DEC,   I_DEC,   I_DEC,   I_DEC,   I_DEC,   I_DEC,  
    #I_JB,    I_AJMP,  I_RET,   I_RL,    I_ADD,   I_ADD,   I_ADD,   I_ADD,   I_ADD,   I_ADD,   I_ADD,   I_ADD,   I_ADD,   I_ADD,   I_ADD,   I_ADD,   
    #I_JNB,   I_ACALL, I_RETI,  I_RLC,   I_ADDC,  I_ADDC,  I_ADDC,  I_ADDC,  I_ADDC,  I_ADDC,  I_ADDC,  I_ADDC,  I_ADDC,  I_ADDC,  I_ADDC,  I_ADDC, 
     
    #I_JC,    I_AJMP,  I_ORL,   I_ORL,   I_ORL,   I_ORL,   I_ORL,   I_ORL,   I_ORL,   I_ORL,   I_ORL,   I_ORL,   I_ORL,   I_ORL,   I_ORL,   I_ORL,   
    #I_JNC,   I_ACALL, I_ANL,   I_ANL,   I_ANL,   I_ANL,   I_ANL,   I_ANL,   I_ANL,   I_ANL,   I_ANL,   I_ANL,   I_ANL,   I_ANL,   I_ANL,   I_ANL,   
    #I_JZ,    I_AJMP,  I_XRL,   I_XRL,   I_XRL,   I_XRL,   I_XRL,   I_XRL,   I_XRL,   I_XRL,   I_XRL,   I_XRL,   I_XRL,   I_XRL,   I_XRL,   I_XRL,   
    #I_JNZ,   I_ACALL, I_ORL,   I_JMP,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV, 
      
    #I_SJMP,  I_AJMP,  I_ANL,   I_MOVC,  I_DIV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   
    #I_MOV,   I_ACALL, I_MOV,   I_MOVC,  I_SUBB,  I_SUBB,  I_SUBB,  I_SUBB,  I_SUBB,  I_SUBB,  I_SUBB,  I_SUBB,  I_SUBB,  I_SUBB,  I_SUBB,  I_SUBB,  
    #I_ORL,   I_AJMP,  I_MOV,   I_INC,   I_MUL,   I_UNDEF, I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   
    #I_ANL,   I_ACALL, I_CPL,   I_CPL,   I_CJNE,  I_CJNE,  I_CJNE,  I_CJNE,  I_CJNE,  I_CJNE,  I_CJNE,  I_CJNE,  I_CJNE,  I_CJNE,  I_CJNE,  I_CJNE,  
    
    #I_PUSH,  I_AJMP,  I_CLR,   I_CLR,   I_SWAP,  I_XCH,   I_XCH,   I_XCH,   I_XCH,   I_XCH,   I_XCH,   I_XCH,   I_XCH,   I_XCH,   I_XCH,   I_XCH,  
    #I_POP,   I_ACALL, I_SETB,  I_SETB,  I_DA,    I_DJNZ,  I_XCHD,  I_XCHD,  I_DJNZ,  I_DJNZ,  I_DJNZ,  I_DJNZ,  I_DJNZ,  I_DJNZ,  I_DJNZ,  I_DJNZ,  
    #I_MOVX,  I_AJMP,  I_MOVX,  I_MOVX,  I_CLR,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   
    #I_MOVX,  I_ACALL, I_MOVX,  I_MOVX,  I_CPL,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   
    #"""    
    #i = 0
    #for s in t1.split(','):
        #s = s.lower().strip()
        #s = s.replace("i_", "inst_")
        
        #j = i & 0xf
        #if j >= 0x8:
            #k = (i & 0xf0)
            #k8 = k + 0x8
            #kf = k + 0xf
            #s += '_' + tohex(k8, 2) + '_' + tohex(kf, 2) + ', '
        #else:
            #s += '_' + tohex(i, 2) + ', '
        #print s
        #i += 1
        
        

inst_handler = [
    inst_nop,    
    inst_ajmp, 
    inst_ljmp, 
    inst_rr, 
    inst_inc_04, 
    inst_inc_05, 
    inst_inc_06, 
    inst_inc_07, 
    inst_inc_08_0F, 
    inst_inc_08_0F, 
    inst_inc_08_0F, 
    inst_inc_08_0F, 
    inst_inc_08_0F, 
    inst_inc_08_0F, 
    inst_inc_08_0F, 
    inst_inc_08_0F, 
    inst_jbc, 
    inst_acall, 
    inst_lcall, 
    inst_rrc, 
    inst_dec_14, 
    inst_dec_15, 
    inst_dec_16, 
    inst_dec_17, 
    inst_dec_18_1F, 
    inst_dec_18_1F, 
    inst_dec_18_1F, 
    inst_dec_18_1F, 
    inst_dec_18_1F, 
    inst_dec_18_1F, 
    inst_dec_18_1F, 
    inst_dec_18_1F, 
    inst_jb, 
    inst_ajmp, 
    inst_ret, 
    inst_rl, 
    inst_add_24, 
    inst_add_25, 
    inst_add_26, 
    inst_add_27, 
    inst_add_28_2F, 
    inst_add_28_2F, 
    inst_add_28_2F, 
    inst_add_28_2F, 
    inst_add_28_2F, 
    inst_add_28_2F, 
    inst_add_28_2F, 
    inst_add_28_2F, 
    inst_jnb, 
    inst_acall, 
    inst_reti, 
    inst_rlc, 
    inst_addc_34, 
    inst_addc_35, 
    inst_addc_36, 
    inst_addc_37, 
    inst_addc_38_3F, 
    inst_addc_38_3F, 
    inst_addc_38_3F, 
    inst_addc_38_3F, 
    inst_addc_38_3F, 
    inst_addc_38_3F, 
    inst_addc_38_3F, 
    inst_addc_38_3F, 
    inst_jc, 
    inst_ajmp, 
    inst_orl_42, 
    inst_orl_43, 
    inst_orl_44, 
    inst_orl_45, 
    inst_orl_46, 
    inst_orl_47, 
    inst_orl_48_4F, 
    inst_orl_48_4F, 
    inst_orl_48_4F, 
    inst_orl_48_4F, 
    inst_orl_48_4F, 
    inst_orl_48_4F, 
    inst_orl_48_4F, 
    inst_orl_48_4F, 
    inst_jnc, 
    inst_acall, 
    inst_anl_52, 
    inst_anl_53, 
    inst_anl_54, 
    inst_anl_55, 
    inst_anl_56, 
    inst_anl_57, 
    inst_anl_58_5F, 
    inst_anl_58_5F, 
    inst_anl_58_5F, 
    inst_anl_58_5F, 
    inst_anl_58_5F, 
    inst_anl_58_5F, 
    inst_anl_58_5F, 
    inst_anl_58_5F, 
    inst_jz, 
    inst_ajmp, 
    inst_xrl_62, 
    inst_xrl_63, 
    inst_xrl_64, 
    inst_xrl_65, 
    inst_xrl_66, 
    inst_xrl_67, 
    inst_xrl_68_6F, 
    inst_xrl_68_6F, 
    inst_xrl_68_6F, 
    inst_xrl_68_6F, 
    inst_xrl_68_6F, 
    inst_xrl_68_6F, 
    inst_xrl_68_6F, 
    inst_xrl_68_6F, 
    inst_jnz, 
    inst_acall, 
    inst_orl_72, 
    inst_jmp, 
    inst_mov_74, 
    inst_mov_75, 
    inst_mov_76, 
    inst_mov_77, 
    inst_mov_78_7F, 
    inst_mov_78_7F, 
    inst_mov_78_7F, 
    inst_mov_78_7F, 
    inst_mov_78_7F, 
    inst_mov_78_7F, 
    inst_mov_78_7F, 
    inst_mov_78_7F, 
    inst_sjmp, 
    inst_ajmp, 
    inst_anl_82, 
    inst_movc_83, 
    inst_div, 
    inst_mov_85, 
    inst_mov_86, 
    inst_mov_87, 
    inst_mov_88_8F, 
    inst_mov_88_8F, 
    inst_mov_88_8F, 
    inst_mov_88_8F, 
    inst_mov_88_8F, 
    inst_mov_88_8F, 
    inst_mov_88_8F, 
    inst_mov_88_8F, 
    inst_mov_90, 
    inst_acall, 
    inst_mov_92, 
    inst_movc_93, 
    inst_subb_94, 
    inst_subb_95, 
    inst_subb_96, 
    inst_subb_97, 
    inst_subb_98_9F, 
    inst_subb_98_9F, 
    inst_subb_98_9F, 
    inst_subb_98_9F, 
    inst_subb_98_9F, 
    inst_subb_98_9F, 
    inst_subb_98_9F, 
    inst_subb_98_9F, 
    inst_orl_A0, 
    inst_ajmp, 
    inst_mov_A2, 
    inst_inc_A3, 
    inst_mul, 
    inst_undef, 
    inst_mov_A6, 
    inst_mov_A7, 
    inst_mov_A8_AF, 
    inst_mov_A8_AF, 
    inst_mov_A8_AF, 
    inst_mov_A8_AF, 
    inst_mov_A8_AF, 
    inst_mov_A8_AF, 
    inst_mov_A8_AF, 
    inst_mov_A8_AF, 
    inst_anl_B0, 
    inst_acall, 
    inst_cpl_B2, 
    inst_cpl_B3, 
    inst_cjne_B4, 
    inst_cjne_B5, 
    inst_cjne_B6, 
    inst_cjne_B7, 
    inst_cjne_B8_BF, 
    inst_cjne_B8_BF, 
    inst_cjne_B8_BF, 
    inst_cjne_B8_BF, 
    inst_cjne_B8_BF, 
    inst_cjne_B8_BF, 
    inst_cjne_B8_BF, 
    inst_cjne_B8_BF, 
    inst_push, 
    inst_ajmp, 
    inst_clr_C2, 
    inst_clr_C3, 
    inst_swap, 
    inst_xch_C5, 
    inst_xch_C6, 
    inst_xch_C7, 
    inst_xch_C8_CF, 
    inst_xch_C8_CF, 
    inst_xch_C8_CF, 
    inst_xch_C8_CF, 
    inst_xch_C8_CF, 
    inst_xch_C8_CF, 
    inst_xch_C8_CF, 
    inst_xch_C8_CF, 
    inst_pop, 
    inst_acall, 
    inst_setb_D2, 
    inst_setb_D3, 
    inst_da, 
    inst_djnz_D5, 
    inst_xchd, 
    inst_xchd, 
    inst_djnz_D8_DF, 
    inst_djnz_D8_DF, 
    inst_djnz_D8_DF, 
    inst_djnz_D8_DF, 
    inst_djnz_D8_DF, 
    inst_djnz_D8_DF, 
    inst_djnz_D8_DF, 
    inst_djnz_D8_DF, 
    inst_movx_E0, 
    inst_ajmp, 
    inst_movx_E2, 
    inst_movx_E3, 
    inst_clr_E4, 
    inst_mov_E5, 
    inst_mov_E6, 
    inst_mov_E7, 
    inst_mov_E8_EF, 
    inst_mov_E8_EF, 
    inst_mov_E8_EF, 
    inst_mov_E8_EF, 
    inst_mov_E8_EF, 
    inst_mov_E8_EF, 
    inst_mov_E8_EF, 
    inst_mov_E8_EF, 
    inst_movx_F0, 
    inst_acall, 
    inst_movx_F2, 
    inst_movx_F3, 
    inst_cpl_F4, 
    inst_mov_F5, 
    inst_mov_F6, 
    inst_mov_F7, 
    inst_mov_F8_FF, 
    inst_mov_F8_FF, 
    inst_mov_F8_FF, 
    inst_mov_F8_FF, 
    inst_mov_F8_FF, 
    inst_mov_F8_FF, 
    inst_mov_F8_FF, 
    inst_mov_F8_FF,
]

#---- for testing -------------------------------------------------------------
if __name__ == '__main__':    
    #temp()
    for f in inst_handler:
        print f
