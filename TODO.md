# All TODOs

- Guide to setup via git/ GitHub
- Setup database
- Setup web-based dashboards
- Arduino code
- Test Arduino serial connection
- Setup MQTT
- Arduino wiring
    **Teacher Node Arduino Wiring:**
    ```
    20x4 LCD (16-pin):             Arduino Uno:
    VSS -----------------> GND
    VDD -----------------> 5V
    V0 ------------------> 10kΩ potentiometer center (contrast)
    RS ------------------> Pin A0
    EN ------------------> Pin A1
    D4 ------------------> Pin A2
    D5 ------------------> Pin A3
    D6 ------------------> Pin A4
    D7 ------------------> Pin A5
    A -------------------> 5V (through 220Ω resistor)
    K -------------------> GND

    7-Segment Display:        Arduino Uno:
    Digit 1 -------------> Pin 10
    Digit 2 -------------> Pin 11
    Digit 3 -------------> Pin 12
    Digit 4 -------------> Pin 13
    Segment A -----------> Pin 2
    Segment B -----------> Pin 3
    Segment C -----------> Pin 4
    Segment D -----------> Pin 5
    Segment E -----------> Pin 6
    Segment F -----------> Pin 7
    Segment G -----------> Pin 8
    Segment DP ----------> Pin 9

    Status/Control:            Arduino Uno:
    Green LED -----------> Pin 0 (through 220Ω resistor)
    Red LED -------------> Pin 1 (through 220Ω resistor)
    Blue LED ------------> Pin 15 (through 220Ω resistor)
    Buzzer --------------> Pin 16
    Push Button ---------> Pin 17 (with pull-up resistor)
    ```

    **Door Node Arduino Wiring:**
    ```
    RC522 RFID Reader:        Arduino Uno:
    SDA/SS --------------> Pin 10
    SCK -----------------> Pin 13
    MOSI ----------------> Pin 11
    MISO ----------------> Pin 12
    RST -----------------> Pin 9
    3.3V ----------------> 3.3V
    GND -----------------> GND

    16x2 LCD (16-pin):        Arduino Uno:
    VSS -----------------> GND
    VDD -----------------> 5V
    V0 ------------------> 10kΩ potentiometer center (contrast)
    RS ------------------> Pin 2
    EN ------------------> Pin 3
    D4 ------------------> Pin 4
    D5 ------------------> Pin 5
    D6 ------------------> Pin 6
    D7 ------------------> Pin 7
    A -------------------> 5V (through 220Ω resistor)
    K -------------------> GND

    Status LEDs:                Arduino Uno:
    Green LED -----------> Pin A0 (through 220Ω resistor)
    Red LED -------------> Pin A1 (through 220Ω resistor)
    Buzzer --------------> Pin A2

    Note: 7-Segment display disabled due to pin conflicts with LCD
