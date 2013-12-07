import wx
from utils import tohex, get_sfr_addr

#FSR0:0x0
#FSR1:0x1
#FSR2:0x2
#FAST:0x1
#W:0x0
#A:0x0
#ACCESS:0x0
#BANKED:0x1
#SRCON0:0x0F68
#SRCON1:0x0F69
#CM2CON0:0x0F6B
#CM2CON1:0x0F6C
#CM1CON0:0x0F6D
#SSPMSK:0x0F6F
#SLRCON:0x0F76
#WPUA:0x0F77
#WPUB:0x0F78
#IOCA:0x0F79
#IOCB:0x0F7A
#ANSEL:0x0F7E
#ANSELH:0x0F7F
#PORTA:0x0F80
#PORTB:0x0F81
#PORTC:0x0F82
#LATA:0x0F89
#LATB:0x0F8A
#LATC:0x0F8B
#DDRA:0x0F92
#TRISA:0x0F92
#DDRB:0x0F93
#TRISB:0x0F93
#DDRC:0x0F94
#TRISC:0x0F94
#OSCTUNE:0x0F9B
#PIE1:0x0F9D
#PIR1:0x0F9E
#IPR1:0x0F9F
#PIE2:0x0FA0
#PIR2:0x0FA1
#IPR2:0x0FA2
#EECON1:0x0FA6
#EECON2:0x0FA7
#EEDATA:0x0FA8
#EEADR:0x0FA9
#RCSTA:0x0FAB
#TXSTA:0x0FAC
#TXREG:0x0FAD
#RCREG:0x0FAE
#SPBRG:0x0FAF
#SPBRGH:0x0FB0
#T3CON:0x0FB1
#TMR3:0x0FB2
#TMR3L:0x0FB2
#TMR3H:0x0FB3
#ECCP1AS:0x0FB6
#PWM1CON:0x0FB7
#BAUDCON:0x0FB8
#BAUDCTL:0x0FB8
#PSTRCON:0x0FB9
#REFCON0:0x0FBA
#VREFCON0:0x0FBA
#REFCON1:0x0FBB
#VREFCON1:0x0FBB
#REFCON2:0x0FBC
#VREFCON2:0x0FBC
#CCP1CON:0x0FBD
#CCPR1:0x0FBE
#CCPR1L:0x0FBE
#CCPR1H:0x0FBF
#ADCON2:0x0FC0
#ADCON1:0x0FC1
#ADCON0:0x0FC2
#ADRES:0x0FC3
#ADRESL:0x0FC3
#ADRESH:0x0FC4
#SSPCON2:0x0FC5
#SSPCON1:0x0FC6
#SSPSTAT:0x0FC7
#SSPADD:0x0FC8
#SSPBUF:0x0FC9
#T2CON:0x0FCA
#PR2:0x0FCB
#TMR2:0x0FCC
#T1CON:0x0FCD
#TMR1:0x0FCE
#TMR1L:0x0FCE
#TMR1H:0x0FCF
#RCON:0x0FD0
#WDTCON:0x0FD1
#OSCCON2:0x0FD2
#OSCCON:0x0FD3
#T0CON:0x0FD5
#TMR0:0x0FD6
#TMR0L:0x0FD6
#TMR0H:0x0FD7
#STATUS:0x0FD8
#FSR2L:0x0FD9
#FSR2H:0x0FDA
#PLUSW2:0x0FDB
#PREINC2:0x0FDC
#POSTDEC2:0x0FDD
#POSTINC2:0x0FDE
#INDF2:0x0FDF
#BSR:0x0FE0
#FSR1L:0x0FE1
#FSR1H:0x0FE2
#PLUSW1:0x0FE3
#PREINC1:0x0FE4
#POSTDEC1:0x0FE5
#POSTINC1:0x0FE6
#INDF1:0x0FE7
#WREG:0x0FE8
#FSR0L:0x0FE9
#FSR0H:0x0FEA
#PLUSW0:0x0FEB
#PREINC0:0x0FEC
#POSTDEC0:0x0FED
#POSTINC0:0x0FEE
#INDF0:0x0FEF
#INTCON3:0x0FF0
#INTCON2:0x0FF1
#INTCON:0x0FF2
#PROD:0x0FF3
#PRODL:0x0FF3
#PRODH:0x0FF4
#TABLAT:0x0FF5
#TBLPTR:0x0FF6
#TBLPTRL:0x0FF6
#TBLPTRH:0x0FF7
#TBLPTRU:0x0FF8
#PC:0x0FF9
#PCL:0x0FF9
#PCLATH:0x0FFA
#PCLATU:0x0FFB
#STKPTR:0x0FFC
#TOS:0x0FFD
#TOSL:0x0FFD
#TOSH:0x0FFE
#TOSU:0x0FFF
#SRPR:0x0000
#SRPS:0x0001
#SRNQEN:0x0002
#SRQEN:0x0003
#SRLEN:0x0007
#SRCLK0:0x0004
#SRCLK1:0x0005
#SRCLK2:0x0006
#SRRC1E:0x0000
#SRRC2E:0x0001
#SRRCKE:0x0002
#SRRPE:0x0003
#SRSC1E:0x0004
#SRSC2E:0x0005
#SRSCKE:0x0006
#SRSPE:0x0007
#C2R:0x0002
#C2SP:0x0003
#C2POL:0x0004
#C2OE:0x0005
#C2OUT_CM2CON0:0x0006
#C2ON:0x0007
#C2CH0:0x0000
#C2CH1:0x0001
#C2SYNC:0x0000
#C1SYNC:0x0001
#C2HYS:0x0002
#C1HYS:0x0003
#C2RSEL:0x0004
#C1RSEL:0x0005
#MC2OUT:0x0006
#MC1OUT:0x0007
#C1R:0x0002
#C1SP:0x0003
#C1POL:0x0004
#C1OE:0x0005
#C1OUT_CM1CON0:0x0006
#C1ON:0x0007
#C1CH0:0x0000
#C1CH1:0x0001
#MSK0:0x0000
#MSK1:0x0001
#MSK2:0x0002
#MSK3:0x0003
#MSK4:0x0004
#MSK5:0x0005
#MSK6:0x0006
#MSK7:0x0007
#SLRA:0x0000
#SLRB:0x0001
#SLRC:0x0002
#WPUA0:0x0000
#WPUA1:0x0001
#WPUA2:0x0002
#WPUA3:0x0003
#WPUA4:0x0004
#WPUA5:0x0005
#WPUB4:0x0004
#WPUB5:0x0005
#WPUB6:0x0006
#WPUB7:0x0007
#IOCA0:0x0000
#IOCA1:0x0001
#IOCA2:0x0002
#IOCA3:0x0003
#IOCA4:0x0004
#IOCA5:0x0005
#IOCB4:0x0004
#IOCB5:0x0005
#IOCB6:0x0006
#IOCB7:0x0007
#ANS0:0x0000
#ANS1:0x0001
#ANS2:0x0002
#ANS3:0x0003
#ANS4:0x0004
#ANS5:0x0005
#ANS6:0x0006
#ANS7:0x0007
#ANSEL0:0x0000
#ANSEL1:0x0001
#ANSEL2:0x0002
#ANSEL3:0x0003
#ANSEL4:0x0004
#ANSEL5:0x0005
#ANSEL6:0x0006
#ANSEL7:0x0007
#ANS8:0x0000
#ANS9:0x0001
#ANS10:0x0002
#ANS11:0x0003
#ANSEL8:0x0000
#ANSEL9:0x0001
#ANSEL10:0x0002
#ANSEL11:0x0003
#RA0:0x0000
#RA1:0x0001
#RA2:0x0002
#RA3:0x0003
#RA4:0x0004
#RA5:0x0005
#AN0:0x0000
#AN1:0x0001
#AN2:0x0002
#MCLR:0x0003
#AN3:0x0004
#T13CKI:0x0005
#CVREF:0x0000
#C12IN0M:0x0001
#C1OUT_PORTA:0x0002
#NOT_MCLR:0x0003
#OSC2:0x0004
#OSC1:0x0005
#VREFM:0x0000
#VREFP:0x0001
#T0CKI:0x0002
#CLKOUT:0x0004
#CLKIN:0x0005
#INT0:0x0000
#INT1:0x0001
#INT2:0x0002
#PGD:0x0000
#PGC:0x0001
#VPP:0x0003
#C1INP:0x0000
#SRQ:0x0002
#RB4:0x0004
#RB5:0x0005
#RB6:0x0006
#RB7:0x0007
#SDI:0x0004
#RX:0x0005
#SCL:0x0006
#TX:0x0007
#SDA:0x0004
#SCK:0x0006
#CK:0x0007
#AN10:0x0004
#AN11:0x0005
#RC0:0x0000
#RC1:0x0001
#RC2:0x0002
#RC3:0x0003
#RC4:0x0004
#RC5:0x0005
#RC6:0x0006
#RC7:0x0007
#AN4:0x0000
#AN5:0x0001
#AN6:0x0002
#AN7:0x0003
#AN8:0x0006
#AN9:0x0007
#C12INP:0x0000
#C12IN1M:0x0001
#C12IN2M:0x0002
#C12IN3M:0x0003
#C12OUT:0x0004
#P1D:0x0002
#P1C:0x0003
#P1B:0x0004
#P1A:0x0005
#SS:0x0006
#SDO:0x0007
#C2INP:0x0000
#PGM:0x0003
#C2OUT_PORTC:0x0004
#CCP1:0x0005
#NOT_SS:0x0006
#LATA0:0x0000
#LATA1:0x0001
#LATA2:0x0002
#LATA4:0x0004
#LATA5:0x0005
#LATB4:0x0004
#LATB5:0x0005
#LATB6:0x0006
#LATB7:0x0007
#LATC0:0x0000
#LATC1:0x0001
#LATC2:0x0002
#LATC3:0x0003
#LATC4:0x0004
#LATC5:0x0005
#LATC6:0x0006
#LATC7:0x0007
#TRISA0:0x0000
#TRISA1:0x0001
#TRISA2:0x0002
#TRISA4:0x0004
#TRISA5:0x0005
#RA0:0x0000
#RA1:0x0001
#RA2:0x0002
#RA4:0x0004
#RA5:0x0005
#TRISA0:0x0000
#TRISA1:0x0001
#TRISA2:0x0002
#TRISA4:0x0004
#TRISA5:0x0005
#RA0:0x0000
#RA1:0x0001
#RA2:0x0002
#RA4:0x0004
#RA5:0x0005
#TRISB4:0x0004
#TRISB5:0x0005
#TRISB6:0x0006
#TRISB7:0x0007
#RB4:0x0004
#RB5:0x0005
#RB6:0x0006
#RB7:0x0007
#TRISB4:0x0004
#TRISB5:0x0005
#TRISB6:0x0006
#TRISB7:0x0007
#RB4:0x0004
#RB5:0x0005
#RB6:0x0006
#RB7:0x0007
#TRISC0:0x0000
#TRISC1:0x0001
#TRISC2:0x0002
#TRISC3:0x0003
#TRISC4:0x0004
#TRISC5:0x0005
#TRISC6:0x0006
#TRISC7:0x0007
#RC0:0x0000
#RC1:0x0001
#RC2:0x0002
#RC3:0x0003
#RC4:0x0004
#RC5:0x0005
#RC6:0x0006
#RC7:0x0007
#TRISC0:0x0000
#TRISC1:0x0001
#TRISC2:0x0002
#TRISC3:0x0003
#TRISC4:0x0004
#TRISC5:0x0005
#TRISC6:0x0006
#TRISC7:0x0007
#RC0:0x0000
#RC1:0x0001
#RC2:0x0002
#RC3:0x0003
#RC4:0x0004
#RC5:0x0005
#RC6:0x0006
#RC7:0x0007
#PLLEN:0x0006
#INTSRC:0x0007
#TUN0:0x0000
#TUN1:0x0001
#TUN2:0x0002
#TUN3:0x0003
#TUN4:0x0004
#TUN5:0x0005
#TMR1IE:0x0000
#TMR2IE:0x0001
#CCP1IE:0x0002
#SSPIE:0x0003
#TXIE:0x0004
#RCIE:0x0005
#ADIE:0x0006
#TMR1IF:0x0000
#TMR2IF:0x0001
#CCP1IF:0x0002
#SSPIF:0x0003
#TXIF:0x0004
#RCIF:0x0005
#ADIF:0x0006
#TMR1IP:0x0000
#TMR2IP:0x0001
#CCP1IP:0x0002
#SSPIP:0x0003
#TXIP:0x0004
#RCIP:0x0005
#ADIP:0x0006
#TMR3IE:0x0001
#BCLIE:0x0003
#EEIE:0x0004
#C2IE:0x0005
#C1IE:0x0006
#OSCFIE:0x0007
#TMR3IF:0x0001
#BCLIF:0x0003
#EEIF:0x0004
#C2IF:0x0005
#C1IF:0x0006
#OSCFIF:0x0007
#TMR3IP:0x0001
#BCLIP:0x0003
#EEIP:0x0004
#C2IP:0x0005
#C1IP:0x0006
#OSCFIP:0x0007
#RD:0x0000
#WR:0x0001
#WREN:0x0002
#WRERR:0x0003
#FREE:0x0004
#CFGS:0x0006
#EEPGD:0x0007
#EEADR0:0x0000
#EEADR1:0x0001
#EEADR2:0x0002
#EEADR3:0x0003
#EEADR4:0x0004
#EEADR5:0x0005
#EEADR6:0x0006
#EEADR7:0x0007
#RX9D:0x0000
#OERR:0x0001
#FERR:0x0002
#ADDEN:0x0003
#CREN:0x0004
#SREN:0x0005
#RX9:0x0006
#SPEN:0x0007
#ADEN:0x0003
#TX9D:0x0000
#TRMT:0x0001
#BRGH:0x0002
#SENDB:0x0003
#SYNC:0x0004
#TXEN:0x0005
#TX9:0x0006
#CSRC:0x0007
#TMR3ON:0x0000
#TMR3CS:0x0001
#NOT_T3SYNC:0x0002
#T3CCP1:0x0003
#RD16:0x0007
#T3SYNC:0x0002
#T3CKPS0:0x0004
#T3CKPS1:0x0005
#ECCPASE:0x0007
#PSSBD0:0x0000
#PSSBD1:0x0001
#PSSAC0:0x0002
#PSSAC1:0x0003
#ECCPAS0:0x0004
#ECCPAS1:0x0005
#ECCPAS2:0x0006
#PRSEN:0x0007
#PDC0:0x0000
#PDC1:0x0001
#PDC2:0x0002
#PDC3:0x0003
#PDC4:0x0004
#PDC5:0x0005
#PDC6:0x0006
#ABDEN:0x0000
#WUE:0x0001
#BRG16:0x0003
#CKTXP:0x0004
#DTRXP:0x0005
#RCIDL:0x0006
#ABDOVF:0x0007
#SCKP:0x0004
#ABDEN:0x0000
#WUE:0x0001
#BRG16:0x0003
#CKTXP:0x0004
#DTRXP:0x0005
#RCIDL:0x0006
#ABDOVF:0x0007
#SCKP:0x0004
#STRA:0x0000
#STRB:0x0001
#STRC:0x0002
#STRD:0x0003
#STRSYNC:0x0004
#FVR1S0:0x0004
#FVR1S1:0x0005
#FVR1ST:0x0006
#FVR1EN:0x0007
#FVR1S0:0x0004
#FVR1S1:0x0005
#FVR1ST:0x0006
#FVR1EN:0x0007
#D1NSS:0x0000
#DAC1OE:0x0005
#D1LPS:0x0006
#D1EN:0x0007
#D1NSS0:0x0000
#D1PSS0:0x0002
#D1PSS1:0x0003
#D1NSS:0x0000
#DAC1OE:0x0005
#D1LPS:0x0006
#D1EN:0x0007
#D1NSS0:0x0000
#D1PSS0:0x0002
#D1PSS1:0x0003
#DAC1R0:0x0000
#DAC1R1:0x0001
#DAC1R2:0x0002
#DAC1R3:0x0003
#DAC1R4:0x0004
#DAC1R0:0x0000
#DAC1R1:0x0001
#DAC1R2:0x0002
#DAC1R3:0x0003
#DAC1R4:0x0004
#CCP1M0:0x0000
#CCP1M1:0x0001
#CCP1M2:0x0002
#CCP1M3:0x0003
#DC1B0:0x0004
#DC1B1:0x0005
#P1M0:0x0006
#P1M1:0x0007
#ADFM:0x0007
#ADCS0:0x0000
#ADCS1:0x0001
#ADCS2:0x0002
#ACQT0:0x0003
#ACQT1:0x0004
#ACQT2:0x0005
#NVCFG0:0x0000
#NVCFG1:0x0001
#PVCFG0:0x0002
#PVCFG1:0x0003
#ADON:0x0000
#GO_NOT_DONE:0x0001
#DONE:0x0001
#CHS0:0x0002
#CHS1:0x0003
#CHS2:0x0004
#CHS3:0x0005
#NOT_DONE:0x0001
#GO_DONE:0x0001
#GO:0x0001
#SEN:0x0000
#RSEN:0x0001
#PEN:0x0002
#RCEN:0x0003
#ACKEN:0x0004
#ACKDT:0x0005
#ACKSTAT:0x0006
#GCEN:0x0007
#CKP:0x0004
#SSPEN:0x0005
#SSPOV:0x0006
#WCOL:0x0007
#SSPM0:0x0000
#SSPM1:0x0001
#SSPM2:0x0002
#SSPM3:0x0003
#BF:0x0000
#UA:0x0001
#R_NOT_W:0x0002
#S:0x0003
#P:0x0004
#D_NOT_A:0x0005
#CKE:0x0006
#SMP:0x0007
#R:0x0002
#D:0x0005
#NOT_W:0x0002
#NOT_A:0x0005
#R_W:0x0002
#D_A:0x0005
#NOT_WRITE:0x0002
#NOT_ADDRESS:0x0005
#TMR2ON:0x0002
#T2CKPS0:0x0000
#T2CKPS1:0x0001
#T2OUTPS0:0x0003
#T2OUTPS1:0x0004
#T2OUTPS2:0x0005
#T2OUTPS3:0x0006
#TMR1ON:0x0000
#TMR1CS:0x0001
#NOT_T1SYNC:0x0002
#T1OSCEN:0x0003
#T1RUN:0x0006
#RD16:0x0007
#T1SYNC:0x0002
#T1CKPS0:0x0004
#T1CKPS1:0x0005
#NOT_BOR:0x0000
#NOT_POR:0x0001
#NOT_PD:0x0002
#NOT_TO:0x0003
#NOT_RI:0x0004
#SBOREN:0x0006
#IPEN:0x0007
#BOR:0x0000
#POR:0x0001
#PD:0x0002
#TO:0x0003
#RI:0x0004
#SWDTEN:0x0000
#SWDTE:0x0000
#LFIOFS:0x0000
#HFIOFL:0x0001
#PRI_SD:0x0002
#HFIOFS:0x0002
#OSTS:0x0003
#IDLEN:0x0007
#SCS0:0x0000
#SCS1:0x0001
#FLTS:0x0002
#IRCF0:0x0004
#IRCF1:0x0005
#IRCF2:0x0006
#PSA:0x0003
#T0SE:0x0004
#T0CS:0x0005
#T08BIT:0x0006
#TMR0ON:0x0007
#T0PS0:0x0000
#T0PS1:0x0001
#T0PS2:0x0002
#C:0x0000
#DC:0x0001
#Z:0x0002
#OV:0x0003
#N:0x0004
#INT1IF:0x0000
#INT2IF:0x0001
#INT1IE:0x0003
#INT2IE:0x0004
#INT1IP:0x0006
#INT2IP:0x0007
#INT1F:0x0000
#INT2F:0x0001
#INT1E:0x0003
#INT2E:0x0004
#INT1P:0x0006
#INT2P:0x0007
#RABIP:0x0000
#TMR0IP:0x0002
#INTEDG2:0x0004
#INTEDG1:0x0005
#INTEDG0:0x0006
#NOT_RABPU:0x0007
#RBIP:0x0000
#RABPU:0x0007
#NOT_RBPU:0x0007
#RABIF:0x0000
#INT0IF:0x0001
#TMR0IF:0x0002
#RABIE:0x0003
#INT0IE:0x0004
#TMR0IE:0x0005
#PEIE_GIEL:0x0006
#GIE_GIEH:0x0007
#RBIF:0x0000
#INT0F:0x0001
#T0IF:0x0002
#RBIE:0x0003
#INT0E:0x0004
#T0IE:0x0005
#PEIE:0x0006
#GIE:0x0007
#GIEL:0x0006
#GIEH:0x0007
#STKUNF:0x0006
#STKOVF:0x0007
#SP0:0x0000
#SP1:0x0001
#SP2:0x0002
#SP3:0x0003
#SP4:0x0004
#STKFUL:0x0007
#_CONFIG1H:0x300001
#_CONFIG2L:0x300002
#_CONFIG2H:0x300003
#_CONFIG3H:0x300005
#_CONFIG4L:0x300006
#_CONFIG5L:0x300008
#_CONFIG5H:0x300009
#_CONFIG6L:0x30000A
#_CONFIG6H:0x30000B
#_CONFIG7L:0x30000C
#_CONFIG7H:0x30000D
#_FOSC_LP_1H:0xF0
#_FOSC_XT_1H:0xF1
#_FOSC_HS_1H:0xF2
#_FOSC_ERCCLKOUT_1H:0xF3
#_FOSC_ECCLKOUTH_1H:0xF4
#_FOSC_ECH_1H:0xF5
#_FOSC_ERC_1H:0xF7
#_FOSC_IRC_1H:0xF8
#_FOSC_IRCCLKOUT_1H:0xF9
#_FOSC_ECCLKOUTM_1H:0xFA
#_FOSC_ECM_1H:0xFB
#_FOSC_ECCLKOUTL_1H:0xFC
#_FOSC_ECL_1H:0xFD
#_PLLEN_OFF_1H:0xEF
#_PLLEN_ON_1H:0xFF
#_PCLKEN_OFF_1H:0xDF
#_PCLKEN_ON_1H:0xFF
#_FCMEN_OFF_1H:0xBF
#_FCMEN_ON_1H:0xFF
#_IESO_OFF_1H:0x7F
#_IESO_ON_1H:0xFF
#_PWRTEN_ON_2L:0xFE
#_PWRTEN_OFF_2L:0xFF
#_BOREN_OFF_2L:0xF9
#_BOREN_ON_2L:0xFB
#_BOREN_NOSLP_2L:0xFD
#_BOREN_SBORDIS_2L:0xFF
#_BORV_30_2L:0xE7
#_BORV_27_2L:0xEF
#_BORV_22_2L:0xF7
#_BORV_19_2L:0xFF
#_WDTEN_OFF_2H:0xFE
#_WDTEN_ON_2H:0xFF
#_WDTPS_1_2H:0xE1
#_WDTPS_2_2H:0xE3
#_WDTPS_4_2H:0xE5
#_WDTPS_8_2H:0xE7
#_WDTPS_16_2H:0xE9
#_WDTPS_32_2H:0xEB
#_WDTPS_64_2H:0xED
#_WDTPS_128_2H:0xEF
#_WDTPS_256_2H:0xF1
#_WDTPS_512_2H:0xF3
#_WDTPS_1024_2H:0xF5
#_WDTPS_2048_2H:0xF7
#_WDTPS_4096_2H:0xF9
#_WDTPS_8192_2H:0xFB
#_WDTPS_16384_2H:0xFD
#_WDTPS_32768_2H:0xFF
#_HFOFST_OFF_3H:0xF7
#_HFOFST_ON_3H:0xFF
#_MCLRE_OFF_3H:0x7F
#_MCLRE_ON_3H:0xFF
#_STVREN_OFF_4L:0xFE
#_STVREN_ON_4L:0xFF
#_LVP_OFF_4L:0xFB
#_LVP_ON_4L:0xFF
#_BBSIZ_OFF_4L:0xF7
#_BBSIZ_ON_4L:0xFF
#_XINST_OFF_4L:0xBF
#_XINST_ON_4L:0xFF
#_DEBUG_ON_4L:0x7F
#_DEBUG_OFF_4L:0xFF
#_CP0_ON_5L:0xFE
#_CP0_OFF_5L:0xFF
#_CP1_ON_5L:0xFD
#_CP1_OFF_5L:0xFF
#_CPB_ON_5H:0xBF
#_CPB_OFF_5H:0xFF
#_CPD_ON_5H:0x7F
#_CPD_OFF_5H:0xFF
#_WRT0_ON_6L:0xFE
#_WRT0_OFF_6L:0xFF
#_WRT1_ON_6L:0xFD
#_WRT1_OFF_6L:0xFF
#_WRTC_ON_6H:0xDF
#_WRTC_OFF_6H:0xFF
#_WRTB_ON_6H:0xBF
#_WRTB_OFF_6H:0xFF
#_WRTD_ON_6H:0x7F
#_WRTD_OFF_6H:0xFF
#_EBTR0_ON_7L:0xFE
#_EBTR0_OFF_7L:0xFF
#_EBTR1_ON_7L:0xFD
#_EBTR1_OFF_7L:0xFF
#_EBTRB_ON_7H:0xBF
#_EBTRB_OFF_7H:0xFF
#_DEVID1:0x3FFFFE
#_DEVID2:0x3FFFFF
#_IDLOC0:0x200000
#_IDLOC1:0x200001
#_IDLOC2:0x200002
#_IDLOC3:0x200003
#_IDLOC4:0x200004
#_IDLOC5:0x200005
#_IDLOC6:0x200006
#_IDLOC7:0x200007

