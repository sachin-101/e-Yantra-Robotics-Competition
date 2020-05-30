/*
*Team ID : #547
*Author List : Siddharth Rao Appala
*Filename: servo_strike.h
*Theme: Supply Bot
*Functions: motorSpeed
*Global Variables: analogArray[]
*
*/

#include "line_sensor.h"

uint16_t analogArray[numOfSensors];

/*
*Function Name: motorSpeed
*Input: Direction (Character)
*Output: None
*Logic: Uses line sensor readings to set motor speed based on line following logic
*Example Call: motorSpeed('F');
*
*/

int motorSpeed(char dir)
{
	int lastError;
	float P, D, error;
	
	int binary_tune[3];
	
	for( int i=0;i<3;i++)
	{
		analogArray[i]= sensorsAnalog(i);
		if (analogArray[i] > 250)
		binary_tune[i]=0;
		else binary_tune[i] = 1;
	}
	
	unsigned int sensorPIDReading[numOfSensors], setpointReading[numOfSensors], errorReading[numOfSensors];
	
	ADCInit();
    
	if(dir=='F'){
	
	if (binary_tune[1] == 0 && binary_tune[2] == 1 && binary_tune[0] == 0  ) motorSet(160, 175, 'F');
	else if (binary_tune[1] == 1 && binary_tune[2] == 0 && binary_tune[0] == 0 ) motorSet(170, 140, 'F');
	else if (binary_tune[1] == 0 && binary_tune[2] == 0 && binary_tune[0] == 1 ) motorSet(145, 175, 'F');
	else if (binary_tune[1] == 0 && binary_tune[2] == 0 && binary_tune[0] == 0 ) motorSet(140, 175,'F');
	else motorSet(155, 175, 'F');}
}