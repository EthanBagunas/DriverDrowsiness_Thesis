//==================================================================================//

#include <CAN.h>
#include <Arduino.h>

#define TX_GPIO_NUM   21  // Connects to CTX
#define RX_GPIO_NUM   22 // Connects to CRX

//==================================================================================//

void setup() {
  Serial.begin(9600);
  while (!Serial);
  delay (1000);

  CAN.setPins(RX_GPIO_NUM, TX_GPIO_NUM);
  Serial.println ("CAN Receiver/Receiver");

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

void loop() {
  canReceiver();
}

//==================================================================================//
