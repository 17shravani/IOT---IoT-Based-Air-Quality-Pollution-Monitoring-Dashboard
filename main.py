import os
import argparse
import time
import pandas as pd
from datetime import datetime, timedelta
from python_simulation.simulator import AirQualitySimulator
from python_simulation.analyzer import AirQualityAnalyzer

def print_banner():
    banner = """
========================================================================
   📡 IoT-BASED AIR QUALITY & POLLUTION MONITORING COMMAND CENTER 📡
========================================================================
    A high-fidelity simulation and analysis tool for environmental nodes.
    Supports real-time logging, AQI classification, and chart plotting.
========================================================================
"""
    print(banner)

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(description="IoT Air Quality CLI Simulator")
    parser.add_argument("--steps", type=int, default=10, help="Number of simulation steps to run")
    parser.add_argument("--mode", type=str, default="normal", 
                        choices=["normal", "gas_leak", "wildfire", "heavy_rain", "clean_air"],
                        help="Simulation scenario mode")
    parser.add_argument("--interval", type=float, default=1.0, help="Interval in seconds between simulation readings")
    parser.add_argument("--analyze", action="store_true", help="Compile logs and regenerate reports/charts after completion")
    parser.add_argument("--clear", action="store_true", help="Clear all historical logs before running")
    
    args = parser.parse_args()
    
    LOGS_FILE = "data/sensor_logs.csv"
    os.makedirs(os.path.dirname(LOGS_FILE), exist_ok=True)
    
    # Handle clear flag
    if args.clear:
        if os.path.exists(LOGS_FILE):
            os.remove(LOGS_FILE)
            print("[SYSTEM] Cleared historical logs database.")
            
    # Initialize file if it doesn't exist
    if not os.path.exists(LOGS_FILE):
        df_init = pd.DataFrame(columns=[
            "timestamp", "temperature", "humidity", "gas_raw", 
            "pm25", "pm10", "aqi", "category", "alert_triggered", 
            "alert_message", "mode"
        ])
        df_init.to_csv(LOGS_FILE, index=False)
        
    # Set up simulator
    simulator = AirQualitySimulator()
    simulator.set_mode(args.mode)
    
    print(f"[SIMULATOR] Starting {args.steps} polls in '{args.mode.upper()}' mode (interval: {args.interval}s)...")
    print("-" * 75)
    print(f"{'Timestamp':<19} | {'Temp':<5} | {'Hum':<5} | {'Gas':<5} | {'PM2.5':<6} | {'AQI':<4} | {'Status'}")
    print("-" * 75)
    
    now = datetime.now()
    readings = []
    
    for i in range(args.steps):
        # Calculate simulation time offset to create realistic chronological history if running multiple steps
        sim_time = now - timedelta(seconds=(args.steps - i) * 60) # 1-minute steps in simulator history
        reading = simulator.get_reading(timestamp=sim_time)
        readings.append(reading)
        
        # Live console output
        print(f"{reading['timestamp']} | {reading['temperature']:>5.1f} | {reading['humidity']:>5.1f} | {reading['gas_raw']:>5} | {reading['pm25']:>6.1f} | {reading['aqi']:>4} | {reading['category']}")
        
        if reading['alert_triggered']:
            print(f"  🚨 [ALERT] {reading['alert_message']}")
            
        time.sleep(args.interval)
        
    # Save to CSV log
    df_new = pd.DataFrame(readings)
    df_new.to_csv(LOGS_FILE, mode='a', header=False, index=False)
    print("-" * 75)
    print(f"[SIMULATOR] Simulation completed. {args.steps} records appended to {LOGS_FILE}.")
    
    # Run analysis if flag set
    if args.analyze:
        print("\n[ANALYZER] Running analytics engine...")
        analyzer = AirQualityAnalyzer(LOGS_FILE)
        analyzer.generate_report()
        analyzer.generate_chart()

if __name__ == "__main__":
    main()
