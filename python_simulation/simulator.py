import time
import random
import math
from datetime import datetime

class AirQualitySimulator:
    """
    Simulates high-fidelity IoT air quality sensor readings.
    Models natural diurnal cycles (temperature and humidity),
    normal atmospheric drift, traffic rush-hour peaks, and industrial anomalies.
    """
    def __init__(self):
        # Base sensor states
        self.base_temp = 25.0       # Celsius
        self.base_hum = 60.0        # Percentage
        self.base_gas = 400         # MQ135 raw baseline (clear air)
        self.base_pm25 = 8.0        # ug/m3
        self.base_pm10 = 15.0       # ug/m3
        
        # Random walks (drift)
        self.gas_drift = 0.0
        self.pm25_drift = 0.0
        
        # Operational mode: 'normal', 'gas_leak', 'wildfire', 'heavy_rain', 'clean_air'
        self.mode = "normal"

    def set_mode(self, mode: str):
        """Changes the simulation mode to model specific events."""
        valid_modes = ["normal", "gas_leak", "wildfire", "heavy_rain", "clean_air"]
        if mode in valid_modes:
            self.mode = mode
        else:
            raise ValueError(f"Invalid mode. Choose from {valid_modes}")

    def calculate_aqi_pm25(self, pm25: float) -> int:
        """
        Calculates the Air Quality Index (AQI) for PM2.5 based on US EPA breakpoints.
        """
        # Breakpoints: [C_low, C_high, I_low, I_high]
        breakpoints = [
            (0.0, 12.0, 0, 50),
            (12.1, 35.4, 51, 100),
            (35.5, 55.4, 101, 150),
            (55.5, 150.4, 151, 200),
            (150.5, 250.4, 201, 300),
            (250.5, 500.4, 301, 500)
        ]
        
        for c_low, c_high, i_low, i_high in breakpoints:
            if c_low <= pm25 <= c_high:
                aqi = ((i_high - i_low) / (c_high - c_low)) * (pm25 - c_low) + i_low
                return round(aqi)
        
        if pm25 > 500.4:
            return 500
        return 0

    def classify_aqi(self, aqi: int) -> str:
        """Categorizes the AQI into index levels."""
        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Moderate"
        elif aqi <= 150:
            return "Unhealthy for Sensitive Groups"
        elif aqi <= 200:
            return "Unhealthy"
        elif aqi <= 300:
            return "Very Unhealthy"
        else:
            return "Hazardous"

    def get_reading(self, timestamp: datetime = None) -> dict:
        """
        Generates a sensor reading based on the simulation mode and current time.
        Models time-of-day variations (traffic peaks, temperature peaks).
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        hour = timestamp.hour + timestamp.minute / 60.0
        
        # 1. Diurnal cycle model (Sinusoidal temperature peaks around 2-3 PM, low at 4 AM)
        # Temp peak is offset by 14 hours.
        temp_cycle = 5.0 * math.sin(2.0 * math.pi * (hour - 8) / 24.0)
        humidity_cycle = -10.0 * math.sin(2.0 * math.pi * (hour - 8) / 24.0)
        
        temp = self.base_temp + temp_cycle + random.normalvariate(0, 0.2)
        hum = self.base_hum + humidity_cycle + random.normalvariate(0, 0.5)
        hum = max(0.0, min(100.0, hum)) # Clamp between 0 and 100
        
        # 2. Traffic peak model (spikes at 8-10 AM and 5-7 PM)
        traffic_factor = 0.0
        if 8.0 <= hour <= 10.0:
            # Peak at 9 AM
            traffic_factor = math.sin(math.pi * (hour - 8) / 2)
        elif 17.0 <= hour <= 19.0:
            # Peak at 6 PM
            traffic_factor = math.sin(math.pi * (hour - 17) / 2)
            
        traffic_gas_spike = 400.0 * traffic_factor
        traffic_pm_spike = 15.0 * traffic_factor
        
        # 3. Random walks/drift to represent background environmental fluctuation
        self.gas_drift += random.uniform(-10, 10)
        self.gas_drift = max(-100, min(100, self.gas_drift))
        
        self.pm25_drift += random.uniform(-1, 1)
        self.pm25_drift = max(-5.0, min(5.0, self.pm25_drift))
        
        # 4. Assemble readings according to mode
        gas = self.base_gas + self.gas_drift + traffic_gas_spike
        pm25 = self.base_pm25 + self.pm25_drift + traffic_pm_spike
        
        # Apply mode overrides
        if self.mode == "gas_leak":
            gas += random.uniform(1500, 3000) # Significant gas concentration jump
            pm25 += random.uniform(10, 30)
        elif self.mode == "wildfire":
            gas += random.uniform(1000, 2000)
            pm25 += random.uniform(180, 350)  # Extreme PM2.5 levels
        elif self.mode == "heavy_rain":
            gas -= random.uniform(50, 100)
            pm25 = max(1.0, pm25 * 0.15)       # Rain washes out particles
            temp -= 4.0                        # Temperature cools down
            hum = min(98.0, hum + 25.0)
        elif self.mode == "clean_air":
            gas = self.base_gas * 0.8          # Purified/natural forest air
            pm25 = self.base_pm25 * 0.4
            
        # Ensure outputs are within logical bounds
        gas = int(max(0, gas))
        pm25 = float(max(0.1, pm25))
        
        # PM10 is generally proportional to PM2.5 with a scale factor and noise
        pm10 = pm25 * 1.6 + random.normalvariate(0, 1.0)
        if self.mode == "wildfire":
            pm10 = pm25 * 2.2 + random.normalvariate(0, 5.0) # Ash and larger soot particles
        pm10 = float(max(0.2, pm10))
        
        # Calculate AQI and categorize
        aqi = self.calculate_aqi_pm25(pm25)
        category = self.classify_aqi(aqi)
        
        # Alerts triggering
        alert_triggered = False
        alert_msg = ""
        if aqi > 100:
            alert_triggered = True
            alert_msg = f"WARNING: {category} Air Quality (AQI {aqi}) detected!"
        if gas > 1500:
            alert_triggered = True
            alert_msg += (" " if alert_msg else "") + f"DANGER: High Combustible/Harmful Gas Level ({gas} Analog)!"
            
        return {
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": round(temp, 2),
            "humidity": round(hum, 2),
            "gas_raw": gas,
            "pm25": round(pm25, 2),
            "pm10": round(pm10, 2),
            "aqi": aqi,
            "category": category,
            "alert_triggered": alert_triggered,
            "alert_message": alert_msg,
            "mode": self.mode
        }
