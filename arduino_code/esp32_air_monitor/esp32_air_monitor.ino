/**
 * @file esp32_air_monitor.ino
 * @brief IoT-Based Air Quality & Pollution Monitoring System
 * 
 * Target Microcontroller: ESP32 (DevKit v1)
 * Sensors: MQ135 (Gas/CO2), DHT22 (Temp/Hum), SDS011 (PM2.5/PM10 via Serial2)
 * Actuators: RGB LEDs (or individual LEDs for AQI categories), Active Buzzer
 * Connectivity: Wi-Fi, MQTT (JSON payload), ThingSpeak (HTTP GET)
 * 
 * Hardware Connections:
 * - MQ135: Analog Out -> GPIO 34 (ADC1_CH6)
 * - DHT22: Data Out -> GPIO 4 (10k Pull-up Resistor)
 * - SDS011: TX -> GPIO 16 (RX2), RX -> GPIO 17 (TX2)
 * - LED Green (Good): GPIO 18
 * - LED Yellow (Moderate): GPIO 19
 * - LED Red (Poor/Hazardous): GPIO 21
 * - Buzzer (Alert): GPIO 22
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

// --- PIN DEFINITIONS ---
#define MQ135_PIN      34  // Analog Input pin
#define DHTPIN         4   // Digital pin for DHT22
#define DHTTYPE        DHT22

#define LED_GREEN      18  // Good Air Quality
#define LED_YELLOW     19  // Moderate Air Quality
#define LED_RED        21  // Poor / Hazardous Air Quality
#define BUZZER_PIN     22  // Buzzer alert

#define RX2            16  // SDS011 TX connected to ESP32 RX2
#define TX2            17  // SDS011 RX connected to ESP32 TX2

// --- WIFI & CLOUD CONFIGURATIONS ---
// To use these, replace with your network credentials and API keys or use .env files during upload.
const char* ssid          = "Your_SSID";
const char* password      = "Your_Password";
const char* mqtt_server   = "broker.hivemq.com";
const int   mqtt_port     = 1883;
const char* mqtt_client_id = "ESP32_AirQualityNode_01";
const char* mqtt_topic     = "airquality/node01/data";

// ThingSpeak Fallback Configurations
const char* ts_server     = "api.thingspeak.com";
const char* ts_api_key    = "YOUR_THINGSPEAK_WRITE_API_KEY"; // Replace with your Write API Key

// --- INSTANCE DECLARATIONS ---
DHT dht(DHTPIN, DHTTYPE);
WiFiClient espClient;
PubSubClient mqtt_client(espClient);

// --- GLOBAL VARIABLES ---
float temperature = 0.0;
float humidity = 0.0;
int gas_raw = 0;
float pm25 = 0.0;
float pm10 = 0.0;
String air_category = "Unknown";
unsigned long last_transmission = 0;
const unsigned long transmission_interval = 15000; // Send data every 15 seconds

// --- FUNCTION PROTOTYPES ---
void setupWiFi();
void connectMQTT();
void readSDS011(float &pm25_val, float &pm10_val);
String classifyAirQuality(int gas, float pm25_val);
void setAlerts(String category);
void sendToThingSpeak(float t, float h, int g, float p25, float p10, String cat);

void setup() {
  Serial.begin(115200);
  
  // Initialize SDS011 Serial Connection (Serial2)
  Serial2.begin(9600, SERIAL_8N1, RX2, TX2);
  
  // Pin modes
  pinMode(MQ135_PIN, INPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  
  // Set all indicators low at startup
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_RED, LOW);
  digitalWrite(BUZZER_PIN, LOW);
  
  // Initialize DHT Sensor
  dht.begin();
  
  Serial.println("\n[SYSTEM START] IoT Air Quality Monitoring Station");
  
  // WiFi Connection
  setupWiFi();
  
  // MQTT Server Setup
  mqtt_client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  // Ensure WiFi and MQTT stay connected
  if (WiFi.status() != WL_CONNECTED) {
    setupWiFi();
  }
  
  if (!mqtt_client.connected()) {
    connectMQTT();
  }
  mqtt_client.loop();
  
  // Read SDS011 UART Stream constantly to flush buffer and capture last reading
  readSDS011(pm25, pm10);

  // Periodic sensor read and cloud transmission
  if (millis() - last_transmission >= transmission_interval) {
    last_transmission = millis();
    
    // Read Temperature and Humidity
    float temp_read = dht.readTemperature();
    float hum_read = dht.readHumidity();
    if (!isnan(temp_read)) temperature = temp_read;
    if (!isnan(hum_read)) humidity = hum_read;
    
    // Read MQ135 raw analog value (0 - 4095 on ESP32 12-bit ADC)
    gas_raw = analogRead(MQ135_PIN);
    
    // Classify air quality
    air_category = classifyAirQuality(gas_raw, pm25);
    
    // Drive LED and Buzzer indicators
    setAlerts(air_category);
    
    // Print to Serial Monitor
    Serial.println("==================================================");
    Serial.print("Timestamp (ms): "); Serial.println(millis());
    Serial.print("Temperature:    "); Serial.print(temperature); Serial.println(" *C");
    Serial.print("Humidity:       "); Serial.print(humidity); Serial.println(" %");
    Serial.print("MQ135 Gas Raw:  "); Serial.print(gas_raw); Serial.println(" / 4095");
    Serial.print("PM2.5 Dust:     "); Serial.print(pm25); Serial.println(" ug/m3");
    Serial.print("PM10 Dust:      "); Serial.print(pm10); Serial.println(" ug/m3");
    Serial.print("AQI Category:   "); Serial.println(air_category);
    Serial.println("==================================================");
    
    // Publish MQTT Payload (JSON)
    if (mqtt_client.connected()) {
      char payload[256];
      snprintf(payload, sizeof(payload), 
        "{\"temperature\":%.2f,\"humidity\":%.2f,\"gas_raw\":%d,\"pm25\":%.2f,\"pm10\":%.2f,\"category\":\"%s\"}",
        temperature, humidity, gas_raw, pm25, pm10, air_category.c_str());
      
      if (mqtt_client.publish(mqtt_topic, payload)) {
        Serial.println("[MQTT] Data published successfully.");
      } else {
        Serial.println("[MQTT] Failed to publish data.");
      }
    }
    
    // ThingSpeak Fallback Upload
    sendToThingSpeak(temperature, humidity, gas_raw, pm25, pm10, air_category);
  }
}

// --- FUNCTION DEFINITIONS ---

void setupWiFi() {
  delay(10);
  Serial.print("[WIFI] Connecting to SSID: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  int retry_count = 0;
  while (WiFi.status() != WL_CONNECTED && retry_count < 20) {
    delay(500);
    Serial.print(".");
    retry_count++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WIFI] Connected! IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n[WIFI] Connection Failed. Operating in Offline/Local Mode.");
  }
}

void connectMQTT() {
  int retry_count = 0;
  while (!mqtt_client.connected() && retry_count < 3) {
    Serial.print("[MQTT] Attempting connection to broker: ");
    Serial.println(mqtt_server);
    
    if (mqtt_client.connect(mqtt_client_id)) {
      Serial.println("[MQTT] Connected to Broker!");
    } else {
      Serial.print("[MQTT] Connection failed, state=");
      Serial.print(mqtt_client.state());
      Serial.println(". Retrying in 5 seconds...");
      delay(5000);
      retry_count++;
    }
  }
}

/**
 * @brief Parses SDS011 UART packet.
 * Protocol format (10 Bytes):
 * Byte 0: Header 0xAA
 * Byte 1: Command 0xC0
 * Byte 2: PM2.5 Low Byte
 * Byte 3: PM2.5 High Byte
 * Byte 4: PM10 Low Byte
 * Byte 5: PM10 High Byte
 * Byte 6: ID Byte 1
 * Byte 7: ID Byte 2
 * Byte 8: Checksum (Low 8-bits of sum of Bytes 2 to 7)
 * Byte 9: Tail 0xAB
 */
