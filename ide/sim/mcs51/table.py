from define import *

addr_sfr = {
    0x00:'r0',
    0x01:'r1',
    0x02:'r2',
    0x03:'r3',
    0x04:'r4',
    0x05:'r5',
    0x06:'r6',
    0x07:'r7',
    0x80:'P0',
    0x81:'SP',
    0x82:'DPL',
    0x83:'DPH',
    0x87:'PCON',
    0x88:'TCON',
    0x89:'TMOD',
    0x8a:'TL0',
    0x8b:'TL1',
    0x8c:'TH0',
    0x8d:'TH1',
    0x90:'P1',
    0x98:'SCON',
    0x99:'SBUF',
    0xa0:'P2',
    0xa8:'IE',
    0xb0:'P3',
    0xb8:'IP',
    0xd0:'PSW',
    0xe0:'ACC',
    0xf0:'B',    
}

bit_addr_map = {
    0x80: 'P0_0',
    0x81: 'P0_1',
    0x82: 'P0_2',
    0x83: 'P0_3',
    0x84: 'P0_4',
    0x85: 'P0_5',
    0x86: 'P0_6',
    0x87: 'P0_7',
    0x88: 'IT0',
    0x89: 'IE0',
    0x8A: 'IT1',
    0x8B: 'IE1',
    0x8C: 'TR0',
    0x8D: 'TF0',
    0x8E: 'TR1',
    0x8F: 'TF1',
    0x90: 'P1_0',
    0x91: 'P1_1',
    0x92: 'P1_2',
    0x93: 'P1_3',
    0x94: 'P1_4',
    0x95: 'P1_5',
    0x96: 'P1_6',
    0x97: 'P1_7',
    0x98: 'RI',
    0x99: 'TI',
    0x9A: 'RB8',
    0x9B: 'TB8',
    0x9C: 'REN',
    0x9D: 'SM2',
    0x9E: 'SM1',
    0x9F: 'SM0',
    0xA0: 'P2_0',
    0xA1: 'P2_1',
    0xA2: 'P2_2',
    0xA3: 'P2_3',
    0xA4: 'P2_4',
    0xA5: 'P2_5',
    0xA6: 'P2_6',
    0xA7: 'P2_7',
    0xA8: 'EX0',
    0xA9: 'ET0',
    0xAA: 'EX1',
    0xAB: 'ET1',
    0xAC: 'ES',
    0xAF: 'EA',
    0xB0: 'P3_0',
    0xB1: 'P3_1',
    0xB2: 'P3_2',
    0xB3: 'P3_3',
    0xB4: 'P3_4',
    0xB5: 'P3_5',
    0xB6: 'P3_6',
    0xB7: 'P3_7',
    0xB0: 'RXD',
    0xB1: 'TXD',
    0xB2: 'INT0',
    0xB3: 'INT1',
    0xB4: 'T0',
    0xB5: 'T1',
    0xB6: 'WR',
    0xB7: 'RD',
    0xB8: 'PX0',
    0xB9: 'PT0',
    0xBA: 'PX1',
    0xBB: 'PT1',
    0xBC: 'PS',
    0xD0: 'P',
    0xD1: 'F1',
    0xD2: 'OV',
    0xD3: 'RS0',
    0xD4: 'RS1',
    0xD5: 'F0',
    0xD6: 'AC',
    0xD7: 'CY',
    0xF0: 'B_0',
    0xF1: 'B_1',
    0xF2: 'B_2',
    0xF3: 'B_3',
    0xF4: 'B_4',
    0xF5: 'B_5',
    0xF6: 'B_6',
    0xF7: 'B_7',
}

sfr_map = {
        'r0':0,'r1':1,'r2':2,'r3':3,'r4':4,'r5':5,'r6':6,'r7':7,
        'P0':   0x80,
        'P1':   0x90,
        'P2':   0xa0,
        'P3':   0xb0,
        'SP':   0x81,
        'DPL':  0x82,
        'DPH':  0x83,
        'PCON': 0x87,
        'TCON': 0x88,
        'TMOD': 0x89,
        'TL0':  0x8a,
        'TL1':  0x8b,
        'TH0':  0x8c,
        'TH1':  0x8d,
        'SCON': 0x98,
        'SBUF': 0x99,
        'IE':   0xa8,
        'IP':   0xb8,
        'PSW':  0xd0,
        'ACC':  0xe0,
        'B':    0xf0,
    }

symbol_str = {
    I_ACALL:"acall", # Absolute Call
    I_ADD:  "add  ", # Add Accumulator
    I_ADDC: "addc ", # Add Accumulator with Carry
    I_AJMP: "ajmp ", # Absolute Jump
    I_ANL:  "anl  ", # Bitwise AND
    I_CJNE: "cjne ", # Compare and Jump if Not Equal
    I_CLR:  "clr  ", # Clear Register
    I_CPL:  "cpl  ", # Complement Register
    I_DA:   "da   ", # Decimal Adjust
    I_DEC:  "dec  ", # Decrement Register
    I_DIV:  "div  ", # Divide Accumulator by B
    I_DJNZ: "djnz ", # Decrement Register and Jump if Not Zero
    I_INC:  "inc  ", # Increment Register
    I_JB:   "jb   ", # Jump if Bit Set
    I_JBC:  "jbc  ", # Jump if Bit Set and Clear Bit
    I_JC:   "jc   ", # Jump if Carry Set
    I_JMP:  "jmp  ", # Jump to Address
    I_JNB:  "jnb  ", # Jump if Bit Not Set
    I_JNC:  "jnc  ", # Jump if Carry Not Set
    I_JNZ:  "jnz  ", # Jump if Accumulator Not Zero
    I_JZ:   "jz   ", # Jump if Accumulator Zero
    I_LCALL:"lcall", # Long Call
    I_LJMP: "ljmp ", # Long Jump
    I_MOV:  "mov  ", # Move Memory
    I_MOVC: "movc ", # Move Code Memory
    I_MOVX: "movx ", # Move Ext#ended Memory
    I_MUL:  "mul  ", # Multiply Accumulator by B
    I_NOP:  "nop  ", # No Operation
    I_ORL:  "orl  ", # Bitwise OR
    I_POP:  "pop  ", # Pop Value From Stack
    I_PUSH: "push ", # Push Value Onto Stack
    I_RET:  "ret  ", # Return From Subroutine
    I_RETI: "reti ", # Return From Interrupt
    I_RL:   "rl   ", # Rotate Accumulator Left
    I_RLC:  "rlc  ", # Rotate Accumulator Left Through Carry
    I_RR:   "rr   ", # Rotate Accumulator Right
    I_RRC:  "rrc  ", # Rotate Accumulator Right Through Carry
    I_SETB: "setb ", # Set Bit
    I_SJMP: "sjmp ", # Short Jump
    I_SUBB: "subb ", # Subtract From Accumulator With Borrow
    I_SWAP: "swap ", # Swap Accumulator Nibbles
    I_XCH:  "xch  ", # Exchange Bytes
    I_XCHD: "xchd ", # Exchange Digits
    I_XRL:  "xrl  ", # Bitwise Exclusive OR
    I_UNDEF:"undef", # Undefined Instruction
}

