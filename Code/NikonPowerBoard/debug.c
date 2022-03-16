/*
 *  debug.c
 *  DevBoardTest
 *
 *  Created by Joshua Schapiro on 12/20/11.
 *  Copyright 2011 Carnegie Mellon. All rights reserved.
 *
 */

#include "debug.h"

volatile uint8_t    DebugBuffer[100];
volatile uint16_t  	Debug_readLocation = 0;
volatile uint16_t   Debug_writeLocation = 0;

static FILE mystdout = FDEV_SETUP_STREAM (Debug_SendByte, NULL, _FDEV_SETUP_WRITE);

void Debug_Init(void){
	PORTE.DIRSET = 0b00001000;			// tx line
	PORTE.DIRCLR = 0b00000100;			// rx line
	
	USARTE0.CTRLC = USART_PMODE_DISABLED_gc | USART_CHSIZE_8BIT_gc ; 	    				
	
	USARTE0.BAUDCTRLA = 207 & 0xFF;								// 32mhz @9600
	USARTE0.BAUDCTRLB = (0 << USART_BSCALE0_bp)|(207 >> 8);
	
	USARTE0.CTRLB |= USART_RXEN_bm;
	USARTE0.CTRLB |= USART_TXEN_bm;
	
	USARTE0.CTRLA |= USART_RXCINTLVL_LO_gc;
	
    stdout = &mystdout;
}




void Debug_SendByte(uint8_t data){
	while(!(USARTE0.STATUS & USART_DREIF_bm));
	USARTE0.DATA = data;	
}

bool Debug_CharReadyToRead(void){
	if(Debug_writeLocation == Debug_readLocation){
		return false;  
	} else { 
		return true;
	}
}


uint8_t Debug_GetByte(bool blocking){
	if(blocking){
		while(!Debug_CharReadyToRead());
	}
	
	uint8_t tmp = DebugBuffer[Debug_readLocation];
	Debug_readLocation++;
	if(Debug_readLocation >= 100){
		Debug_readLocation=0;
	}
	return tmp;
}

ISR(USARTE0_RXC_vect){
	DebugBuffer[Debug_writeLocation] = USARTE0.DATA;
	Debug_writeLocation++;
	if(Debug_writeLocation >= 100){
		Debug_writeLocation = 0;
	}
}