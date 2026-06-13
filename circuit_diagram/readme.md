# Circuit Wiring Schematic

This folder contains the wiring schema and pinout mapping for connecting the multi-sensor node to the ESP32 microcontroller.

---

## 1. ASCII Circuit Schematic

```text
                                  +-------------------+
                                  |   ESP32 MCU Node  |
                                  +-------------------+
                                  | 5V  3.3V  GND  34 |
                                  +-+----+-----+---+--+
                                    |    |     |   |
         +--------------------------+    |     |   | (ADC1)
         | (5V)                          |     |   |
         v                               v     v   v
     +-------+                         +---+ +---+ +---+
     | MQ135 |                         |DHT| |SDS| |LED| (Pins 18, 19, 21)
     | (Gas) |                         |22 | |011| |   |--> Green LED (Good)  -> GPIO 18
     +-------+                         +---+ +---+ |   |--> Yellow LED (Mod)  -> GPIO 19
                                                   |   |--> Red LED (Alert)   -> GPIO 21
                                                   +---+
                                                     |
                                                     v
                                                +---------+
                                                | Buzzer  | -> GPIO 22
                                                +---------+
```

---

## 2. Pinout Configuration Table

| Sensor/Module | Module Pin | ESP32 Pin | Connection Purpose |
| :--- | :--- | :--- | :--- |
| **MQ135** | VCC | 5V | Sensor heater element power |
| | GND | GND | Shared ground reference |
| | AO (Analog Out) | GPIO 34 | Analog gas concentration reading |
| **DHT22** | VCC | 3.3V | Temperature & humidity power |
| | DATA | GPIO 4 | Digital telemetry (requires 10kΩ pull-up) |
| | GND | GND | Shared ground reference |
| **SDS011** | VCC | 5V | Internal laser fan power |
| | GND | GND | Shared ground reference |
| | TX | GPIO 16 (RX2) | Serial transfer line |
| | RX | GPIO 17 (TX2) | Serial receive line |
| **Active Buzzer** | Positive (+) | GPIO 22 | Alarm trigger output |
| | Negative (-) | GND | Ground |
| **Green LED** | Anode (+) | GPIO 18 | Status indicator (Good Air) |
| **Yellow LED** | Anode (+) | GPIO 19 | Status indicator (Moderate Air) |
| **Red LED** | Anode (+) | GPIO 21 | Status indicator (Poor/Hazardous Air) |
