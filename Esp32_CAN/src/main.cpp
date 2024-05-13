//==================================================================================//
#include <Arduino.h>
#include <CAN.h>

#define TX_GPIO_NUM   17  // Connects to CTX
#define RX_GPIO_NUM   16 // Connects to CRX

const int buzz_pin= 18;
const int blink_pin= 22;
int count=0;
//==================================================================================//


void buzz() {
  digitalWrite(buzz_pin, HIGH);
  for (int i=0; i<4; i++) {
    digitalWrite(blink_pin,HIGH);
    delay(1000);
    digitalWrite(blink_pin,LOW);
    delay(1000);
  }
  digitalWrite(buzz_pin, LOW);
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
    buzz();

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


void setup() {
  
  Serial.begin(9600);
  while (!Serial);
  delay (1000);

  CAN.setPins(RX_GPIO_NUM, TX_GPIO_NUM);
  Serial.println ("CAN Receiver/Receiver");
  

  // Set the pins
  pinMode(buzz_pin, OUTPUT);
  pinMode(blink_pin, OUTPUT);
  
  // start the CAN bus at 500 kbps
  if (!CAN.begin (500E3)) {
    Serial.println ("Starting CAN failed!");
    while (1);
  }
  else {
    Serial.println ("CAN Initialized");
    CAN.filter(0x11);
  }
}
// put function definitions here:
void loop() {
  canReceiver();
}

//==================================================================================//