#---------------------------------------------------------------------------------------------------
class SfrTextCtrl(wx.TextCtrl):
    def __init__(self, parent, sizer, label_str, help_str="", default_str="", flag=wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, sz1=(40,-1), sz2=(35,-1)):
        wx.TextCtrl.__init__(self, parent, -1, "", size=sz2, style=wx.TE_READONLY)
        box = wx.BoxSizer(wx.HORIZONTAL)

        self.label = wx.StaticText(parent, -1, label_str, pos=(0,0), size=sz1, style=wx.ALIGN_RIGHT)
        box.Add(self.label, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 0)
        
        text = self
        text.SetValue(default_str)
        text.SetHelpText(help_str)
        text.SetBackgroundColour((185,185,185))
        box.Add(text, 1, wx.ALIGN_CENTRE|wx.RIGHT, 0)

        sizer.Add(box, 0, flag, 0)
        
    def set_value(self, v):
        self.SetValue(tohex(v, 2))
        if v == 0:
            self.SetBackgroundColour((185,185,185))
        else:
            self.SetBackgroundColour((235,235,235))   
            
#---------------------------------------------------------------------------------------------------
class SfrTextCtrlList(wx.StaticBoxSizer):
    def __init__(self, parent, parent_sizer, title, lst):
        box = wx.StaticBox(parent, wx.ID_ANY, title)
        wx.StaticBoxSizer.__init__(self, box, wx.HORIZONTAL)
        box_sizer = self
                    
        panel = wx.Panel(parent,style=wx.TAB_TRAVERSAL|wx.NO_BORDER)
        p_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.text_list = []
        h = 0
        for t in lst:
            obj = SfrTextCtrl(panel, p_sizer, t[0], hex(t[1]), '00')
            self.text_list.append([t[0], t[1], obj])
            
        panel.SetSizer(p_sizer)
        panel.Layout()
         
        box_sizer.Add(panel, 1, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 2)
        parent_sizer.Add(box_sizer, 0, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 2)
        
    #------------------------------------------------------------------------
    def update(self, sim):
        if sim is None:
            return
        
        for t in self.text_list:
            i = t[1]
            v = sim.get_reg(t[0].lower())
            text = t[2]
            text.SetValue(tohex(v, 2))
            if v == 0:
                text.SetBackgroundColour((185,185,185))
            else:
                text.SetBackgroundColour((235,235,235))

