/*
*Team ID : #547
*Author List : Kumar Gaurav Singh
*Filename: line_sensor.h
*Theme: Supply Bot
*Functions: emitterOn, emitterOff, DEC_to_BCD, usart_send_packedBCD, ADCInit, analogRead, button_press, usart_init, usart_send, calibrate, sensorAnalog, sensorsBinary 
*Global Variables: maxValues[3], minValues[3], threshold[3],sensorValues[numOfSensors];
*
*/


#ifndef line_sensor
#define line_sensor

#include <avr/io.h>
#include <util/delay.h>
#include <avr/eeprom.h>

#define emitterPort PORTC
#define emitterDirReg DDRC
#define emitterPin1 0
#define emitterPin2 1
#define emitterPin3 2
#define numOfSensors 3

static uint16_t maxValues[3], minValues[3], threshold[3],sensorValues[numOfSensors];

/*
*Function Name: emitterOn
*Input: None
*Output: None
*Logic: Makes Emitter pins high
*Example Call: emitterOn();
*
*/


void emitterOn()
{
	emitterPort |= (1<<emitterPin1)|(1<<emitterPin2)|(1<<emitterPin3);
}

/*
*Function Name: emitterOff
*Input: None
*Output: None
*Logic: Makes Emitter pins low
*Example Call: emitterOff();
*
*/

void emitterOff()
{
	emitterPort &= ~((1<<emitterPin1)|(1<<emitterPin2)|(1<<emitterPin3));
}
/*
*Function Name: DEC_to_BCD 
*Input: Integer value to be changed to BCD 
*Output: BCD value
*Logic: Converts Decimal to BCD by dividing by 16 as, shifting 4 places in Binary multiples or divides by 16
*Example Call: DEC_to_BCD(value);
*
*/
unsigned char DEC_to_BCD(int val) //Converting Decimal to packed BCD
{
	return ( (val/10)*16 + (val%10));
}

/*
*Function Name: usart_send_packedBCD
*Input:  BCD Data(unsigned char) to be sent
*Output: None
*Logic: Converts packed BCD to unpacked BCD and then to ASCII for transmission and sends the same using Usart
*Example Call: usart_send_packedBCD() 
*
*/

void usart_send_packedBCD(unsigned char data) // To convert packed BCD to ASCII before transmitting
{
	usart_send( '0' + (data>>4));
	usart_send( '0' + (data & 0x0F));
}
/*
*Function Name: button_press
*Input:  None
*output: number 1 or 2, according as whether button is pressed or not
*Logic: Push button is interfaced in Pull-up mode and returns 2 when pressed.
*Example Call: button_press()
*
*/

uint8_t button_press()
{
	if(!(PIND & (1<<PD3)))
		return 2;
	return 1;
}

/*
*Function Name: ADCInit
*Input: None
*Output: None
*Logic: Initializes ADC (for reading sensor values) by setting the appropriate bits of ADC Registers
*Example Call: ADCInit();
*
*/

void ADCInit()
{
	ADCSRA |=  (1<<ADPS2)|(1<<ADPS1);	// prescalar set to 8
	ADMUX |= 1<<REFS0;		//reference voltage as AVCC
	ADCSRA |= (1<<ADEN)|(1<<ADATE);	//To Enable ADC
	emitterDirReg= 0x00; //Set emitter pin as input pin
}

/*
*Function Name: analogRead
*Input: ADC channel number (uint8_t)
*Output: Returns the analog value(uint16_t) after the conversion is completed 
*Logic: Reads the Analog values being retunred by the sensors
*Example Call: analogRead();
*
*/

uint16_t analogRead(uint8_t ch) //Read
{    
   ch&=0b00000111;         //ANDing to limit input to 7
	ADMUX = (ADMUX & 0xf8)|ch;  //Clear last 3 bits of ADMUX, OR with ch. 0xf8= 11111000
	ADCSRA |= 1<<ADSC;		//conversion starts
	
	while(!(ADCSRA & (1 << ADIF)));	//Wait till conversion is completed
	return ADC;
}

/*
*Function Name: usart_init
*Input: None
*Output: None
*Logic: Initializes Usart by setting appropriate bit of usart registers
*Example Call: usart_init();
*
*/

void usart_init()
{
	UCSR0A=0x00;
	UCSR0B= (1<<TXEN0)|(1<<RXEN0)|(1<<RXCIE0); //Enabling transmitter
	UCSR0C= (1<<UCSZ01)|(1<<UCSZ00); // Setting number of data bits as 8
	UBRR0= 103; //Setting baud rate as 9600 bps. UBBR= Fosc/(16*BAUD)-1, Fosc--> System clock frequency= 16MHz
}

/*
*Function Name: usart_send_packedBCD
*Input: Data (char ) to be sent
*Output: None
*Logic: Sends the data through Usart protocol
*Example Call: usart_send('c');
*/

