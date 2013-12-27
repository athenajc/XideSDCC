#include <pic16/pic18f452.h> 

// Configurations
/*
 char at __CONFIG1H conf1 = _OSC_HS_PLL_1H & _OSCS_ON_1H;   // Select HS PLL OSC
 char at __CONFIG2L conf2 = _PUT_ON_2L;
 char at __CONFIG2H conf3 = _WDT_OFF_2H;                    // Disable WDT
 char at __CONFIG4L conf4 = _LVP_OFF_4L;                    // Disable LVP
*/

// Main body
void main() {
    unsigned char i = 0;
    int j;
    // Initializing ports
    PORTA = 0;
    PORTB = 0;

    // Set RA4 as input and RB3-RB0 as output
    TRISA |= 0x10;
    TRISB &= 0xF0;

    // Set value 0x0A to PORTB
    PORTB = 0x0A;

    // If button is pressed, toggle PORTB
    for (i = 0; i < 30; i++)
    {
        //if(PORTAbits.RA4 != 0)
        PORTB = ~PORTB;
        PORTA++;
        PORTB += 2;
        for (j = 0; j < 3000; j++) {}
    }
}