#---------------------------------------------------------------------------
class LabelTextCtrl(wx.TextCtrl):
    def __init__(self, parent, sizer, label_str, help_str="", default_str="", flag=wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, size=(-1,-1)):
        wx.TextCtrl.__init__(self, parent, -1, "", size = size)
        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(parent, -1, label_str, style=wx.ALIGN_RIGHT)
        box.Add(label, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 1)
        
        text = self
        text.SetValue(default_str)
        text.SetHelpText(help_str)
        box.Add(text, 1, wx.ALIGN_CENTRE|wx.RIGHT, 1)

        sizer.Add(box, 0, flag, 0)
        
    def set_value(self, v, n):
        self.SetValue(tohex(v, n))
        if v == 0:
            self.SetBackgroundColour((185,185,185))
        else:
            self.SetBackgroundColour((235,235,235))

#---------------------------------------------------------------------------------------------------
class PcDptrTextCtrlList(wx.StaticBoxSizer):
    def __init__(self, parent, parent_sizer):
        title = ''
        box = wx.StaticBox(parent, wx.ID_ANY, title)
        wx.StaticBoxSizer.__init__(self, box, wx.HORIZONTAL)
        box_sizer = self
                    
        panel = wx.Panel(parent,style=wx.TAB_TRAVERSAL|wx.NO_BORDER)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
            
        self.pc_text = LabelTextCtrl(panel, sizer, 'PC ', '', '00', size=(60, -1))
        self.dptr_text = LabelTextCtrl(panel, sizer, '  FSR0 ', '', '00', size=(60, -1))
        self.sp_text = LabelTextCtrl(panel, sizer, '  SP ', '', '00', size=(30, -1))
        panel.SetSizer(sizer)
        panel.Layout()
         
        box_sizer.Add(panel, 1, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 2)
        parent_sizer.Add(box_sizer, 0, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 2)
        
    #------------------------------------------------------------------------
    def update(self, sim):
        if sim is None:
            return
        self.pc_text.set_value(sim.get_reg('PC'), 4)
        self.dptr_text.set_value(sim.get_reg('FSR0'), 4)
        self.sp_text.set_value(sim.get_reg('SP'), 2)
        
