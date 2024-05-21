//==================================================================================//
#include "header.h"
//==================================================================================//

void setup() {
  lcd.init();
  lcd.clear();
  lcd.backlight();
  serv.attach(serv_pin);
  serv.attach(serv_pin);
  
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
    CAN.filter(0x12);
  }
}  // end of setup

// put function definitions here:
void loop() {
canReceiver();
}
//==================================================================================//
