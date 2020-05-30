/*
*Team ID : #547
*Author List : Kumar Gaurav Singh
*Filename: motorControl.h
*Theme: Supply Bot
*Functions: motorsInit, motorSet
*Global Variables: None 
*
*/




#include <avr/io.h>

#define leftMotorComp	OCR0B
#define rightMotorComp	OCR0A

/*
*Function Name: motorsInit
*Input: None
*Output: None
*Logic: Initializes Timer0 to control motor speed with PWM
*Example Call: motorsInit();
*
*/  
void motorsInit()
{
	// motor direction control pins set to output mode
	DDRB |= (1<<4)|(1<<5);
	// OC1B and OC1A Pins set to output mode
	DDRD |= (1<<5)|(1<<6)|(1<<7)|(1<<4);
	//Clear OC1A/OC1B on compare match when up-counting and set OC1A/OC1B
	//on compare match when downcounting (sets PWM to non-inverting mode)
	TCCR0A |= (1<<COM0A1) | (1<<COM0B1);
	// prescalar value 1
	TCCR0B |= (1<<CS00);
	//Fast PWM mode
	TCCR0A |= (1<<WGM01)|(1<<WGM00);
}

/*
*Function Name: motorSet
*Input: left motor speed(integer) and right motor speed(integer) and the direction(characters 'F' or 'B',any one) we wish to set
*Output: None
*Logic: Sets the desired motor speed by assigning suitable value to Compare registers (OCR0A and OCR0B), thus, setting the right duty cycle for the PWM. 
        Sets the direction by making the direction control pins of the motor driver high or low.  
*Example Call: motorsInit(170,185,'F');
*
*/

void motorSet(int leftMotorSpeed, int rightMotorSpeed, char direction)
{
	leftMotorComp = leftMotorSpeed;
	rightMotorComp = rightMotorSpeed;
	if(direction=='B')
	{
		PORTD |=(1<<7);
		PORTD &=~(1<<4);
		PORTB |=(1<<5);
		PORTB &=~(1<<4);
	}
	else if(direction=='F')
	{
		PORTD &=~(1<<7);
		PORTD |=(1<<4);
		PORTB &=~(1<<5);
		PORTB |=(1<<4);
	}
	else
	{
		PORTB =0x00;
	}
}