op_str =  {
    OP_A: "a",
    OP_B: "b",
    OP_C: "c",
    OP_DATA: "#op",
    OP_IRAM: "op",
    OP_DPTR: "dptr",
    OP_BITADDR: "op",
    OP_RELADDR: "op",
    OP_R0: "r0",
    OP_R1: "r1",
    OP_R2: "r2",
    OP_R3: "r3",
    OP_R4: "r4",
    OP_R5: "r5",
    OP_R6: "r6",
    OP_R7: "r7",
    OP_ATR0: "@r0",
    OP_ATR1: "@r1",
    OP_ATA: "@a",
    OP_ATDPTR: "@dptr",
    OP_PC: "pc",
    OP_CODE: "op",
    OP_ADDR: "op",
    OP_PAGE: "op",
}

symbol_map = [I_NOP, 
I_NOP,   I_AJMP,  I_LJMP,  I_RR,    I_INC,   I_INC,   I_INC,   I_INC,   I_INC,   I_INC,   I_INC,   I_INC,   I_INC,   I_INC,   I_INC,   I_INC,
I_JBC,   I_ACALL, I_LCALL, I_RRC,   I_DEC,   I_DEC,   I_DEC,   I_DEC,   I_DEC,   I_DEC,   I_DEC,   I_DEC,   I_DEC,   I_DEC,   I_DEC,   I_DEC,  
I_JB,    I_AJMP,  I_RET,   I_RL,    I_ADD,   I_ADD,   I_ADD,   I_ADD,   I_ADD,   I_ADD,   I_ADD,   I_ADD,   I_ADD,   I_ADD,   I_ADD,   I_ADD,   
I_JNB,   I_ACALL, I_RETI,  I_RLC,   I_ADDC,  I_ADDC,  I_ADDC,  I_ADDC,  I_ADDC,  I_ADDC,  I_ADDC,  I_ADDC,  I_ADDC,  I_ADDC,  I_ADDC,  I_ADDC, 
 
I_JC,    I_AJMP,  I_ORL,   I_ORL,   I_ORL,   I_ORL,   I_ORL,   I_ORL,   I_ORL,   I_ORL,   I_ORL,   I_ORL,   I_ORL,   I_ORL,   I_ORL,   I_ORL,   
I_JNC,   I_ACALL, I_ANL,   I_ANL,   I_ANL,   I_ANL,   I_ANL,   I_ANL,   I_ANL,   I_ANL,   I_ANL,   I_ANL,   I_ANL,   I_ANL,   I_ANL,   I_ANL,   
I_JZ,    I_AJMP,  I_XRL,   I_XRL,   I_XRL,   I_XRL,   I_XRL,   I_XRL,   I_XRL,   I_XRL,   I_XRL,   I_XRL,   I_XRL,   I_XRL,   I_XRL,   I_XRL,   
I_JNZ,   I_ACALL, I_ORL,   I_JMP,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV, 
  
I_SJMP,  I_AJMP,  I_ANL,   I_MOVC,  I_DIV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   
I_MOV,   I_ACALL, I_MOV,   I_MOVC,  I_SUBB,  I_SUBB,  I_SUBB,  I_SUBB,  I_SUBB,  I_SUBB,  I_SUBB,  I_SUBB,  I_SUBB,  I_SUBB,  I_SUBB,  I_SUBB,  
I_ORL,   I_AJMP,  I_MOV,   I_INC,   I_MUL,   I_UNDEF, I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   
I_ANL,   I_ACALL, I_CPL,   I_CPL,   I_CJNE,  I_CJNE,  I_CJNE,  I_CJNE,  I_CJNE,  I_CJNE,  I_CJNE,  I_CJNE,  I_CJNE,  I_CJNE,  I_CJNE,  I_CJNE,  

I_PUSH,  I_AJMP,  I_CLR,   I_CLR,   I_SWAP,  I_XCH,   I_XCH,   I_XCH,   I_XCH,   I_XCH,   I_XCH,   I_XCH,   I_XCH,   I_XCH,   I_XCH,   I_XCH,  
I_POP,   I_ACALL, I_SETB,  I_SETB,  I_DA,    I_DJNZ,  I_XCHD,  I_XCHD,  I_DJNZ,  I_DJNZ,  I_DJNZ,  I_DJNZ,  I_DJNZ,  I_DJNZ,  I_DJNZ,  I_DJNZ,  
I_MOVX,  I_AJMP,  I_MOVX,  I_MOVX,  I_CLR,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   
I_MOVX,  I_ACALL, I_MOVX,  I_MOVX,  I_CPL,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   I_MOV,   
]

