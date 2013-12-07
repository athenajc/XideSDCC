
FLAG_C = 1
FLAG_AC = 2
FLAG_OV = 4
FLAG_C_AC_OV = 7
FLAG_C_OV = 3
FLAG_NONE = 0

# operand type
OP_DATA = 0x100
OP_IRAM = 0x101
OP_BITADDR = 0x102
OP_RELADDR = 0x103
OP_CODE = 0x104
OP_ADDR = 0x105

OP_A = 0x110
OP_B = 0x111
OP_C = 0x112
OP_DPTR = 0x113

OP_R0 = 0x120
OP_R1 = 0x121
OP_R2 = 0x122
OP_R3 = 0x123
OP_R4 = 0x124
OP_R5 = 0x125
OP_R6 = 0x126
OP_R7 = 0x127
OP_ATR0 = 0x130
OP_ATR1 = 0x131
OP_ATA  = 0x132
OP_ATDPTR = 0x133
OP_PC = 0x140

I_ACALL = 0x11
I_ADD   = 0x24
I_ADDC  = 0x34
I_AJMP  = 0x01  
I_ANL   = 0x52   
I_CJNE  = 0xB4   
I_CLR   = 0xC2   
I_CPL   = 0xF4   
I_DA    = 0xD4   
I_DEC   = 0x15   
I_DIV   = 0x84   
I_DJNZ  = 0xD5   
I_INC   = 0x04   
I_JB    = 0x20   
I_JBC   = 0x10   
I_JC    = 0x40   
I_JMP   = 0x73   
I_JNB   = 0x30   
I_JNC   = 0x50   
I_JNZ   = 0x70   
I_JZ    = 0x60   
I_LCALL = 0x12   
I_LJMP  = 0x02   
I_MOV   = 0x76   
I_MOVC  = 0x93   
I_MOVX  = 0xF0   
I_MUL   = 0xA4   
I_NOP   = 0x00   
I_ORL   = 0x42   
I_POP   = 0xD0   
I_PUSH  = 0xC0   
I_RET   = 0x22  
I_RETI  = 0x32     
I_RL    = 0x23     
I_RLC   = 0x33     
I_RR    = 0x03     
I_RRC   = 0x13     
I_SETB  = 0xD3   
I_SJMP  = 0x80   
I_SUBB  = 0x94   
I_SWAP  = 0xC4
I_UNDEF  = 0xA5   
I_XCH   = 0xC6   
I_XCHD  = 0xD6   
I_XRL   = 0x62

BIT0 = 0x0001
BIT1 = 0x0002
BIT2 = 0x0004
BIT3 = 0x0008
BIT4 = 0x0010
BIT5 = 0x0020
BIT6 = 0x0040
BIT7 = 0x0080
BIT8 = 0x0100

BIT31 = 0x8000