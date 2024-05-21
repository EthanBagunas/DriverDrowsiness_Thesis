
#include <Arduino.h>
#include <CAN.h>
#include <ESP32Servo.h>
#include <LiquidCrystal_I2C.h>
#include <Wire.h>


#define TX_GPIO_NUM   17  // Connects to CTX
#define RX_GPIO_NUM   16 // Connects to CRX

LiquidCrystal_I2C lcd(0x27,16,2);
Servo serv;

const int serv_pin =18;
int count= 0;
int pos;


void yawnLcd() {
  for (int i=0; i<5; i++) {
  // Print a message on both lines of the LCD.
    lcd.setCursor(2,0);   //Set cursor to character 2 on line 0
    lcd.print("Driver Sleepy!!!");
    lcd.setCursor(2,1);   //Move cursor to character 2 on line 1
    lcd.print("KEEP DISTANCE");
    delay(1000);
    lcd.clear();
    delay(1000);
  }
}
void yawnSpray() {
  for (pos = 45; pos <= 145; pos ++) { // goes from 45 degrees to 90 degrees
    // in steps of 1 degree
    serv.write(pos);              // tell servo to go to position in variable 'pos'
    delay(15);     
                      // waits 15ms for the servo to reach the position
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
    yawnSpray();
    yawnLcd();
    
    
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