symbol_table = [
    # ACALL
    [0x11, 2, I_ACALL, [OP_PAGE], FLAG_NONE, "ACALL page0, op1"],
    [0x31, 2, I_ACALL, [OP_PAGE], FLAG_NONE, "ACALL page1, op1"],
    [0x51, 2, I_ACALL, [OP_PAGE], FLAG_NONE, "ACALL page2, op1"],
    [0x71, 2, I_ACALL, [OP_PAGE], FLAG_NONE, "ACALL page3, op1"],
    [0x91, 2, I_ACALL, [OP_PAGE], FLAG_NONE, "ACALL page4, op1"],
    [0xB1, 2, I_ACALL, [OP_PAGE], FLAG_NONE, "ACALL page5, op1"],
    [0xD1, 2, I_ACALL, [OP_PAGE], FLAG_NONE, "ACALL page6, op1"],
    [0xF1, 2, I_ACALL, [OP_PAGE], FLAG_NONE, "ACALL page7, op1"],

    # ADD, ADD A,operand
    [0x24, 2, I_ADD, [OP_A, OP_DATA], FLAG_C_AC_OV, "ADD A,#data"], 
    [0x25, 2, I_ADD, [OP_A, OP_IRAM], FLAG_C_AC_OV, "ADD A,iram_addr"], 
    [0x26, 1, I_ADD, [OP_A, OP_ATR0], FLAG_C_AC_OV, "ADD A,@R0"], 
    [0x27, 1, I_ADD, [OP_A, OP_ATR1], FLAG_C_AC_OV, "ADD A,@R1"],
    [0x28, 1, I_ADD, [OP_A, OP_R0],   FLAG_C_AC_OV, "ADD A,R0"],
    [0x29, 1, I_ADD, [OP_A, OP_R1],   FLAG_C_AC_OV, "ADD A,R1"], 
    [0x2A, 1, I_ADD, [OP_A, OP_R2],   FLAG_C_AC_OV, "ADD A,R2"], 
    [0x2B, 1, I_ADD, [OP_A, OP_R3],   FLAG_C_AC_OV, "ADD A,R3"], 
    [0x2C, 1, I_ADD, [OP_A, OP_R4],   FLAG_C_AC_OV, "ADD A,R4"], 
    [0x2D, 1, I_ADD, [OP_A, OP_R5],   FLAG_C_AC_OV, "ADD A,R5"], 
    [0x2E, 1, I_ADD, [OP_A, OP_R6],   FLAG_C_AC_OV, "ADD A,R6"], 
    [0x2F, 1, I_ADD, [OP_A, OP_R7],   FLAG_C_AC_OV, "ADD A,R7"], 

    # ADDC
    [0x34, 2, I_ADDC, [OP_A, OP_DATA], FLAG_C_AC_OV, "ADDC A,#data"], 
    [0x35, 2, I_ADDC, [OP_A, OP_IRAM], FLAG_C_AC_OV, "ADDC A,iram_addr"], 
    [0x36, 1, I_ADDC, [OP_A, OP_ATR0], FLAG_C_AC_OV, "ADDC A,@R0"], 
    [0x37, 1, I_ADDC, [OP_A, OP_ATR1], FLAG_C_AC_OV, "ADDC A,@R1"], 
    [0x38, 1, I_ADDC, [OP_A, OP_R0],   FLAG_C_AC_OV, "ADDC A,R0"], 
    [0x39, 1, I_ADDC, [OP_A, OP_R1],   FLAG_C_AC_OV, "ADDC A,R1"], 
    [0x3A, 1, I_ADDC, [OP_A, OP_R2],   FLAG_C_AC_OV, "ADDC A,R2"], 
    [0x3B, 1, I_ADDC, [OP_A, OP_R3],   FLAG_C_AC_OV, "ADDC A,R3"], 
    [0x3C, 1, I_ADDC, [OP_A, OP_R4],   FLAG_C_AC_OV, "ADDC A,R4"], 
    [0x3D, 1, I_ADDC, [OP_A, OP_R5],   FLAG_C_AC_OV, "ADDC A,R5"], 
    [0x3E, 1, I_ADDC, [OP_A, OP_R6],   FLAG_C_AC_OV, "ADDC A,R6"], 
    [0x3F, 1, I_ADDC, [OP_A, OP_R7],   FLAG_C_AC_OV, "ADDC A,R7"], 

    # AJMP, AJMP code address
    [0x01, 2, I_AJMP, [OP_PAGE], FLAG_NONE, "AJMP page0, op1"], 
    [0x21, 2, I_AJMP, [OP_PAGE], FLAG_NONE, "AJMP page1, op1"], 
    [0x41, 2, I_AJMP, [OP_PAGE], FLAG_NONE, "AJMP page2, op1"], 
    [0x61, 2, I_AJMP, [OP_PAGE], FLAG_NONE, "AJMP page3, op1"], 
    [0x81, 2, I_AJMP, [OP_PAGE], FLAG_NONE, "AJMP page4, op1"], 
    [0xA1, 2, I_AJMP, [OP_PAGE], FLAG_NONE, "AJMP page5, op1"], 
    [0xC1, 2, I_AJMP, [OP_PAGE], FLAG_NONE, "AJMP page6, op1"], 
    [0xE1, 2, I_AJMP, [OP_PAGE], FLAG_NONE, "AJMP page7, op1"], 

    # ANL, Bitwise AND, ANL operand1, operand2
    [0x52, 2, I_ANL, [OP_A,    OP_IRAM], FLAG_NONE, "ANL iram_addr,A"],   
    [0x53, 3, I_ANL, [OP_IRAM, OP_DATA], FLAG_NONE, "ANL iram_addr,#data"], 
    [0x54, 2, I_ANL, [OP_A,    OP_DATA], FLAG_NONE, "ANL A,#data"],       
    [0x55, 2, I_ANL, [OP_A,    OP_IRAM], FLAG_NONE, "ANL A,iram_addr"],   
    [0x56, 1, I_ANL, [OP_A,    OP_ATR0], FLAG_NONE, "ANL A,@R0"],         
    [0x57, 1, I_ANL, [OP_A,    OP_ATR1], FLAG_NONE, "ANL A,@R1"],         
    [0x58, 1, I_ANL, [OP_A,    OP_R0],   FLAG_NONE, "ANL A,R0"],          
    [0x59, 1, I_ANL, [OP_A,    OP_R1],   FLAG_NONE, "ANL A,R1"],          
    [0x5A, 1, I_ANL, [OP_A,    OP_R2],   FLAG_NONE, "ANL A,R2"],          
    [0x5B, 1, I_ANL, [OP_A,    OP_R3],   FLAG_NONE, "ANL A,R3"],          
    [0x5C, 1, I_ANL, [OP_A,    OP_R4],   FLAG_NONE, "ANL A,R4"],          
    [0x5D, 1, I_ANL, [OP_A,    OP_R5],   FLAG_NONE, "ANL A,R5"],          
    [0x5E, 1, I_ANL, [OP_A,    OP_R6],   FLAG_NONE, "ANL A,R6"],          
    [0x5F, 1, I_ANL, [OP_A,    OP_R7],   FLAG_NONE, "ANL A,R7"],          
    [0x82, 2, I_ANL, [OP_C,    OP_BITADDR],   FLAG_C, "ANL C,bit_addr"],  
    [0xB0, 2, I_ANL, [OP_C,    OP_BITADDR],   FLAG_C, "ANL C,/bit_addr"], 

    # CJNE
    # Compare and Jump If Not Equal
    # Syntax: CJNE operand1,operand2,reladdr
    [0xB4, 3, I_CJNE, [OP_A,    OP_DATA, OP_RELADDR], FLAG_C, "CJNE A,#data,reladdr"],
    [0xB5, 3, I_CJNE, [OP_A,    OP_IRAM, OP_RELADDR], FLAG_C, "CJNE A,iram_addr,reladdr"], 
    [0xB6, 3, I_CJNE, [OP_ATR0, OP_DATA, OP_RELADDR], FLAG_C, "CJNE @R0,#data,reladdr"], 
    [0xB7, 3, I_CJNE, [OP_ATR1, OP_DATA, OP_RELADDR], FLAG_C, "CJNE @R1,#data,reladdr"], 
    [0xB8, 3, I_CJNE, [OP_R0,   OP_DATA, OP_RELADDR], FLAG_C, "CJNE R0,#data,reladdr"], 
    [0xB9, 3, I_CJNE, [OP_R1,   OP_DATA, OP_RELADDR], FLAG_C, "CJNE R1,#data,reladdr"], 
    [0xBA, 3, I_CJNE, [OP_R2,   OP_DATA, OP_RELADDR], FLAG_C, "CJNE R2,#data,reladdr"], 
    [0xBB, 3, I_CJNE, [OP_R3,   OP_DATA, OP_RELADDR], FLAG_C, "CJNE R3,#data,reladdr"], 
    [0xBC, 3, I_CJNE, [OP_R4,   OP_DATA, OP_RELADDR], FLAG_C, "CJNE R4,#data,reladdr"], 
    [0xBD, 3, I_CJNE, [OP_R5,   OP_DATA, OP_RELADDR], FLAG_C, "CJNE R5,#data,reladdr"], 
    [0xBE, 3, I_CJNE, [OP_R6,   OP_DATA, OP_RELADDR], FLAG_C, "CJNE R6,#data,reladdr"], 
    [0xBF, 3, I_CJNE, [OP_R7,   OP_DATA, OP_RELADDR], FLAG_C, "CJNE R7,#data,reladdr"], 

    # CLR : Clear Register
    # Syntax: CLR register
    [0xC2, 2, I_CLR, [OP_BITADDR], FLAG_NONE, "CLR bit_addr"], 
    [0xC3, 1, I_CLR, [OP_C],       FLAG_C,    "CLR C"], 
    [0xE4, 1, I_CLR, [OP_A],       FLAG_NONE, "CLR A"], 

    # CPL : Complement Register
    # Syntax: CPL operand
    [0xF4, 1, I_CPL, [OP_A],       FLAG_NONE, "CPL A"], 
    [0xB3, 1, I_CPL, [OP_C],       FLAG_C,    "CPL C"], 
    [0xB2, 2, I_CPL, [OP_BITADDR], FLAG_NONE, "CPL bit_addr"], 

    # DA : Decimal Adjust Accumulator
    # Syntax: DA A
    [0xD4, 1, I_DA, [OP_A], FLAG_C, "DA 0xD4 1 C"],

    # DEC : Decrement Register
    # Syntax: DEC register
    [0x14, 1, I_DEC, [OP_A],    FLAG_NONE, "DEC A"],
    [0x15, 2, I_DEC, [OP_IRAM], FLAG_NONE, "DEC iram_addr"], 
    [0x16, 1, I_DEC, [OP_ATR0], FLAG_NONE, "DEC @R0"], 
    [0x17, 1, I_DEC, [OP_ATR1], FLAG_NONE, "DEC @R1"],
    [0x18, 1, I_DEC, [OP_R0], FLAG_NONE, "DEC R0"], 
    [0x19, 1, I_DEC, [OP_R1], FLAG_NONE, "DEC R1"], 
    [0x1A, 1, I_DEC, [OP_R2], FLAG_NONE, "DEC R2"], 
    [0x1B, 1, I_DEC, [OP_R3], FLAG_NONE, "DEC R3"], 
    [0x1C, 1, I_DEC, [OP_R4], FLAG_NONE, "DEC R4"], 
    [0x1D, 1, I_DEC, [OP_R5], FLAG_NONE, "DEC R5"], 
    [0x1E, 1, I_DEC, [OP_R6], FLAG_NONE, "DEC R6"], 
    [0x1F, 1, I_DEC, [OP_R7], FLAG_NONE, "DEC R7"], 

    # DIV   : Divide Accumulator by B
    # Syntax: DIV AB
    [0x84, 1, I_DIV, [OP_A, OP_B], FLAG_OV, "DIV AB 0x84 1 C, OV"],

    # DJNZ  : Decrement and Jump if Not Zero
    # Syntax: DJNZ register,reladdr
    [0xD5, 3, I_DJNZ, [OP_IRAM, OP_RELADDR], FLAG_NONE, "DJNZ iram_addr,reladdr"], 
    [0xD8, 2, I_DJNZ, [OP_R0,   OP_RELADDR], FLAG_NONE, "DJNZ R0,reladdr"], 
    [0xD9, 2, I_DJNZ, [OP_R1,   OP_RELADDR], FLAG_NONE, "DJNZ R1,reladdr"], 
    [0xDA, 2, I_DJNZ, [OP_R2,   OP_RELADDR], FLAG_NONE, "DJNZ R2,reladdr"], 
    [0xDB, 2, I_DJNZ, [OP_R3,   OP_RELADDR], FLAG_NONE, "DJNZ R3,reladdr"], 
    [0xDC, 2, I_DJNZ, [OP_R4,   OP_RELADDR], FLAG_NONE, "DJNZ R4,reladdr"], 
    [0xDD, 2, I_DJNZ, [OP_R5,   OP_RELADDR], FLAG_NONE, "DJNZ R5,reladdr"], 
    [0xDE, 2, I_DJNZ, [OP_R6,   OP_RELADDR], FLAG_NONE, "DJNZ R6,reladdr"], 
    [0xDF, 2, I_DJNZ, [OP_R7,   OP_RELADDR], FLAG_NONE, "DJNZ R7,reladdr"], 


    # INC   : Increment Register
    # Syntax: INC register
    [0x04, 1, I_INC, [OP_A],    FLAG_NONE, "INC A"], 
    [0x05, 2, I_INC, [OP_IRAM], FLAG_NONE, "INC iram_addr"], 
    [0x06, 1, I_INC, [OP_ATR0], FLAG_NONE, "INC @R0"], 
    [0x07, 1, I_INC, [OP_ATR1], FLAG_NONE, "INC @R1"], 
    [0x08, 1, I_INC, [OP_R0], FLAG_NONE, "INC R0"],
    [0x09, 1, I_INC, [OP_R1], FLAG_NONE, "INC R1"], 
    [0x0A, 1, I_INC, [OP_R2], FLAG_NONE, "INC R2"], 
    [0x0B, 1, I_INC, [OP_R3], FLAG_NONE, "INC R3"], 
    [0x0C, 1, I_INC, [OP_R4], FLAG_NONE, "INC R4"], 
    [0x0D, 1, I_INC, [OP_R5], FLAG_NONE, "INC R5"], 
    [0x0E, 1, I_INC, [OP_R6], FLAG_NONE, "INC R6"], 
    [0x0F, 1, I_INC, [OP_R7], FLAG_NONE, "INC R7"], 
    [0xA3, 1, I_INC, [OP_DPTR], FLAG_NONE, "INC DPTR"], 

    # JB    : Jump if Bit Set
    # Syntax: JB bit addr, reladdr
    [0x20, 3, I_JB, [OP_BITADDR, OP_RELADDR], FLAG_NONE, "JB bit_addr,reladdr"], 

    # JBC   : Jump if Bit Set and Clear Bit
    # Syntax: JB bit addr, reladdr
    [0x10, 3, I_JBC, [OP_BITADDR, OP_RELADDR], FLAG_NONE, "JBC bit_addr,reladdr"], 

    # JC
    # Function: Jump if Carry Set
    # Syntax: JC reladdr
    [0x40, 2, I_JC, [OP_RELADDR], FLAG_NONE, "JC reladdr"], 

    # JMP
    # Function: Jump to Data Pointer + Accumulator
    # Syntax: JMP @A+DPTR
    [0x73, 1, I_JMP, [OP_ATA, OP_DPTR], FLAG_NONE, "JMP @A+DPTR"], 

    # JNB
    # Function: Jump if Bit Not Set
    # Syntax: JNB bit addr,reladdr
    [0x30, 3, I_JNB, [OP_BITADDR, OP_RELADDR], FLAG_NONE, "JNB bit_addr,reladdr"], 

    # JNC
    # Function: Jump if Carry Not Set
    # Syntax: JNC reladdr
    [0x50, 2, I_JNC, [OP_RELADDR], FLAG_NONE, "JNC reladdr"], 

    # JNZ
    # Function: Jump if Accumulator Not Zero
    # Syntax: JNZ reladdr
    [0x70, 2, I_JNZ, [OP_RELADDR], FLAG_NONE, "JNZ reladdr"], 

    # JZ    : Jump if Accumulator Zero
    # Syntax: JNZ reladdr
    [0x60, 2, I_JZ, [OP_RELADDR], FLAG_NONE, "JZ reladdr"], 

    # LCALL
    # Function: Long Call
    # Syntax: LCALL code addr
    [0x12, 3, I_LCALL, [OP_CODE, OP_ADDR], FLAG_NONE, "LCALL code_addr"], 

    # LJMP
    # Function: Long Jump
    # Syntax: LJMP code addr
    [0x02, 3, I_LJMP, [OP_CODE, OP_ADDR], FLAG_NONE, "LJMP code_addr"], 

    # MOV
    # Function: Move Memory
    # Syntax: MOV operand1,operand2
    [0x76, 2, I_MOV, [OP_ATR0, OP_DATA], FLAG_NONE, "MOV @R0,#data"], 
    [0x77, 2, I_MOV, [OP_ATR1, OP_DATA], FLAG_NONE, "MOV @R1,#data"], 
    [0xF6, 1, I_MOV, [OP_ATR0, OP_A], FLAG_NONE, "MOV @R0,A"], 
    [0xF7, 1, I_MOV, [OP_ATR1, OP_A], FLAG_NONE, "MOV @R1,A"], 
    [0xA6, 2, I_MOV, [OP_ATR0, OP_IRAM], FLAG_NONE, "MOV @R0,iram_addr"], 
    [0xA7, 2, I_MOV, [OP_ATR1, OP_IRAM], FLAG_NONE, "MOV @R1,iram_addr"], 
    [0x74, 2, I_MOV, [OP_A, OP_DATA], FLAG_NONE, "MOV A,#data"], 
    [0xE6, 1, I_MOV, [OP_A, OP_ATR0], FLAG_NONE, "MOV A,@R0"], 
    [0xE7, 1, I_MOV, [OP_A, OP_ATR1], FLAG_NONE, "MOV A,@R1"], 
    [0xE8, 1, I_MOV, [OP_A, OP_R0], FLAG_NONE, "MOV A,R0"], 
    [0xE9, 1, I_MOV, [OP_A, OP_R1], FLAG_NONE, "MOV A,R1"], 
    [0xEA, 1, I_MOV, [OP_A, OP_R2], FLAG_NONE, "MOV A,R2"], 
    [0xEB, 1, I_MOV, [OP_A, OP_R3], FLAG_NONE, "MOV A,R3"], 
    [0xEC, 1, I_MOV, [OP_A, OP_R4], FLAG_NONE, "MOV A,R4"], 
    [0xED, 1, I_MOV, [OP_A, OP_R5], FLAG_NONE, "MOV A,R5"], 
    [0xEE, 1, I_MOV, [OP_A, OP_R6], FLAG_NONE, "MOV A,R6"], 
    [0xEF, 1, I_MOV, [OP_A, OP_R7], FLAG_NONE, "MOV A,R7"], 
    [0xE5, 2, I_MOV, [OP_A, OP_IRAM], FLAG_NONE, "MOV A,iram_addr"], 
    [0xA2, 2, I_MOV, [OP_C, OP_BITADDR], FLAG_C, "MOV C,bit_addr"], 
    [0x90, 3, I_MOV, [OP_DPTR, OP_DATA, OP_DATA], FLAG_NONE, "MOV DPTR,#data16"], 
    [0x78, 2, I_MOV, [OP_R0, OP_DATA], FLAG_NONE, "MOV R0,#data"], 
    [0x79, 2, I_MOV, [OP_R1, OP_DATA], FLAG_NONE, "MOV R1,#data"], 
    [0x7A, 2, I_MOV, [OP_R2, OP_DATA], FLAG_NONE, "MOV R2,#data"], 
    [0x7B, 2, I_MOV, [OP_R3, OP_DATA], FLAG_NONE, "MOV R3,#data"], 
    [0x7C, 2, I_MOV, [OP_R4, OP_DATA], FLAG_NONE, "MOV R4,#data"], 
    [0x7D, 2, I_MOV, [OP_R5, OP_DATA], FLAG_NONE, "MOV R5,#data"], 
    [0x7E, 2, I_MOV, [OP_R6, OP_DATA], FLAG_NONE, "MOV R6,#data"], 
    [0x7F, 2, I_MOV, [OP_R7, OP_DATA], FLAG_NONE, "MOV R7,#data"], 
    [0xF8, 1, I_MOV, [OP_R0, OP_A], FLAG_NONE, "MOV R0,A"], 
    [0xF9, 1, I_MOV, [OP_R1, OP_A], FLAG_NONE, "MOV R1,A"], 
    [0xFA, 1, I_MOV, [OP_R2, OP_A], FLAG_NONE, "MOV R2,A"], 
    [0xFB, 1, I_MOV, [OP_R3, OP_A], FLAG_NONE, "MOV R3,A"], 
    [0xFC, 1, I_MOV, [OP_R4, OP_A], FLAG_NONE, "MOV R4,A"], 
    [0xFD, 1, I_MOV, [OP_R5, OP_A], FLAG_NONE, "MOV R5,A"], 
    [0xFE, 1, I_MOV, [OP_R6, OP_A], FLAG_NONE, "MOV R6,A"], 
    [0xFF, 1, I_MOV, [OP_R7, OP_A], FLAG_NONE, "MOV R7,A"], 
    [0xA8, 2, I_MOV, [OP_R0, OP_IRAM], FLAG_NONE, "MOV R0,iram_addr"], 
    [0xA9, 2, I_MOV, [OP_R1, OP_IRAM], FLAG_NONE, "MOV R1,iram_addr"], 
    [0xAA, 2, I_MOV, [OP_R2, OP_IRAM], FLAG_NONE, "MOV R2,iram_addr"], 
    [0xAB, 2, I_MOV, [OP_R3, OP_IRAM], FLAG_NONE, "MOV R3,iram_addr"], 
    [0xAC, 2, I_MOV, [OP_R4, OP_IRAM], FLAG_NONE, "MOV R4,iram_addr"], 
    [0xAD, 2, I_MOV, [OP_R5, OP_IRAM], FLAG_NONE, "MOV R5,iram_addr"], 
    [0xAE, 2, I_MOV, [OP_R6, OP_IRAM], FLAG_NONE, "MOV R6,iram_addr"], 
    [0xAF, 2, I_MOV, [OP_R7, OP_IRAM], FLAG_NONE, "MOV R7,iram_addr"], 
    [0x92, 2, I_MOV, [OP_BITADDR, OP_C], FLAG_NONE, "MOV bit_addr,C"], 
    [0x75, 3, I_MOV, [OP_IRAM, OP_DATA], FLAG_NONE, "MOV iram_addr,#data"], 
    [0x86, 2, I_MOV, [OP_IRAM, OP_ATR0], FLAG_NONE, "MOV iram_addr,@R0"], 
    [0x87, 2, I_MOV, [OP_IRAM, OP_ATR1], FLAG_NONE, "MOV iram_addr,@R1"], 
    [0x88, 2, I_MOV, [OP_IRAM, OP_R0], FLAG_NONE, "MOV iram_addr,R0"], 
    [0x89, 2, I_MOV, [OP_IRAM, OP_R1], FLAG_NONE, "MOV iram_addr,R1"], 
    [0x8A, 2, I_MOV, [OP_IRAM, OP_R2], FLAG_NONE, "MOV iram_addr,R2"], 
    [0x8B, 2, I_MOV, [OP_IRAM, OP_R3], FLAG_NONE, "MOV iram_addr,R3"], 
    [0x8C, 2, I_MOV, [OP_IRAM, OP_R4], FLAG_NONE, "MOV iram_addr,R4"], 
    [0x8D, 2, I_MOV, [OP_IRAM, OP_R5], FLAG_NONE, "MOV iram_addr,R5"], 
    [0x8E, 2, I_MOV, [OP_IRAM, OP_R6], FLAG_NONE, "MOV iram_addr,R6"], 
    [0x8F, 2, I_MOV, [OP_IRAM, OP_R7], FLAG_NONE, "MOV iram_addr,R7"], 
    [0xF5, 2, I_MOV, [OP_IRAM, OP_A], FLAG_NONE, "MOV iram_addr,A"], 
    [0x85, 3, I_MOV, [OP_IRAM, OP_IRAM], FLAG_NONE, "MOV iram_addr,iram_addr"], 


    # MOVC
    # Function: Move Code Byte to Accumulator
    # Syntax: MOVC A,@A+register
    [0x93, 1, I_MOVC, [OP_A, OP_ATA, OP_DPTR], FLAG_NONE, "MOVC A,@A+DPTR"], 
    [0x83, 1, I_MOVC, [OP_A, OP_ATA, OP_PC], FLAG_NONE, "MOVC A,@A+PC"], 

    # MOVX
    # Function: Move Data To/From External Memory (XRAM)
    # Syntax: MOVX operand1,operand2
    [0xF0, 1, I_MOVX, [OP_ATDPTR, OP_A], FLAG_NONE, "MOVX @DPTR,A"], 
    [0xF2, 1, I_MOVX, [OP_ATR0, OP_A], FLAG_NONE, "MOVX @R0,A"], 
    [0xF3, 1, I_MOVX, [OP_ATR1, OP_A], FLAG_NONE, "MOVX @R1,A"], 
    [0xE0, 1, I_MOVX, [OP_A, OP_ATDPTR], FLAG_NONE, "MOVX A,@DPTR"], 
    [0xE2, 1, I_MOVX, [OP_A, OP_ATR0], FLAG_NONE, "MOVX A,@R0"], 
    [0xE3, 1, I_MOVX, [OP_A, OP_ATR1], FLAG_NONE, "MOVX A,@R1"], 

    # MUL
    # Function: Multiply Accumulator by B
    # Syntax: MUL AB
    [0xA4, 1, I_MUL, [OP_A, OP_B], FLAG_OV, "MUL AB"], 

    # NOP
    # Function: None"],, waste time
    # Syntax: No Operation
    [0x00, 1, I_NOP, [], FLAG_NONE, "NOP"], 

    # ORL
    # Function: Bitwise OR
    # Syntax: ORL operand1,operand2
    [0x42, 2, I_ORL, [OP_IRAM, OP_A], FLAG_NONE, "ORL iram_addr,A"], 
    [0x43, 3, I_ORL, [OP_IRAM, OP_DATA], FLAG_NONE, "ORL iram_addr,#data"], 
    [0x44, 2, I_ORL, [OP_A, OP_DATA], FLAG_NONE, "ORL A,#data"], 
    [0x45, 2, I_ORL, [OP_A, OP_IRAM], FLAG_NONE, "ORL A,iram_addr"], 
    [0x46, 1, I_ORL, [OP_A, OP_ATR0], FLAG_NONE, "ORL A,@R0"], 
    [0x47, 1, I_ORL, [OP_A, OP_ATR1], FLAG_NONE, "ORL A,@R1"], 
    [0x48, 1, I_ORL, [OP_A, OP_R0], FLAG_NONE, "ORL A,R0"], 
    [0x49, 1, I_ORL, [OP_A, OP_R1], FLAG_NONE, "ORL A,R1"], 
    [0x4A, 1, I_ORL, [OP_A, OP_R2], FLAG_NONE, "ORL A,R2"], 
    [0x4B, 1, I_ORL, [OP_A, OP_R3], FLAG_NONE, "ORL A,R3"], 
    [0x4C, 1, I_ORL, [OP_A, OP_R4], FLAG_NONE, "ORL A,R4"], 
    [0x4D, 1, I_ORL, [OP_A, OP_R5], FLAG_NONE, "ORL A,R5"], 
    [0x4E, 1, I_ORL, [OP_A, OP_R6], FLAG_NONE, "ORL A,R6"], 
    [0x4F, 1, I_ORL, [OP_A, OP_R7], FLAG_NONE, "ORL A,R7"], 
    [0x72, 2, I_ORL, [OP_C, OP_BITADDR], FLAG_NONE, "ORL C,bit_addr"], 
    [0xA0, 2, I_ORL, [OP_C, OP_BITADDR], FLAG_NONE, "ORL C,/bit_addr"], 

    # POP
    # Function: Pop Value From Stack
    # Syntax: POP iram_addr
    [0xD0, 2, I_POP, [OP_IRAM], FLAG_NONE, "POP iram_addr"], 

    # PUSH
    # Function: Push Value Onto Stack
    # Syntax: PUSH
    [0xC0, 2, I_PUSH, [OP_IRAM], FLAG_NONE, "PUSH iram_addr"], 

    # RET
    # Function: Return From Subroutine
    # Syntax: RET
    [0x22, 1, I_RET, [], FLAG_NONE, "RET"], 


    # RETI
    # Function: Return From Interrupt
    # Syntax: RETI
    [0x32, 1, I_RETI, [], FLAG_NONE, "RETI"], 

    # RL
    # Function: Rotate Accumulator Left
    # Syntax: RL A
    [0x23, 1, I_RL, [OP_A], FLAG_C, "RL A"], 

    # RLC
    # Function: Rotate Accumulator Left Through Carry
    # Syntax: RLC A
    [0x33, 1, I_RLC, [OP_A], FLAG_C, "RLC A"], 

    # RR
    # Function: Rotate Accumulator Right
    # Syntax: RR A
    [0x03, 1, I_RR, [OP_A], FLAG_NONE, "RR A"], 

    # RRC
    # Function: Rotate Accumulator Right Through Carry
    # Syntax: RRC A
    [0x13, 1, I_RRC, [OP_A], FLAG_C, "RRC A"], 

    # Operation: SETB
    # Function: Set Bit
    # Syntax: SETB bit addr
    [0xD3, 1, I_SETB, [OP_C],       FLAG_C, "SETB C"],
    [0xD2, 2, I_SETB, [OP_BITADDR], FLAG_C, "SETB bit_addr"], 

    # Operation: SJMP
    # Function: Short Jump
    # Syntax: SJMP reladdr  (-128 ~ +127)
    [0x80, 2, I_SJMP, [OP_RELADDR], FLAG_NONE, "SJMP reladdr"], 

    # Operation: SUBB
    # Function: Subtract from Accumulator With Borrow
    # Syntax: SUBB A,operand
    [0x94, 2, I_SUBB, [OP_A, OP_DATA], FLAG_C_AC_OV, "SUBB A,#data"],
    [0x95, 2, I_SUBB, [OP_A, OP_IRAM], FLAG_C_AC_OV, "SUBB A,iram_addr"], 
    [0x96, 1, I_SUBB, [OP_A, OP_ATR0], FLAG_C_AC_OV, "SUBB A,@R0"],
    [0x97, 1, I_SUBB, [OP_A, OP_ATR1], FLAG_C_AC_OV, "SUBB A,@R1"],
    [0x98, 1, I_SUBB, [OP_A, OP_R0], FLAG_C_AC_OV, "SUBB A,R0"], 
    [0x99, 1, I_SUBB, [OP_A, OP_R1], FLAG_C_AC_OV, "SUBB A,R1"], 
    [0x9A, 1, I_SUBB, [OP_A, OP_R2], FLAG_C_AC_OV, "SUBB A,R2"], 
    [0x9B, 1, I_SUBB, [OP_A, OP_R3], FLAG_C_AC_OV, "SUBB A,R3"], 
    [0x9C, 1, I_SUBB, [OP_A, OP_R4], FLAG_C_AC_OV, "SUBB A,R4"], 
    [0x9D, 1, I_SUBB, [OP_A, OP_R5], FLAG_C_AC_OV, "SUBB A,R5"], 
    [0x9E, 1, I_SUBB, [OP_A, OP_R6], FLAG_C_AC_OV, "SUBB A,R6"], 
    [0x9F, 1, I_SUBB, [OP_A, OP_R7], FLAG_C_AC_OV, "SUBB A,R7"], 

    # Operation: SWAP
    # Function: Swap Accumulator Nibbles
    # Syntax: SWAP A
    [0xC4, 1, I_SWAP, [OP_A], FLAG_NONE, "SWAP A"],

    # Operation: Undefined Instruction
    # Function: Undefined
    # Syntax: ???
    [0xA5, 1, I_UNDEF, [], FLAG_C, "??? 0xA5 1 C"],

    # Operation: XCH
    # Function: Exchange Bytes
    # Syntax: XCH A,register
    [0xC5, 2, I_XCH, [OP_A, OP_IRAM], FLAG_NONE, "XCH A,iram_addr"], 
    [0xC6, 1, I_XCH, [OP_A, OP_ATR0], FLAG_NONE, "XCH A,@R0"], 
    [0xC7, 1, I_XCH, [OP_A, OP_ATR1], FLAG_NONE, "XCH A,@R1"], 
    [0xC8, 1, I_XCH, [OP_A, OP_R0], FLAG_NONE, "XCH A,R0"], 
    [0xC9, 1, I_XCH, [OP_A, OP_R1], FLAG_NONE, "XCH A,R1"], 
    [0xCA, 1, I_XCH, [OP_A, OP_R2], FLAG_NONE, "XCH A,R2"], 
    [0xCB, 1, I_XCH, [OP_A, OP_R3], FLAG_NONE, "XCH A,R3"], 
    [0xCC, 1, I_XCH, [OP_A, OP_R4], FLAG_NONE, "XCH A,R4"], 
    [0xCD, 1, I_XCH, [OP_A, OP_R5], FLAG_NONE, "XCH A,R5"], 
    [0xCE, 1, I_XCH, [OP_A, OP_R6], FLAG_NONE, "XCH A,R6"], 
    [0xCF, 1, I_XCH, [OP_A, OP_R7], FLAG_NONE, "XCH A,R7"], 

    # Operation: XCHD
    # Function: Exchange Digit
    # Syntax: XCHD A,[@R0/@R1]
    [0xD6, 1, I_XCHD, [OP_A, OP_ATR0], FLAG_NONE, "XCHD A,@R0"], 
    [0xD7, 1, I_XCHD, [OP_A, OP_ATR1], FLAG_NONE, "XCHD A,@R1"], 

    # Operation: XRL
    # Function: Bitwise Exclusive OR
    # Syntax: XRL operand1,operand2
    [0x62, 2, I_XRL, [OP_IRAM, OP_A], FLAG_NONE, "XRL iram_addr,A"], 
    [0x63, 3, I_XRL, [OP_IRAM, OP_DATA], FLAG_NONE, "XRL iram_addr,#data"], 
    [0x64, 2, I_XRL, [OP_A, OP_DATA], FLAG_NONE, "XRL A,#data"], 
    [0x65, 2, I_XRL, [OP_A, OP_IRAM], FLAG_NONE, "XRL A,iram_addr"], 
    [0x66, 1, I_XRL, [OP_A, OP_ATR0], FLAG_NONE, "XRL A,@R0"], 
    [0x67, 1, I_XRL, [OP_A, OP_ATR1], FLAG_NONE, "XRL A,@R1"], 
    [0x68, 1, I_XRL, [OP_A, OP_R0], FLAG_NONE, "XRL A,R0"], 
    [0x69, 1, I_XRL, [OP_A, OP_R1], FLAG_NONE, "XRL A,R1"], 
    [0x6A, 1, I_XRL, [OP_A, OP_R2], FLAG_NONE, "XRL A,R2"], 
    [0x6B, 1, I_XRL, [OP_A, OP_R3], FLAG_NONE, "XRL A,R3"], 
    [0x6C, 1, I_XRL, [OP_A, OP_R4], FLAG_NONE, "XRL A,R4"], 
    [0x6D, 1, I_XRL, [OP_A, OP_R5], FLAG_NONE, "XRL A,R5"], 
    [0x6E, 1, I_XRL, [OP_A, OP_R6], FLAG_NONE, "XRL A,R6"], 
    [0x6F, 1, I_XRL, [OP_A, OP_R7], FLAG_NONE, "XRL A,R7"], 
]