#---------------------------------------------------------------------------
class PortTextCtrl():
    def __init__(self, parent, sizer, label_str, help_str="", default_str="", flag=wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, size=(-1,-1)):
        
        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(parent, -1, label_str, style=wx.ALIGN_RIGHT)
        box.Add(label, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 1)
        
        self.text = wx.TextCtrl(parent, -1, default_str, size = size)
        self.text.SetValue(default_str)
        self.text.SetHelpText(help_str)
        box.Add(self.text, 0, wx.ALIGN_CENTRE|wx.RIGHT, 1)
        
        self.bit_text_list = []
        c = parent.GetBackgroundColour()
        for i in range(8):
            t = wx.TextCtrl(parent, -1, "0", size=(20, -1),style=wx.BORDER_STATIC|wx.ALIGN_CENTER)
            t.SetBackgroundColour(c)
            self.bit_text_list.append(t)
            box.Add(t, 0, wx.ALIGN_CENTRE, 1)

        sizer.Add(box, 0, flag, 0)
        
            
    def set_value(self, v):
        self.text.SetValue(tohex(v, 2))
        c = [(180, 180, 180), (255, 255, 100)]
        for i in range(8):
            b = (v >> (7 - i)) & 1
            t = self.bit_text_list[i]
            t.SetValue(str(b))
            t.SetBackgroundColour(c[b])
        
