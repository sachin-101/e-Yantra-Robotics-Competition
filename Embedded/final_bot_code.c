/*
*Team ID : #547
*Author List : Siddharth Rao Appala, Kumar Gaurav Singh, Sachin Kumar
*Filename: servo_strike.h
*Theme: Supply Bot
*Functions: beep_buzzer, 
*Global Variables: duty_time
*
*/

#include <avr/io.h>
#include <util/delay.h>
#include <avr/interrupt.h>
#include "motorControl.h"
#include "follow_logic.h"
#include "Xbee.h"
#include "line_sensor.h"
#include "servo_strike.h"

#define buzzerPin 2

unsigned char data;

	// 1 sec - twice on reaching city
	// 1 sec - After striking
	// 5 sec - After run completes

/*
*Function Name: ISR 
*Input: None
*Output: None
*Logic: Usart interrupt is fired when the RX data buffer receives data
*Example Call: None
*
*/

ISR(USART_RX_vect)
{
	data = usart_read(); 
}

int main ()
{
	
	sei();
	//buzzer init
	DDRD|= (1<<buzzerPin);
	PORTD|= (1<<buzzerPin);
	
	motorsInit();
	ADCInit();
	usart_init();
	servo_begin();
	servo_init();
	_delay_ms(2000);
	servo_reset();
	_delay_ms(2000);
	
	uint16_t binaryArray[3];
	uint8_t readingBinary;
	char sensorChar[50],sensorCharMin[50],sensorCharMax[50];
	char temp;
	
	int moving = 0;
	
	while(1){
		
		if(data == 'm')  // move the bot
		{
			UDR0 = 0x00;
			motorSpeed('F');
		}
		else if (data == 's')  // stop to hit marker
		{	
			UDR0 = 0x00;
			motorSet(0, 0, 'c');
			data = NULL;
		}
		else if(data == 'b')  // beep the buzzer
		{  // 1 sec - twice on reaching city
			// 1 sec - After striking
			UDR0 = 0x00;                           
			PORTD &= ~(1<<buzzerPin);
			_delay_ms(1000);
			PORTD |= (1<<buzzerPin);
			data = NULL;
		}
		else if(data == 'h')  //hit the marker  
		{
			UDR0 = 0x00;
			_delay_ms(2000);
			servo_strike();
			_delay_ms(5000);
			servo_init();
			_delay_ms(1000);
			servo_reset();
			_delay_ms(5000);
			data = NULL;		
		}
		
		else if(data == 'l')  // long beep end of run
		{  // 5 sec - After run completes
			UDR0 = 0x00;
			PORTD &= ~(1<<buzzerPin);
			_delay_ms(5000);
			PORTD |= (1<<buzzerPin);
			data = NULL;
			break;	
		} 	
			
	}	
}


// ARCHIVE
//readingBinary= sensorsBinary();
/*for( int i=0;i<3;i++)
	{
		analogArray[i]= sensorsAnalog(i);
		if (analogArray[i] > 250) 
			{
				//sprintf(sensorChar,"%d",analogArray[i]);
		//for(int k= 0; sensorChar[k]!=0;k++)
			usart_send('0');
			}
		else usart_send('1');					
		usart_send('\t');
	}				
usart_send('\n');
}*/	

//usart_send('\n');