void readSDS011(float &pm25_val, float &pm10_val) {
  while (Serial2.available() >= 10) {
    byte header = Serial2.read();
    if (header == 0xAA) {
      byte cmd = Serial2.read();
      if (cmd == 0xC0) {
        byte data[8];
        Serial2.readBytes(data, 8);
        
        // Validate Checksum
        byte checksum = 0;
        for (int i = 0; i < 6; i++) {
          checksum += data[i];
        }
        
        if (checksum == data[6] && data[7] == 0xAB) {
          // PM2.5 value (ug/m3) = ((High Byte * 256) + Low Byte) / 10
          pm25_val = ((data[1] * 256.0) + data[0]) / 10.0;
          // PM10 value (ug/m3) = ((High Byte * 256) + Low Byte) / 10
          pm10_val = ((data[3] * 256.0) + data[2]) / 10.0;
        }
      }
    }
  }
}

/**
 * @brief Categorizes the current Air Quality according to gas concentration and particulate levels.
 */
String classifyAirQuality(int gas, float pm25_val) {
  // Simple indexing based on analog readings and EPA breakpoints for PM2.5
  // MQ135: Good (<800), Moderate (800-1500), Poor (1500-2500), Hazardous (>2500)
  // PM2.5: Good (<12 ug/m3), Moderate (12-35.4 ug/m3), Poor (35.4-150 ug/m3), Hazardous (>150 ug/m3)
  
  if (gas > 2500 || pm25_val > 150.0) {
    return "Hazardous";
  } else if (gas > 1500 || pm25_val > 35.4) {
    return "Poor";
  } else if (gas > 800 || pm25_val > 12.0) {
    return "Moderate";
  } else {
    return "Good";
  }
}

