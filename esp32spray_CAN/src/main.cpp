//==================================================================================//
#include <Arduino.h>
#include <CAN.h>
#include <ESP32Servo.h>

Servo serv;

#define TX_GPIO_NUM   17  // Connects to CTX
#define RX_GPIO_NUM   16 // Connects to CRX

int count= 0;
int pos;

//==================================================================================//

void setup() {
  Serial.begin(9600);
  while (!Serial);
  delay (1000);

  CAN.setPins(RX_GPIO_NUM, TX_GPIO_NUM);
  Serial.println ("CAN Receiver/Receiver");

  serv.attach(19);
  // Set the pins
  
  // start the CAN bus at 500 kbps
  if (!CAN.begin (500E3)) {
    Serial.println ("Starting CAN failed!");
    while (1);
  }
  else {
    Serial.println ("CAN Initialized");
  }
}

void myFunction() {
  for (pos = 45; pos <= 145; pos ++) { // goes from 45 degrees to 90 degrees
    // in steps of 1 degree
    serv.write(pos);              // tell servo to go to position in variable 'pos'
    delay(15);                       // waits 15ms for the servo to reach the position
  }

  for (pos = 145; pos >= 45; pos --) { // goes from 180 degrees to 0 degrees
    serv.write(pos);              // tell servo to go to position in variable 'pos'
    delay(15);                       // waits 15ms for the servo to reach the position
  }
}
void canReceiver() {
  // try to parse packet
  int packetSize = CAN.parsePacket();

  if (packetSize) {
    // received a packet
    Serial.print ("Received ");

    if (CAN.packetExtended()) {
      Serial.print ("extended ");
    }

    if (CAN.packetRtr()) {
      // Remote transmission request, packet contains no data
      Serial.print ("RTR ");
    }

    Serial.print ("packet with id 0x");
    Serial.print (CAN.packetId(), HEX);

    CAN.filter(0x12);
    myFunction();
    if (CAN.packetRtr()) {
      Serial.print (" and requested length ");
      Serial.println (CAN.packetDlc());
    } else {
      Serial.print (" and length ");
      Serial.println (packetSize);

      // only print packet data for non-RTR packets
      
      while (CAN.available()) {
        Serial.print ((char) CAN.read());
      }
      Serial.println();
    }

    Serial.println();
  }
}


// put function definitions here:
void loop() {
  canReceiver();
  
}

//==================================================================================//
