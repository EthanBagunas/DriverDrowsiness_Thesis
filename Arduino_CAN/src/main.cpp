//==================================================================================//

#include <CAN.h>  

const int button_pin = 8;
const int buzz_pin = 9;
int pos =0;
int val;
int count=0;
void setup() {

  Serial.begin(9600);
  while (!Serial);
  delay (1000);
  pinMode(LED_BUILTIN,OUTPUT);

  // start the CAN bus at 500 kbps
  if (!CAN.begin (500E3)) {
    Serial.println ("Starting CAN failed!");
    while (1);
  }
  else {
    Serial.println ("CAN Initialized");
  }
}


void canSender(int& mcuid) {
  // send packet: id is 11 bits, packet can contain up to 8 bytes of data
  int id;
  if (mcuid == 0) {
  id = 0x12;    
  Serial.print ("Sending packet ... ");
  
  CAN.beginPacket (id);  //sets the ID and clears the transmit buffer
  // CAN.beginExtendedPacket(0xabcdef);
  CAN.write ('Y');
  CAN.write ('A');
  CAN.write ('W');
  CAN.write ('N');
  CAN.endPacket();
  //RTR packet with a requested data length
  CAN.beginPacket (0x12, 3, true);
  CAN.endPacket();
  Serial.println (id,HEX);
  } 
  
  else{
  id = 0x11;  
  Serial.print ("Sending packet ... ");
  CAN.beginPacket (id);  //sets the ID and clears the transmit buffer
  // CAN.beginExtendedPacket(0xabcdef);
  CAN.write ('C'); //write data to buffer. data is not sent until endPacket() is called.
  CAN.write ('L');
  CAN.write ('O');
  CAN.write ('S');
  CAN.write ('E');
  CAN.endPacket();
  //RTR packet with a requested data length
  CAN.beginPacket (0x11, 3, true);
  CAN.endPacket();
  Serial.println (id, HEX);
  }
  delay (1000);
}


void blink(int& wait) {
  digitalWrite(LED_BUILTIN, HIGH);
  // Wait for 1 second
  delay(wait*1000);
  // Turn the LED off
  digitalWrite(LED_BUILTIN, LOW);
  // Wait for 1 second
  delay(wait*1000);
}
void loop() 
{
  int data;
  if (Serial.available() > 0) {
    String rcv = Serial.readStringUntil('\n');
    Serial.print("Data Received: ");
    data= rcv.toInt();
    Serial.println(data);
    canSender(data);
  }     
}



