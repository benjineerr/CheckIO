// Benötigte Standard-Bibliothek für parallele LCDs einbinden
#include <LiquidCrystal.h>

// --- Konfiguration ---
const int buttonPinWeiter = 9;
const int buttonPinZurueck = 10;
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

// --- Globale Variablen ---
const int MAX_DATASETS = 20; // Maximal erwartete Anzahl an Datensätzen
String datensaetze[MAX_DATASETS];
int anzahlDatensaetze = 0; // Wird dynamisch gefüllt
int aktuellerIndex = 0;

unsigned long letzteButtonZeit = 0;
unsigned int entprellVerzoegerung = 250;

String serialBuffer = ""; // Puffer für eingehende serielle Daten

// Setup-Funktion
void setup() {
  lcd.begin(16, 2);
  Serial.begin(9600); // Serielle Kommunikation starten
  
  pinMode(buttonPinWeiter, INPUT_PULLUP);
  pinMode(buttonPinZurueck, INPUT_PULLUP);

  lcd.print("Warte auf Daten");
  lcd.setCursor(0, 1);
  lcd.print("vom Raspberry Pi...");

  // Kurze Verzögerung, damit der Pi Zeit hat, die serielle Verbindung zu erkennen
  delay(2000); 
  
  // Daten vom Pi anfordern
  Serial.println("GET_DATA");
}

// Loop-Funktion
void loop() {
  // Auf Antwort vom Pi warten
  checkSerial();

  // Knöpfe abfragen (funktioniert nur, wenn Daten geladen wurden)
  if (anzahlDatensaetze > 0) {
    handleButtons();
  }
}

// NEUE Funktion: Eingehende serielle Daten prüfen
void checkSerial() {
  while (Serial.available()) {
    char zeichen = (char)Serial.read();
    
    // Wenn das Newline-Zeichen ankommt, ist die Nachricht komplett
    if (zeichen == '\n') {
      parseData(serialBuffer); // Die empfangenen Daten verarbeiten
      serialBuffer = ""; // Puffer für die nächste Nachricht leeren
    } else {
      serialBuffer += zeichen; // Zeichen zum Puffer hinzufügen
    }
  }
}

// NEUE Funktion: Den Datenstring vom Pi verarbeiten
void parseData(String data) {
  // Zuerst alle alten Datensätze löschen
  anzahlDatensaetze = 0;
  
  int lastDelimiter = -1;
  for (int i = 0; i < data.length(); i++) {
    // Wenn ein Trennzeichen gefunden wird...
    if (data.charAt(i) == '|') {
      // Füge den Teilstring zur Liste hinzu
      datensaetze[anzahlDatensaetze] = data.substring(lastDelimiter + 1, i);
      anzahlDatensaetze++;
      lastDelimiter = i;
      
      // Abbruch, wenn das Array voll ist
      if (anzahlDatensaetze >= MAX_DATASETS) break;
    }
  }
  
  // Den letzten Datensatz nach dem letzten Trennzeichen hinzufügen
  if (anzahlDatensaetze < MAX_DATASETS) {
    datensaetze[anzahlDatensaetze] = data.substring(lastDelimiter + 1);
    anzahlDatensaetze++;
  }
  
  // LCD mit dem ersten Datensatz aktualisieren
  aktuellerIndex = 0;
  updateLCD();
}

// Knopf-Logik (ausgelagert in eine eigene Funktion)
void handleButtons() {
  int stateWeiter = digitalRead(buttonPinWeiter);
  int stateZurueck = digitalRead(buttonPinZurueck);

  if (millis() - letzteButtonZeit > entprellVerzoegerung) {
    if (stateWeiter == LOW) {
      aktuellerIndex = (aktuellerIndex + 1) % anzahlDatensaetze;
      updateLCD();
      letzteButtonZeit = millis();
    }

    if (stateZurueck == LOW) {
      aktuellerIndex--;
      if (aktuellerIndex < 0) {
        aktuellerIndex = anzahlDatensaetze - 1;
      }
      updateLCD();
      letzteButtonZeit = millis();
    }
  }
}

// LCD-Anzeige aktualisieren
void updateLCD() {
  lcd.clear();
  lcd.setCursor(0, 0);
  if (anzahlDatensaetze > 0) {
    lcd.print(datensaetze[aktuellerIndex]);
  } else {
    lcd.print("Keine Daten!");
  }
}