/**
 * @brief Drives indicator LEDs and alarms based on air quality severity.
 */
void setAlerts(String category) {
  if (category == "Good") {
    digitalWrite(LED_GREEN, HIGH);
    digitalWrite(LED_YELLOW, LOW);
    digitalWrite(LED_RED, LOW);
    digitalWrite(BUZZER_PIN, LOW); // No alarm
  } 
  else if (category == "Moderate") {
    digitalWrite(LED_GREEN, LOW);
    digitalWrite(LED_YELLOW, HIGH);
    digitalWrite(LED_RED, LOW);
    digitalWrite(BUZZER_PIN, LOW); // No alarm, only warning light
  } 
  else if (category == "Poor") {
    digitalWrite(LED_GREEN, LOW);
    digitalWrite(LED_YELLOW, LOW);
    digitalWrite(LED_RED, HIGH);
    
    // Slow warning beep
    digitalWrite(BUZZER_PIN, HIGH);
    delay(100);
    digitalWrite(BUZZER_PIN, LOW);
  } 
  else if (category == "Hazardous") {
    digitalWrite(LED_GREEN, LOW);
    digitalWrite(LED_YELLOW, LOW);
    
    // Rapid flashing red light and buzzer alarm
    for (int i = 0; i < 3; i++) {
      digitalWrite(LED_RED, HIGH);
      digitalWrite(BUZZER_PIN, HIGH);
      delay(80);
      digitalWrite(LED_RED, LOW);
      digitalWrite(BUZZER_PIN, LOW);
      delay(80);
    }
    digitalWrite(LED_RED, HIGH); // Keep Red on
  }
}

/**
 * @brief Transmits readings to ThingSpeak using direct HTTP GET requests.
 */
void sendToThingSpeak(float t, float h, int g, float p25, float p10, String cat) {
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    if (client.connect(ts_server, 80)) {
      // Form HTTP GET update string
      // Field 1: Temp, Field 2: Humidity, Field 3: MQ135 Gas, Field 4: PM2.5, Field 5: PM10
      String url = "/update?api_key=" + String(ts_api_key) +
                   "&field1=" + String(t) +
                   "&field2=" + String(h) +
                   "&field3=" + String(g) +
                   "&field4=" + String(p25) +
                   "&field5=" + String(p10);
      
      client.print(String("GET ") + url + " HTTP/1.1\r\n" +
                   "Host: " + ts_server + "\r\n" +
                   "Connection: close\r\n\r\n");
      
      unsigned long timeout = millis();
      while (client.available() == 0) {
        if (millis() - timeout > 5000) {
          Serial.println("[ThingSpeak] Server connection timeout.");
          client.stop();
          return;
        }
      }
      
      Serial.println("[ThingSpeak] Update packet sent successfully.");
      client.stop();
    } else {
      Serial.println("[ThingSpeak] Failed to connect to server.");
    }
  }
}
