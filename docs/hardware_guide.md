# Hardware Implementation & Connection Guide

This guide details the components used, their electrical working principles, and the exact wiring connections required to assemble the physical hardware station.

---

## 1. Sensor Profiles & Principles

### A. MQ135 Air Quality Sensor
* **Target Pollutants**: CO₂, NH₃, NOₓ, Benzene, Smoke, Alcohol.
* **Working Principle**: The sensor contains a micro-heating element and a tin dioxide ($SnO_2$) semiconductor layer. In clean air, $SnO_2$ has low conductivity. When combustible/pollutant gases are present, they react with oxygen adsorbed on the sensor surface, releasing electrons back into the conduction band. This decreases electrical resistance, which increases the analog output voltage.
* **Calibration Note**: The MQ135 is sensitive to temperature and humidity. A DHT22 sensor is used in parallel to calibrate the readings via software. Before first-time use, burn in the sensor for 24-48 hours to stabilize the internal heater.

### B. SDS011 / PMS5003 Dust & Particulate Sensor
* **Target Pollutants**: Particulate Matter (PM2.5 and PM10).
* **Working Principle**: Laser light scattering detection. A laser diode projects light into a small chamber. When particles (dust, soot, pollen) pass through the chamber via the internal fan, the light scatters. A photodiode detector measures the intensity and pattern of the scattered light. Microprocessor algorithms convert this light signal into particle counts and estimate the mass concentrations of PM2.5 and PM10 in micrograms per cubic meter ($\mu g/m^3$).
* **Data Transmission**: Outputs data continuously over UART Serial at a 9600 baud rate.

### C. DHT22 / AM2302 Temperature & Humidity Sensor
* **Target Parameters**: Ambient Temperature & Relative Humidity.
* **Working Principle**:
  * **Humidity**: Utilizes a capacitive sensor element containing two electrodes with a moisture-holding substrate between them. As moisture is absorbed, the dielectric constant changes, shifting the electrical capacitance.
  * **Temperature**: Uses a high-precision Negative Temperature Coefficient (NTC) thermistor (resistance decreases as temperature rises).
* **Communication**: Employs a custom single-wire digital bus protocol. Requires a 10 kΩ pull-up resistor from the data pin to VCC.

---

## 2. Complete Wiring Diagram (Pin Connections)

| Sensor / Actuator | Sensor Pin | ESP32 Pin | Arduino UNO Pin | Remarks |
| :--- | :--- | :--- | :--- | :--- |
| **MQ135** | VCC | 5V | 5V | Needs stable 5V for heating coil |
| | GND | GND | GND | Shared ground |
| | AO (Analog) | GPIO 34 (ADC1) | A0 | ESP32 requires GPIO 32-39 for ADC |
| **DHT22** | VCC | 3.3V / 5V | 5V | Power supply |
| | DATA | GPIO 4 | Pin 2 | Place a 10kΩ resistor between DATA & VCC |
| | GND | GND | GND | Shared ground |
| **SDS011** | VCC | 5V | 5V | Internal fan requires 5V to rotate |
| | GND | GND | GND | Shared ground |
| | TX | GPIO 16 (RX2) | Pin 3 (SoftwareSerial) | Serial RX line |
| | RX | GPIO 17 (TX2) | Pin 4 (SoftwareSerial) | Serial TX line |
| **Buzzer** | Positive (+) | GPIO 22 | Pin 5 | Active buzzer alarm |
| | Negative (-) | GND | GND | Shared ground |
| **LED Green** | Anode (+) | GPIO 18 | Pin 6 | Good Air Indicator (needs 220Ω resistor) |
| | Cathode (-) | GND | GND | Shared ground |
| **LED Yellow** | Anode (+) | GPIO 19 | Pin 7 | Moderate Air Indicator (needs 220Ω resistor) |
| | Cathode (-) | GND | GND | Shared ground |
| **LED Red** | Anode (+) | GPIO 21 | Pin 8 | Poor/Hazardous Indicator (needs 220Ω resistor) |
| | Cathode (-) | GND | GND | Shared ground |
| **OLED (SSD1306)** | VCC | 3.3V | 3.3V | Optional visual display |
| | GND | GND | GND | Shared ground |
| | SCL | GPIO 22 (I2C) | A5 | I2C clock line |
| | SDA | GPIO 21 (I2C) | A4 | I2C data line |

---

## 3. Circuit Assembly Schematic

Below is the text representation of the electrical node:

```
                  +-----------------------------------+
                  |            ESP32 MCU              |
                  +-----------------------------------+
                  | [5V]   [3.3V]   [GND]   [GPIO34]  |
                  +---+------+--------+--------+------+
                      |      |        |        |
    +-----------------+      |        |        |
    | (5V)                   |        |        | (ADC1)
    |                        |        |        |
+---+---+                  +-+-+    +-+-+    +-+-+
|       |                  |   |    |   |    |   |
|MQ135  |                  |DHT|    |SDS|    |LED| <-- (Through 220 Ohm resistors)
|       |                  |22 |    |011|    |Red| -> GPIO 21
+---+---+                  +-+-+    +-+-+    |Yel| -> GPIO 19
    |                        |        |      |Grn| -> GPIO 18
    | (GND)                  |        |      +---+
    +------------------------+--------+
```
