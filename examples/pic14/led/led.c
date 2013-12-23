#include <pic14/pic16f883.h>



void main()
{
    unsigned char i=0;
    int j;
    unsigned char led[] = {0x3f, 0x06, 0x5b, 0x4f, 0x66, 0x6D, 0x7D, 0x07, 0x7f, 0x6f};
    
    /* all bits inverse */
    unsigned char led1[] = {0xfc, 0x60, 0xda, 0xf2, 0x66, 0xb6, 0xbe, 0xe0, 0xfe, 0xf6};
    do
    {
        i++;
        if (i > 9)
            i = 0;
        PORTA = led[i];
        PORTB = led1[i];
        
        for (j = 0; j < 5000; j++);

    } while(1);
}