#---------------------------------------------------------------------------------------------------
class PortTextCtrlList(wx.StaticBoxSizer):
    def __init__(self, parent, parent_sizer):
        title = ''
        box = wx.StaticBox(parent, wx.ID_ANY, title)
        wx.StaticBoxSizer.__init__(self, box, wx.VERTICAL)
        box_sizer = self
                    
        panel = wx.Panel(parent,style=wx.TAB_TRAVERSAL|wx.NO_BORDER)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.p0_text = PortTextCtrl(panel, sizer, 'PORTA ', '', '00', size=(30, -1))
        self.p1_text = PortTextCtrl(panel, sizer, 'PORTB ', '', '00', size=(30, -1))
        self.p2_text = PortTextCtrl(panel, sizer, 'PORTC ', '', '00', size=(30, -1))
        self.t0_text = PortTextCtrl(panel, sizer, 'TRISA ', '', '00', size=(30, -1))
        self.t1_text = PortTextCtrl(panel, sizer, 'TRISB ', '', '00', size=(30, -1))
        self.t2_text = PortTextCtrl(panel, sizer, 'TRISC ', '', '00', size=(30, -1))        
        panel.SetSizer(sizer)
        panel.Layout()
         
        box_sizer.Add(panel, 1, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 2)
        parent_sizer.Add(box_sizer, 0, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 2)
        
    #------------------------------------------------------------------------
    def update(self, sim):
        if sim is None:
            return

        self.p0_text.set_value(sim.get_reg('PORTA'))
        self.p1_text.set_value(sim.get_reg('PORTB'))
        self.p2_text.set_value(sim.get_reg('PORTC'))
        self.t0_text.set_value(sim.get_reg('TRISA'))
        self.t1_text.set_value(sim.get_reg('TRISB'))
        self.t2_text.set_value(sim.get_reg('TRISC'))
        
