// Random MAC + Timestamp Generator for Serial Debugging
// Gibt zufällige MAC-Adressen mit Unix-Timestamps aus, z. B.:
// [1728645123] 3A:7F:2C:B1:09:E4

void setup() {
  Serial.begin(115200);           // Serielle Verbindung starten
  randomSeed(analogRead(A0));     // Zufall initialisieren
}

void loop() {
  unsigned long timestamp = millis() / 1000 + 1728000000UL; // ungefährer Unix-Timestamp
  
  Serial.print("[");
  Serial.print(timestamp);
  Serial.print("] ");

  // Zufällige MAC-Adresse erzeugen
  for (int i = 0; i < 6; i++) {
    byte octet = random(0, 256);
    if (octet < 16) Serial.print("0"); // führende Null
    Serial.print(octet, HEX);
    if (i < 5) Serial.print(":");
  }

  Serial.println(); // Zeilenumbruch

  delay(1000); // Ausgabeintervall (in ms)
}
