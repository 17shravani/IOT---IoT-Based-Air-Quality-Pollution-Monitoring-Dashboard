import time
import json
import random
import os
import sys
import paho.mqtt.client as mqtt

# Ensure parent directory is in path to import simulator
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from python_simulation.simulator import AirQualitySimulator

# MQTT Broker Details
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "airquality/node01/data"

def main():
    print("==================================================")
    print(" 📡 IoT AIR QUALITY TELEMETRY PUBLISHER (MOCK NODE) 📡")
    print("==================================================")
    print(f"Connecting to broker: {BROKER} on port {PORT}...")
    
    client = mqtt.Client()
    
    try:
        client.connect(BROKER, PORT, 60)
        print("Connected successfully!")
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    # Start loop
    client.loop_start()
    
    simulator = AirQualitySimulator()
    print(f"Publishing data to topic '{TOPIC}' every 3 seconds...")
    print("Press Ctrl+C to terminate.")
    print("-" * 50)
    
    # Alternate simulation modes over time to show spikes on the web dashboard
    step = 0
    try:
        while True:
            # Change scenarios periodically to trigger warning widgets on UI
            if 10 < step <= 25:
                simulator.set_mode("gas_leak")
            elif 35 < step <= 55:
                simulator.set_mode("wildfire")
            elif 65 < step <= 75:
                simulator.set_mode("heavy_rain")
            elif step > 90:
                simulator.set_mode("clean_air")
                if step > 105:
                    step = 0  # loop back to start
            else:
                simulator.set_mode("normal")
                
            reading = simulator.get_reading()
            payload = json.dumps(reading)
            
            print(f"[TX] Mode: {reading['mode'].upper()} | AQI: {reading['aqi']} | Gas: {reading['gas_raw']} | Temp: {reading['temperature']}°C")
            client.publish(TOPIC, payload)
            
            step += 1
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\nStopping publisher...")
    finally:
        client.loop_stop()
        client.disconnect()
        print("Disconnected. Done.")

if __name__ == "__main__":
    main()
