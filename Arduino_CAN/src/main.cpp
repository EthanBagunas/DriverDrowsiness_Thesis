//==================================================================================//

#include <CAN.h>


//==================================================================================//

void setup() {

  Serial.begin (9600);
  while (!Serial);
  delay (1000);
  
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
  if (mcuid == 1) {
  int id = 0x12;    
  Serial.print ("Sending packet ... ");
  
  CAN.beginPacket (id);  //sets the ID and clears the transmit buffer
  // CAN.beginExtendedPacket(0xabcdef);
  CAN.write ('1'); //write data to buffer. data is not sent until endPacket() is called.
  CAN.write ('2');
  CAN.write ('3');
  CAN.write ('4');
  CAN.write ('5');
  CAN.write ('6');
  CAN.write ('7');
  CAN.write ('8');
  CAN.endPacket();

  //RTR packet with a requested data length
  CAN.beginPacket (0x12, 3, true);
  CAN.endPacket();

  Serial.println (id,HEX);
  } else {
  int id = 0x11;  
  Serial.print ("Sending packet ... ");
  CAN.beginPacket (id);  //sets the ID and clears the transmit buffer
  // CAN.beginExtendedPacket(0xabcdef);
  CAN.write ('N'); //write data to buffer. data is not sent until endPacket() is called.
  CAN.write ('O');
  CAN.write ('T');
  CAN.write ('-');
  CAN.write ('M');
  CAN.write ('I');
  CAN.write ('N');
  CAN.write ('E');
  CAN.endPacket();

  //RTR packet with a requested data length
  CAN.beginPacket (0x11, 3, true);
  CAN.endPacket();

  Serial.println (id, HEX);


  }
  delay (1000);
}

//==================================================================================//




void loop() {
  Serial.println("Please enter something:");

  while(Serial.available() ==0) {
    
  }

  int input = Serial.parseInt();
  Serial.println(input);
  canSender(input);
}