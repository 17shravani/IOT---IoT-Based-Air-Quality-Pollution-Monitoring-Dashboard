import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

class AirQualityAnalyzer:
    """
    Reads logged sensor CSV data, performs statistical calculations,
    compiles detailed textual reports, and renders high-quality trend charts.
    """
    def __init__(self, csv_path: str = "data/sensor_logs.csv"):
        self.csv_path = csv_path

    def load_data(self) -> pd.DataFrame:
        """Loads data from the CSV file and converts timestamps to datetime objects."""
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Data log file not found at: {self.csv_path}. Please run simulation first.")
        
        df = pd.read_csv(self.csv_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df

    def generate_report(self, report_path: str = "reports/air_quality_report.txt"):
        """Compiles a detailed textual analysis of the logged data."""
        df = self.load_data()
        if df.empty:
            return "No data logged to analyze."
            
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        total_records = len(df)
        start_time = df['timestamp'].min()
        end_time = df['timestamp'].max()
        duration = end_time - start_time
        
        # Calculate stats
        stats = {
            "Temperature": (df['temperature'].mean(), df['temperature'].min(), df['temperature'].max(), "*C"),
            "Humidity": (df['humidity'].mean(), df['humidity'].min(), df['humidity'].max(), "%"),
            "MQ135 Gas Raw": (df['gas_raw'].mean(), df['gas_raw'].min(), df['gas_raw'].max(), "analog value"),
            "PM2.5": (df['pm25'].mean(), df['pm25'].min(), df['pm25'].max(), "ug/m3"),
            "PM10": (df['pm10'].mean(), df['pm10'].min(), df['pm10'].max(), "ug/m3"),
            "AQI": (df['aqi'].mean(), df['aqi'].min(), df['aqi'].max(), "index points")
        }
        
        # Category distribution
        cat_counts = df['category'].value_counts()
        cat_percentages = (cat_counts / total_records) * 100
        
        # Triggered alert counts
        alert_count = df['alert_triggered'].sum()
        
        # Build textual report
        with open(report_path, "w") as f:
            f.write("========================================================================\n")
            f.write("                 AIR QUALITY & POLLUTION ANALYTICAL REPORT             \n")
            f.write("========================================================================\n")
            f.write(f"Generated at:       {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Monitoring Period:  {start_time} to {end_time}\n")
            f.write(f"Total Duration:     {duration}\n")
            f.write(f"Data Logs Processed: {total_records} readings\n")
            f.write(f"Alerts Triggered:   {alert_count} thresholds breached\n")
            f.write("------------------------------------------------------------------------\n\n")
            
            f.write("1. METRIC STATISTICS\n")
            f.write("---------------------\n")
            f.write(f"{'Metric':<20} | {'Average':<12} | {'Minimum':<12} | {'Maximum':<12} | {'Unit'}\n")
            f.write("-" * 72 + "\n")
            for metric, val in stats.items():
                f.write(f"{metric:<20} | {val[0]:<12.2f} | {val[1]:<12.2f} | {val[2]:<12.2f} | {val[3]}\n")
            f.write("\n")
            
            f.write("2. AQI CATEGORY DISTRIBUTION\n")
            f.write("-----------------------------\n")
            f.write(f"{'Category':<32} | {'Count':<8} | {'Percentage'}\n")
            f.write("-" * 55 + "\n")
            for cat in ["Good", "Moderate", "Unhealthy for Sensitive Groups", "Unhealthy", "Very Unhealthy", "Hazardous"]:
                count = cat_counts.get(cat, 0)
                pct = cat_percentages.get(cat, 0.0)
                f.write(f"{cat:<32} | {count:<8} | {pct:.1f}%\n")
            f.write("\n")
            
            f.write("3. SYSTEM REMARKS & ACTIONS REQUIRED\n")
            f.write("------------------------------------\n")
            if alert_count > 0:
                f.write(f"[ALERT] The system registered {alert_count} instances of excessive pollution.\n")
                f.write("Recommendation: Review the timeline for correlation with peak industrial activity\n")
                f.write("or traffic peaks. Deploy localized air purification systems or activate HVAC ventilation filters.\n")
            else:
                f.write("[NORMAL] Air quality remained within satisfactory bounds during the reporting period.\n")
                f.write("No corrective actions required.\n")
            f.write("========================================================================\n")
            
        print(f"[ANALYZER] Analytical report successfully compiled: {report_path}")

    def generate_chart(self, chart_path: str = "outputs/aq_trends.png"):
        """Generates a high-quality visualization of the pollution trends."""
        df = self.load_data()
        if df.empty:
            return
            
        os.makedirs(os.path.dirname(chart_path), exist_ok=True)
        
        plt.style.use('dark_background')
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        # Primary axis (AQI and Particulates)
        color_aqi = '#00e400'  # standard green for good, will plot line as cyber-cyan
        line_aqi, = ax1.plot(df['timestamp'], df['aqi'], color='#00f0ff', linewidth=2.5, label='AQI (PM2.5)')
        line_pm25, = ax1.plot(df['timestamp'], df['pm25'], color='#ff9900', linewidth=1.5, linestyle='--', label='PM2.5 (ug/m3)')
        
        ax1.set_xlabel('Timestamp / Reading Log Time', color='#cccccc', labelpad=10)
        ax1.set_ylabel('Air Quality Index (AQI) / PM2.5 (ug/m3)', color='#cccccc')
        ax1.tick_params(axis='y', labelcolor='#cccccc')
        ax1.grid(True, linestyle=':', alpha=0.3)
        
        # Add AQI category reference bands
        ax1.axhspan(0, 50, color='#00e400', alpha=0.08, label='Good (0-50)')
        ax1.axhspan(50, 100, color='#ffff00', alpha=0.08, label='Moderate (50-100)')
        ax1.axhspan(100, 150, color='#ff7e00', alpha=0.08, label='Unhealthy for Sensitive (100-150)')
        ax1.axhspan(150, 200, color='#ff0000', alpha=0.08, label='Unhealthy (150-200)')
        ax1.axhspan(200, 300, color='#8f3f97', alpha=0.08, label='Very Unhealthy (200-300)')
        ax1.axhspan(300, 500, color='#7e0023', alpha=0.08, label='Hazardous (>300)')
        
        # Secondary axis (Temp & Humidity)
        ax2 = ax1.twinx()
        line_temp, = ax2.plot(df['timestamp'], df['temperature'], color='#ff007f', linewidth=1.2, label='Temp (*C)')
        line_hum, = ax2.plot(df['timestamp'], df['humidity'], color='#00ff7f', linewidth=1.2, label='Hum (%)')
        
        ax2.set_ylabel('Temperature (*C) / Humidity (%)', color='#cccccc')
        ax2.tick_params(axis='y', labelcolor='#cccccc')
        
        # Align legends
        lines = [line_aqi, line_pm25, line_temp, line_hum]
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper left', framealpha=0.6, facecolor='#111111')
        
        # Title and styling
        plt.title('Air Quality and Environmental Parameters Trend Analysis', pad=15, fontsize=14, color='#ffffff', fontweight='bold')
        fig.autofmt_xdate()
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        
        plt.tight_layout()
        plt.savefig(chart_path, dpi=300)
        plt.close()
        
        print(f"[ANALYZER] Trend visualization chart saved: {chart_path}")