void usart_send( char data)
{
while(!( UCSR0A & (1<<UDRE0))){ } // Wait while the UDRE0 flag is set and transmit buffer (UDR0) is empty to receive new data.
UDR0= data;
}

/*
*Function Name: calibrate
*Input: None
*Output: None
*Logic: Calibrates the three sensors by taking 100 readings on one call, arranging the readings on ascending order and taking the middle (median) value
*Example Call: calibrate();
*/
/*void calibrate() // To find maximum and minimum values for each sensor, which is stored in an array and used to define threshold
{
	emitterDirReg|= (1<<emitterPin1)|(1<<emitterPin2)|(1<<emitterPin3); //Setting emitter pins as output pins
	
	int numReadings = 100;
	int temp[100][numOfSensors];
	//int flag = 1;
	//printf("Read white values now!");
	while(flag != 2)
	{
		uint16_t t;
			//Take 100 readings from 3 sensors and store it into an array
		for(uint8_t k=0; k<100; k++)
		{
			for(uint8_t j=0; j<numOfSensors; j++)
			{
				emitterOn();		//Set IR emitters on
				_delay_ms(10);
				temp[k][j] = analogRead(j);
				/* emitterOff(); //Set IR emitters off
				_delay_ms(10);
				sensorValues[j] = analogRead(j);
				temp[k][j] = temp[k][j] - sensorValues[j];
			}
		}
		//Arrange the values of each sensor in ascending order
		for(uint8_t k=0; k<numOfSensors; k++)
		{
			for(uint8_t j=0; j<99; j++)
			{
				for(uint8_t i=j+1; i<100; i++)
				{
					if(temp[i][k] < temp[j][k])
					{
						t = temp[i][k];
						temp[i][k] = temp[j][k];
						temp[j][k] = t;
					}
				}
			}
		}
	
		
		for(int i = 0; i<numOfSensors; i++)
			maxValues[i] = temp[49][i];
		flag = button_press();
		_delay_ms(100);
		DEC_to_BCD(flag);
		usart_send_packedBCD(flag);
	}	
	
	printf("Read black values now!");
	while(flag != 1)
	{
		uint16_t t;
		//Take 1000 readings from 3 sensors and store it into an array
		for(uint8_t k=0; k<100; k++)
		{
			for(uint8_t j=0; j<numOfSensors; j++)
			{
				emitterOn();		//Set IR emitters on
				temp[k][j] = analogRead(j);
				/*emitterOff(); //Set IR emitters off
				_delay_ms(10);
				sensorValues[j] = analogRead(j);
				temp[k][j] = temp[k][j] - sensorValues[j]; 
			}
		}
		//Arrange the values of each sensor in ascending order
		for(uint8_t k=0; k<numOfSensors; k++)
		{
			for(uint8_t j=0; j<99; j++)
			{
				for(uint8_t i=j+1; i<100; i++)
				{
					if(temp[i][k] < temp[j][k])
					{
						t = temp[i][k];
						temp[i][k] = temp[j][k];
						temp[j][k] = t;
					}
				}
			}
		}
		
		for(int i = 0; i<numOfSensors; i++)
			minValues[i] = temp[49][i];
		flag = button_press();
		_delay_ms(100);
		DEC_to_BCD(flag);
		usart_send_packedBCD(flag);
	}
	
	//printf("Stored both the values");
	
	for(int i=0; i<numOfSensors; i++)
	{
		threshold[i] = ((maxValues[i] - minValues[i]) / 2);
		/*eeprom_write_word((uint16_t*)(i*2), threshold[i]);
		eeprom_write_word((uint16_t*)((i*2)+16), minValues[i]);
		eeprom_write_word((uint16_t*)((i*2)+32), maxValues[i]);
	}
	}*/

/*
*Function Name: sensorsAnalog
*Input: sensor index (integer 0 or 1 or 2)
*Output: The analog value of the intensity received by the sensor
*Logic: Stores the analog values being received by the sensor receivers in an array and returns the value corresponding to the sensor index passed
*Example Call: sensorsAnalog(1);
*/
int sensorsAnalog(int i) 
{
	uint16_t temp[numOfSensors];
	for(uint8_t i=0; i<numOfSensors; i++)
	
		emitterOn();	//Set IR emitters on
		sensorValues[i] = analogRead(i);
		return sensorValues[i];
}



// Archive
/*
uint8_t sensorsBinary() // To convert analog values from sensor to binary, based on whether the value is above or below the threshold
{   
	uint16_t binaryArray[8];
	uint8_t binary=0, bitmask=0b10000000;
	 sensorsAnalog(binaryArray);
			for(uint8_t i=0; i<numOfSensors; i++)
		{
		if(binaryArray[i] > threshold[i])
		binary |= bitmask;
		else
		binary |= 0;
		bitmask = bitmask>>1;
			}	
		return binary;
}*/	
#endif