#---------------------------------------------------------------------------------------------------
class RegTextCtrlList(wx.StaticBoxSizer):
    def __init__(self, parent, parent_sizer):
        title = ''
        box = wx.StaticBox(parent, wx.ID_ANY, title)
        wx.StaticBoxSizer.__init__(self, box, wx.HORIZONTAL)
        box_sizer = self
                    
        panel = wx.Panel(parent,style=wx.TAB_TRAVERSAL|wx.NO_BORDER)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        size1 = (25, -1)
        size2 = (30, -1)
        self.a_text = SfrTextCtrl(panel, sizer, ' A', '', '00', sz1=size1, sz2=size2)
        self.c_text = SfrTextCtrl(panel, sizer, ' C', '', '00', sz1=size1, sz2=size2)
        self.r0_text = SfrTextCtrl(panel, sizer, 'R0', '', '00', sz1=size1, sz2=size2)
        self.r1_text = SfrTextCtrl(panel, sizer, 'R1', '', '00', sz1=size1, sz2=size2)
        self.r2_text = SfrTextCtrl(panel, sizer, 'R2', '', '00', sz1=size1, sz2=size2)
        self.r3_text = SfrTextCtrl(panel, sizer, 'R3', '', '00', sz1=size1, sz2=size2)
        self.r4_text = SfrTextCtrl(panel, sizer, 'R4', '', '00', sz1=size1, sz2=size2)
        self.r5_text = SfrTextCtrl(panel, sizer, 'R5', '', '00', sz1=size1, sz2=size2)
        self.r6_text = SfrTextCtrl(panel, sizer, 'R6', '', '00', sz1=size1, sz2=size2)
        self.r7_text = SfrTextCtrl(panel, sizer, 'R7', '', '00', sz1=size1, sz2=size2)
        
        panel.SetSizer(sizer)
        panel.Layout()
         
        box_sizer.Add(panel, 1, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 2)
        parent_sizer.Add(box_sizer, 0, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 2)
        
    #------------------------------------------------------------------------
    def update(self, sim):
        if sim is None:
            return

        self.a_text.set_value(sim.get_reg('a'))
        self.c_text.set_value(sim.get_reg('c'))
        self.r0_text.set_value(sim.get_reg('r0'))
        self.r1_text.set_value(sim.get_reg('r1'))
        self.r2_text.set_value(sim.get_reg('r2'))
        self.r3_text.set_value(sim.get_reg('r3'))
        self.r4_text.set_value(sim.get_reg('r4'))
        self.r5_text.set_value(sim.get_reg('r5'))
        self.r6_text.set_value(sim.get_reg('r6'))
        self.r7_text.set_value(sim.get_reg('r7'))
                    
