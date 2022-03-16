

#include "avr_compiler.h"
#include <stdio.h>
#include "string.h"
#include "main.h"
#include "debug.c"

#define usb_pin_bm  (1 << 0)
#define cam_pin_bm (1 << 1)
#define outputPORT  PORTD

void Clock_Init(void);
void Interrupts_Init(void);
void CCPWrite( volatile uint8_t * address, uint8_t value );


uint8_t command = 0;
volatile uint16_t servoCurrent;
volatile uint16_t servoSpeedCounter = 0;
volatile uint8_t currentCapCounter = 0;
volatile bool runServo;
#define currentMax  150
#define currentCapThreshold   5

int main(void){


    Clock_Init();
    Debug_Init();
    printf("Starting up!\r");

    // 100hz for servo upkeep
    TCC1.PER = 49;
    TCC1.CTRLA = TC_CLKSEL_DIV64_gc;
    TCC1.INTCTRLA = TC_CCAINTLVL_LO_gc;


    ADCA.CH1.CTRL = ADC_CH_INPUTMODE_SINGLEENDED_gc;    // set input mode
    ADCA.CH1.MUXCTRL = ADC_CH_MUXPOS_PIN1_gc;           // set mux to read channel 0, pin A1


    ADCA.PRESCALER = (ADCA.PRESCALER & (~ADC_PRESCALER_gm)) | ADC_PRESCALER_DIV16_gc;

    ADCA.REFCTRL = ADC_REFSEL_INT1V_gc;
    ADCA.EVCTRL = 0;
    ADCA.CTRLB = 0;
    ADCA.CTRLA = ADC_ENABLE_bm;



    PORTC.DIRSET = (1 << 0);
    PORTC.OUTCLR = (1 << 0);

    TCC0.CTRLA = 0x05;				//set TC_CLK to CLK/64 (500k)
    TCC0.CTRLB = TC0_CCAEN_bm | TC0_WGMODE0_bm | TC0_WGMODE1_bm;       //Enable OC A,B,C&D.  Set to Single Slope PWM
    TCC0.PER = 10000;				// (500k / 10k = 50 hz)  (500 bits per ms)
    TCC0.CCA = 750;


    currentPORT.DIRSET = currentCS_bm |  currentCLK_bm | currentMOSI_bm;
    currentPORT.OUTSET = currentCS_bm;

    currentSPI.CTRL = SPI_ENABLE_bm
                       | SPI_MASTER_bm
                       | SPI_MODE_0_gc
                       | SPI_PRESCALER_DIV128_gc;




    outputPORT.DIRSET = usb_pin_bm | cam_pin_bm;
    outputPORT.OUTCLR = usb_pin_bm | cam_pin_bm;


    _delay_ms(2000);
    Interrupts_Init();

/*    uint16_t a, b;
    while(true){
        a 	= Current_Read(0xA0);
        printf("%u\r",a);
        _delay_ms(100);
    }
*/

    while(true){
    
        
        _delay_ms(10);
        if(Debug_CharReadyToRead()){
            command = Debug_GetByte(false);
            switch (command) {
                case 'C':   // turn camera off
                    outputPORT.OUTSET = cam_pin_bm;
                    break;
                case 'c':   // turn camera on
                    outputPORT.OUTCLR = cam_pin_bm;
                    break;
                case 'U':       //turn usb off
                    outputPORT.OUTSET = usb_pin_bm;
                    break;
                case 'u':       // turn usb on
                    outputPORT.OUTCLR = usb_pin_bm;
                    break;
                case 's':
                    currentCapCounter = 0;
                    runServo = true;
                    printf("pressing button\r");
                    break;
                default:
                    break;
            }
        }
        
    }
}

ISR(TCC1_OVF_vect){



    if(runServo){

        servoSpeedCounter++;
        if(servoSpeedCounter > 50){
            servoSpeedCounter = 0;


/*            servoCurrent = Current_Read(0xA0);
            //printf("%u\r",servoCurrent);
            if(servoCurrent > currentMax){
                currentCapCounter++;
                if(currentCapCounter > currentCapThreshold){
                    currentCapCounter = 0;
                    printf("STOP!\r");
                    runServo = false;
                    TCC0.CCA = 750;
                }
                //printf("%u\r",servoCurrent);
            } else {
                currentCapCounter = 0;
            }
*/


            if (TCC0.CCA > 450) {
                TCC0.CCA--;
            } else {
                printf("HIT END\r");
                runServo = false;
                TCC0.CCA = 750;
            }
        }

    }
}

void Clock_Init(void){
	OSC.CTRL |= OSC_RC32MEN_bm;                     // turn on 32MHz internal RC oscillator
	while(!(OSC.STATUS & OSC_RC32MRDY_bm));         // wait for it to be ready
	CCPWrite( &CLK.CTRL, CLK_SCLKSEL_RC32M_gc);     // change from 2MHz to 32MHz
}

void Interrupts_Init(void){
	
	PMIC.CTRL |= PMIC_LOLVLEN_bm;
	sei();
	
}

uint16_t Current_Read(uint8_t channel){
    uint16_t hi, lo;

    currentPORT.OUTCLR = currentCLK_bm;
    currentPORT.OUTCLR = currentCS_bm;

    currentSPI.DATA = 1;
    while(!(currentSPI.STATUS & SPI_IF_bm));

    currentSPI.DATA = channel;
    while(!(currentSPI.STATUS & SPI_IF_bm));
    hi = (currentSPI.DATA & 0b0001111);

    currentSPI.DATA = 0;
    while(!(currentSPI.STATUS & SPI_IF_bm));
    lo = currentSPI.DATA;

    currentPORT.OUTSET = currentCS_bm;

    return (lo + (hi << 8));
}


// From Application Note AVR1003
// Used to slow down clock in disk_initialize()
void CCPWrite( volatile uint8_t * address, uint8_t value ) {
    uint8_t volatile saved_sreg = SREG;
    cli();
    
#ifdef __ICCAVR__
	asm("movw r30, r16");
#ifdef RAMPZ
	RAMPZ = 0;
#endif
	asm("ldi  r16,  0xD8 \n"
	    "out  0x34, r16  \n"
#if (__MEMORY_MODEL__ == 1)
	    "st     Z,  r17  \n");
#elif (__MEMORY_MODEL__ == 2)
    "st     Z,  r18  \n");
#else /* (__MEMORY_MODEL__ == 3) || (__MEMORY_MODEL__ == 5) */
    "st     Z,  r19  \n");
#endif /* __MEMORY_MODEL__ */
    
#elif defined __GNUC__
	volatile uint8_t * tmpAddr = address;
#ifdef RAMPZ
	RAMPZ = 0;
#endif
	asm volatile(
                 "movw r30,  %0"	      "\n\t"
                 "ldi  r16,  %2"	      "\n\t"
                 "out   %3, r16"	      "\n\t"
                 "st     Z,  %1"       "\n\t"
                 :
                 : "r" (tmpAddr), "r" (value), "M" (CCP_IOREG_gc), "i" (&CCP)
                 : "r16", "r30", "r31"
                 );
    
#endif
	SREG = saved_sreg;
}
