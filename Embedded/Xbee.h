/*
*Team ID : #547
*Author List : Kumar Gaurav Singh
*Filename: Xbee.h
*Theme: Supply Bot
*Functions: usart_read
*Global Variables: None
*
*/


/*
*Function Name: usart_read
*Input: None
*Output: None
*Logic: Reads the data sent by Xbee module 
*Example Call: usart_read();
*
*/

char usart_read() {
while( !(UCSR0A & (1<<RXC0))) { }// Wait for RXC0 flag to get set after which received value in UDR0 register is returned
return UDR0;
}