#---------------------------------------------------------------------------------------------------
class SfrWatchPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__ (self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size(300,300), style = wx.TAB_TRAVERSAL)
                
        self.SetMinSize(wx.Size(300,300))
        #main_sizer = wx.BoxSizer(wx.VERTICAL)
        #self.pc_dptr_viewer = PcDptrTextCtrlList(self, main_sizer)
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.sfr_map_1 = [
            ['P0',   0x80],
            ['P1',   0x90],
            ['P2',   0xA0],
            ['P3',   0xB0],
            ['DPL',  0x82],
            ['DPH',  0x83],
            ['PSW',  0xD0],
            
            ['ACC',  0xE0],
            
            ['IE',   0xA8],
            ['IP',   0xB8],
        ]
        
        self.sfr_map_2 = [
            ['PCON', 0x87],
            ['TCON', 0x88],
            ['TMOD', 0x89],
            ['TL0',  0x8A],
            
            ['TL1',  0x8B],
            ['TH0',  0x8C],
            ['TH1',  0x8D],
            ['SCON', 0x98],
            ['SBUF', 0x99],
            ['B',    0xF0],
        ]
        
        self.watch1 = SfrTextCtrlList(self, sizer, '', self.sfr_map_1)
        self.watch2 = SfrTextCtrlList(self, sizer, '', self.sfr_map_2)
        self.reg_watch = RegTextCtrlList(self, sizer)
        
        #main_sizer.Add(sizer, 1, wx.EXPAND|wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        self.SetSizer(sizer)
        self.Layout()
        
    #------------------------------------------------------------------------
    def update(self, sim):
        if sim is None:
            return
        #self.pc_dptr_viewer.update(sim)
        self.watch1.update(sim)
        self.watch2.update(sim)
        self.reg_watch.update(sim)
        
        
