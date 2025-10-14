#include <SPI.h>
#include <MFRC522.h>
#include <ArduinoJson.h>
#include <LiquidCrystal.h>        // LCD-Bibliothek hinzugefügt

/* ---------- Pin-Definitionen ---------- */
// RFID Setup
constexpr uint8_t RST_PIN = 9;
constexpr uint8_t SS_PIN  = 10;

MFRC522 mfrc522(SS_PIN, RST_PIN);

/* ---------- LCD-Pin-Belegung (4-Bit-Modus) ---------- */
constexpr uint8_t LCD_RS = 2;   // Register-Select
constexpr uint8_t LCD_EN = 3;   // Enable
constexpr uint8_t LCD_D4 = 4;   // Daten-Bit 4
constexpr uint8_t LCD_D5 = 5;   // Daten-Bit 5
constexpr uint8_t LCD_D6 = 6;   // Daten-Bit 6
constexpr uint8_t LCD_D7 = 7;   // Daten-Bit 7

// Erzeuge das LCD-Objekt (RS, EN, D4, D5, D6, D7)
LiquidCrystal lcd(LCD_RS, LCD_EN, LCD_D4, LCD_D5, LCD_D6, LCD_D7);

/* ---------- Anzeige-Timing ---------- */
const unsigned long DISPLAY_TIME_MS = 3000UL;   // 3s Anzeige für bessere Lesbarkeit
unsigned long lastDisplayChange = 0UL;
bool displayingCard = false;

void setup() {
  Serial.begin(115200);
  while (!Serial) ;               // (nur bei manchen Boards nötig)

  /* ---- SPI + RFID ---- */
  SPI.begin();                    // SPI-Bus starten
  mfrc522.PCD_Init();             // RC522 initialisieren

  /* ---- LCD (parallel) ---- */
  lcd.begin(16, 2);               // 16 Spalten, 2 Zeilen
  lcd.clear();
  showReadyMessage();
}

void loop() {
  /* ---------- RFID-Erkennung ---------- */
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    
    // Convert UID to hex string
    String uid = "";
    for (byte i = 0; i < mfrc522.uid.size; i++) {
      if (mfrc522.uid.uidByte[i] < 0x10) uid += "0";
      uid += String(mfrc522.uid.uidByte[i], HEX);
    }
    uid.toUpperCase();
    
    // Backend-kompatibles Format: "RFID" + UID
    String rfidTag = "RFID" + uid;
    
    // Minimales JSON nur für Door-Pi Python Script
    StaticJsonDocument<100> doc;
    doc["rfid_tag"] = rfidTag;
    doc["timestamp"] = millis();
    
    // Send JSON to serial
    serializeJson(doc, Serial);
    Serial.println();
    
    /* ----- LCD-Feedback ----- */
    displayCardDetected(rfidTag);
    
    /* ----- Tag zurücksetzen ----- */
    mfrc522.PICC_HaltA();          // Karte in Ruhe-Modus
    mfrc522.PCD_StopCrypto1();     // Verschlüsselung abschalten
    delay(300);                    // Entprell-Pause
  }

  /* ---------- Display-Timeout-Handling ---------- */
  handleDisplayTimeout();
}

String getCardType() {
  MFRC522::PICC_Type piccType = mfrc522.PICC_GetType(mfrc522.uid.sak);
  return String(mfrc522.PICC_GetTypeName(piccType));
}

/* ---------- LCD-Hilfsfunktionen ---------- */
void showReadyMessage() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("RFID Scanner");
  lcd.setCursor(0, 1);
  lcd.print("Ready...");
  displayingCard = false;
  lastDisplayChange = millis();
}

void displayCardDetected(String rfidTag) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Card Detected!");
  
  // Zeile 2: RFID-Tag anzeigen (verkürzt falls zu lang)
  lcd.setCursor(0, 1);
  if (rfidTag.length() <= 16) {
    lcd.print(rfidTag);
  } else {
    // Zeige die letzten 16 Zeichen für bessere Lesbarkeit
    lcd.print(rfidTag.substring(rfidTag.length() - 16));
  }
  
  displayingCard = true;
  lastDisplayChange = millis();
}

void handleDisplayTimeout() {
  if (displayingCard && (millis() - lastDisplayChange > DISPLAY_TIME_MS)) {
    showReadyMessage();
  }
}