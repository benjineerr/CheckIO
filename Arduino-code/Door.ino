#include <SPI.h>
#include <MFRC522.h>
#include <ArduinoJson.h>

// RFID Setup
#define RST_PIN         9
#define SS_PIN          10

MFRC522 mfrc522(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(115200);
  SPI.begin();
  mfrc522.PCD_Init();
  
  Serial.println("{\"status\":\"ready\",\"device\":\"door_scanner\"}");
}

void loop() {
  // Look for new cards
  if (!mfrc522.PICC_IsNewCardPresent()) {
    return;
  }

  // Select one of the cards
  if (!mfrc522.PICC_ReadCardSerial()) {
    return;
  }

  // Create JSON object
  StaticJsonDocument<200> doc;
  doc["device"] = "door_scanner";
  doc["action"] = "rfid_scan";
  
  // Convert UID to hex string
  String uid = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    uid += String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : "");
    uid += String(mfrc522.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();
  
  doc["rfid_uid"] = uid;
  doc["card_type"] = getCardType();
  
  // Send JSON to serial
  serializeJson(doc, Serial);
  Serial.println();
  
  // Halt PICC
  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();
  
  delay(1000); // Prevent spam
}

String getCardType() {
  MFRC522::PICC_Type piccType = mfrc522.PICC_GetType(mfrc522.uid.sak);
  return String(mfrc522.PICC_GetTypeName(piccType));
}