#---------------------------------------------------------------------------------------------------
class UartTextViewer(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__ (self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size(300,200), style = wx.TAB_TRAVERSAL)
                
        self.SetMinSize(wx.Size(300,100))
        sbSizer1 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"Uart Viewer"), wx.VERTICAL)

        self.inst_text = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE|wx.HSCROLL)
        
        sbSizer1.Add(self.inst_text, 1, wx.EXPAND, 5)
        self.SetSizer(sbSizer1)
        sbSizer1.Layout()
        
    #------------------------------------------------------------------------
    def update_inst(self, sim, sbuf): 
        self.inst_text.SetValue('')
        s = "file = " + sim.c_file + "\n"
        s += "line = " + str(sim.c_line) + "\n\n"
        
        s += str(sbuf) + '\n'
        s1 = ''.join(chr(i) for i in sbuf)
        s += s1 
        #s += 'sbuf list = ' + str(sim.sbuf_list) + '\n'
            
        self.inst_text.WriteText(s)
        
#class WatchPanel (wx.Panel):
    
    #def __init__(self, parent):
        #wx.Panel.__init__ (self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size(500,300), style = wx.TAB_TRAVERSAL)
        
        #sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        #self.splitter = wx.SplitterWindow(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D)
        #self.splitter.Bind(wx.EVT_IDLE, self.OnIdle)
        
        #p1 = self.sfr_watch = SfrWatchPanel(self.splitter)
        #p2 = self.sfr_text_view = SfrTextViewer(self.splitter)

        #self.splitter.SplitHorizontally(p1, p2, 0)
            
        #sizer.Add(self.splitter, 1, wx.EXPAND, 5)
                
        #self.SetSizer(sizer)
        #self.Layout()
        
    ##------------------------------------------------------------------------
    #def update(self, sim):
        #self.sfr_watch.update(sim)
        
    ##------------------------------------------------------------------------
    #def update_inst(self, sim, sbuf): 
        #self.sfr_text_view.update_inst(sim, sbuf)
        
    ##------------------------------------------------------------------------
    #def OnIdle(self, event):
        #self.splitter.SetSashPosition(0)
        #self.splitter.Unbind(wx.EVT_IDLE)
        
    ##------------------------------------------------------------------------
    #def __del__(self):
        #pass
        
class IoPortPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        box = wx.StaticBox(self, -1, "This is a wx.StaticBox")
        bsizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        t = wx.StaticText(self, -1, "Controls placed \"inside\" the box are really its siblings")
        bsizer.Add(t, 0, wx.TOP|wx.LEFT, 5)


        border = wx.BoxSizer()
        border.Add(bsizer, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(border)
    
#---------------------------------------------------------------------------------------------------
class WatchPanel (wx.Panel):
    
    def __init__(self, parent, mcu_name, mcu_device):
        wx.Panel.__init__ (self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size(500,300), style = wx.TAB_TRAVERSAL)
        
        self.mcu_name = mcu_name
        self.mcu_device = mcu_device
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.pc_dptr_viewer = PcDptrTextCtrlList(self, sizer)
        self.port_panel = PortTextCtrlList(self, sizer)
        
        #watch_panel = self.sfr_watch = SfrWatchPanel(self)
        text_view = self.uart_text_view = UartTextViewer(self)
        
        #sizer.Add(watch_panel, 0, wx.EXPAND, 5)
        sizer.Add(text_view, 1, wx.EXPAND, 5)
        
        self.SetSizer(sizer)
        self.Layout()
        
    #------------------------------------------------------------------------
    def update(self, sim):
        self.pc_dptr_viewer.update(sim)
        self.port_panel.update(sim)
        #self.sfr_watch.update(sim)
        
    #------------------------------------------------------------------------
    def update_inst(self, sim, sbuf): 
        self.uart_text_view.update_inst(sim, sbuf)
        
    #------------------------------------------------------------------------
    def OnIdle(self, event):
        self.splitter.SetSashPosition(0)
        self.splitter.Unbind(wx.EVT_IDLE)
        
    #------------------------------------------------------------------------
    def __del__(self):
        pass