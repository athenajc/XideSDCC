/**
 * 0001-test.c -- modified from 
 * http://ubicomp.lancs.ac.uk/~martyn/sdcc_linux/test.c
 *
 * Ports A and B will be set as all outputs.  Look for successively 
 * slower squarewaves on B0, B1, ... B7, and A0, A1, ... A3.  A4 will 
 * not show anything unless you connect it to +5V through a 10K 
 * resistor, since it is an open-drain output.
 */
 
#define __16f628a
#include <pic16f628a.h>

void swing_portb()
{
    int i;
    int j;
    
    for (i = 0; i < 8; i++)
    {
        PORTB = 1 << i;
        for (j = 0; j < 500; j++) ;
    }
    for (i = 7; i >= 0; i--)
    {
        PORTB = 1 << i;
        for (j = 0; j < 500; j++) ;
    }
}

void main(void)
{
    unsigned char i = 0;
	TRISB = 0x00;	// Set port B as all outputs
    TRISA = 0x00;	// Set port A as all outputs
	PORTB = 0x01;	
    PORTA = 0x01;	
        
    for (i = 0; i < 200; i++)
    {
        PORTA = 1 << (i & 7);
        swing_portb();
    }
}

