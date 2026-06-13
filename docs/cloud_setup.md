# Cloud Dashboard Setup Guide

This document describes how to configure external cloud services (ThingSpeak, Blynk, and public MQTT brokers) to log, monitor, and visualize telemetry streamed from the ESP32 node.

---

## 1. ThingSpeak IoT Platform Configuration

ThingSpeak is an open-source IoT analytics platform service that allows you to aggregate, visualize, and analyze live data streams in the cloud.

### Step-by-Step Setup:
1. **Create Account**: Visit [ThingSpeak](https://thingspeak.com/) and register a MathWorks account.
2. **Create Channel**: Go to **Channels** -> **My Channels** -> click **New Channel**.
3. **Configure Channel Fields**:
   * Name: `IoT Air Quality Station`
   * Check and rename the following fields:
     * **Field 1**: `Temperature`
     * **Field 2**: `Humidity`
     * **Field 3**: `MQ135 Gas Raw`
     * **Field 4**: `PM2.5 Particulates`
     * **Field 5**: `PM10 Particulates`
4. **Save Channel**: Scroll down and click **Save Channel**.
5. **Get Write API Key**:
   * Click the **API Keys** tab.
   * Copy the **Write API Key**.
   * Replace the placeholder value in the ESP32 code: `ts_api_key = "YOUR_WRITE_API_KEY"`.
6. **Customize Visualizations**:
   * Under the **Private View** tab, you can click **Add Widget** to add Gauges or numerical displays for real-time parameters alongside the default line charts.

---

## 2. Blynk IoT Platform Configuration

Blynk allows you to design custom iOS and Android mobile applications to control and read IoT sensors remotely.

### Datastream Pin Mappings:
Configure the following Virtual Pins inside the Blynk Console:

* **V1 (Temperature)**: Double/Float, unit `°C`, range `-40 to 80`
* **V2 (Humidity)**: Double/Float, unit `%`, range `0 to 100`
* **V3 (MQ135 Gas)**: Integer, range `0 to 4095`
* **V4 (PM2.5)**: Double/Float, unit `µg/m³`, range `0 to 500`
* **V5 (PM10)**: Double/Float, unit `µg/m³`, range `0 to 1000`

### Step-by-Step Dashboard Setup:
1. Log in to [Blynk Console](https://blynk.cloud/).
2. Create a new **Template** -> select hardware **ESP32** and connection type **WiFi**.
3. Create the 5 Datastreams matching the Virtual Pins listed above.
4. Go to **Web Dashboard** tab:
   * Drag and drop **Gauges** for V1, V2, and V3.
   * Drag and drop **Labeled Value** widgets for V4 and V5.
   * Drag and drop a **SuperChart** widget, set data source to V4 and V3 to monitor logs over time.
5. In the templates, copy the **Template ID**, **Template Name**, and **Auth Token** given in the Blynk Device Info panel.
6. Insert those tokens at the top of your ESP32 code if you choose to compile with Blynk libraries:
   ```cpp
   #define BLYNK_TEMPLATE_ID   "TMPL..."
   #define BLYNK_TEMPLATE_NAME "Air Quality Dashboard"
   #define BLYNK_AUTH_TOKEN    "YourAuthToken"
   ```

---

## 3. Public MQTT Broker (HiveMQ) Setup

MQTT (Message Queuing Telemetry Transport) is a lightweight network protocol designed for publisher/subscriber topologies.

### Connection Parameters:
* **Broker Address**: `broker.hivemq.com` (Free public test broker)
* **Port**: `1883` (Unencrypted TCP port)
* **Topic**: `airquality/node01/data`

### Subscribing to Stream:
You can verify that your ESP32 is successfully publishing JSON payloads using external tools:

1. **MQTT Explorer**: Download [MQTT Explorer](http://mqtt-explorer.com/).
2. Connect to host `broker.hivemq.com` on port `1883`.
3. Add a subscription to topic: `airquality/node01/#` or click the root node to view incoming payloads.
4. The payload should appear as a formatted JSON:
   ```json
   {
     "temperature": 26.54,
     "humidity": 58.21,
     "gas_raw": 612,
     "pm25": 10.45,
     "pm10": 16.72,
     "category": "Good"
   }
   ```
> [!WARNING]
> Public brokers like `broker.hivemq.com` are open to the public and do not require usernames or passwords. Do not transmit sensitive data (such as private Wi-Fi credentials or locations) over public MQTT brokers. For production, switch to authenticated brokers like AWS IoT Core, Adafruit IO, or a self-hosted Mosquitto instance with TLS.
