
#define 	currentSPI				SPIC
#define 	currentPORT			PORTC
#define		currentCS_bm			(1 << 4)
#define		currentMOSI_bm			(1 << 5)
#define		currentCLK_bm			(1 << 7)



void Clock_Init(void);
void Interrupts_Init(void);
void CCPWrite( volatile uint8_t * address, uint8_t value );
uint16_t Current_Read(uint8_t channel);