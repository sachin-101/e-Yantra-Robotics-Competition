/*
*Team ID : #547
*Author List : Siddharth Rao Appala and Kumar Gaurav Singh
*Filename: servo_strike.h
*Theme: Supply Bot
*Functions: servo_begin, servo_write, servo_init, servo_reset, servo_strike
*Global Variables: duty_time
*
*/


#include <avr/io.h>
#include <util/delay.h>
#define OCR1_2ms 3999
#define OCR1_1ms 900

float duty_time;
/*
*Function Name: servo_begin
*Input: None
*Output: None
*Logic: Initializes Timer1 in PWM mode to control the servo  
*Example Call: servo_begin();
*
*/

void servo_begin()
{
	/*Set pre-scaler of 8 with Fast PWM (Mode 14 i.e TOP value as ICR1)  non-inverting mode */
	DDRB |= 1 << PINB1;
	TCCR1A |= (1 << WGM11) | (1 << COM1A1);
	TCCR1B |= (1 << WGM12) | (1 << WGM13) | (1 << CS11);
	ICR1 = 39999; // Set pwm period as 20ms
}
/*
*Function Name: servo_write
*Input: Angle (float)
*Output: None
*Logic: Sets the compare register (OCR1A) value depending on the angle of servo sweep using linear mapping
*Example Call: servo_write(60);
*
*/
void servo_write(float angle)
{
	OCR1A = (OCR1_1ms + (OCR1_2ms-OCR1_1ms)*angle/180);  // Map angle to OCR1_1ms - OCR_2ms range
}

/*
*Function Name: servo_init
*Input: None
*Output: None
*Logic: Initializes the servo to 10 degrees position at the beginning
*Example Call: servo_init();
*
*/
void servo_init()      // go to 10 degrees
{
	for(int angle=110; angle>=10; angle-- )
	{	servo_write(angle);
		_delay_ms(100);
	}
}

/*
*Function Name: servo_reset
*Input: None
*Output: None
*Logic: Resets the servo to 80 degrees, making it ready for strike
*Example Call: servo_reset();
*
*/
void servo_reset()    // go to 80 degrees
{
	for(int angle=10; angle<=80; angle++ )
	{	servo_write(angle);
		_delay_ms(100);
	}
}

/*
*Function Name: servo_strike
*Input: None
*Output: None
*Logic: Moves the servo across the angle range sufficient for it to compress the spring with the striking rod connected to it. The servo misses the rod at a particular
        angle during the compression, thereby allowing the rod to strike with the energy stored due to the compression until now.
*Example Call: servo_strike();
*
*/
void servo_strike()   // go to 160 degrees
{
	for(int angle=80; angle<=160; angle++ )
	{	servo_write(angle);
		_delay_ms(100);
	}
}
