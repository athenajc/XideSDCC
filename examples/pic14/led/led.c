#include <pic14/pic16f883.h>



void main()
{
    unsigned char i=0;
    int j;
    unsigned char led[] = {0x3f, 0x06, 0x5b, 0x4f, 0x66, 0x6D, 0x7D, 0x07, 0x7f, 0x6f};

    do
    {
        i++;
        if (i > 9)
            i = 0;
        PORTA = led[i];
        
        for (j = 0; j < 5000; j++);

    } while(1);
}