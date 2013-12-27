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
    int i = 0;
    int j;
    // Initializing ports
    PORTA = 0;

    // Set PORTA and PORTB as output
    TRISA = 0x0;

    // Set value 
    PORTA = 0xFF;
    
    for (i = 0; i < 300; i++)
    {
        PORTA = ~PORTA;

        for (j = 0; j < 3000; j++) {}
    }
}

