import os
import sys
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time

# Ensure parent directory is in path to import simulation packages
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from python_simulation.simulator import AirQualitySimulator
from python_simulation.analyzer import AirQualityAnalyzer

# =====================================
# PAGE CONFIGURATION
# =====================================
st.set_page_config(
    page_title="AETHER Network: Sovereign Multi-Agent Command Center",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================
# CUSTOM STYLING (Premium Dark/Glassmorphic Hybrid)
# =====================================
st.markdown("""
<style>
    .stApp {
        background-color: #030712;
        color: #ffffff;
        background-image: radial-gradient(circle at 10% 20%, rgba(0, 240, 255, 0.03) 0%, transparent 40%),
                          radial-gradient(circle at 90% 80%, rgba(168, 85, 247, 0.03) 0%, transparent 40%);
    }
    
    /* Custom Card Design */
    .metric-card {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.06);
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
        margin-bottom: 15px;
        backdrop-filter: blur(12px);
    }
    
    .metric-card-title {
        font-size: 11px;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 8px;
    }

    .metric-card-value {
        font-size: 28px;
        font-weight: 800;
        color: #ffffff;
    }
    
    .metric-card-footer {
        font-size: 12px;
        color: #00f0ff;
        font-weight: 500;
        margin-top: 4px;
    }

    /* System Status Headers */
    .section-title {
        font-size: 16px;
        font-weight: 700;
        color: #00f0ff;
        margin-top: 25px;
        margin-bottom: 15px;
        border-left: 4px solid #a855f7;
        padding-left: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Node Status Row */
    .node-row {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 15px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.02);
        backdrop-filter: blur(12px);
    }
    
    .node-info {
        display: flex;
        flex-direction: column;
    }
    
    .node-name {
        font-size: 14px;
        font-weight: 700;
        color: #ffffff;
    }
    
    .node-meta {
        font-size: 11px;
        color: #94a3b8;
    }

    .node-stat-grid {
        display: flex;
        gap: 20px;
    }

    .node-stat {
        text-align: center;
    }

    .node-stat-val {
        font-size: 13px;
        font-weight: 700;
        color: #ffffff;
    }

    .node-stat-lbl {
        font-size: 9px;
        color: #94a3b8;
        text-transform: uppercase;
    }

    /* Agent status cards */
    .agent-card {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 12px 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        backdrop-filter: blur(8px);
    }
    .agent-name {
        font-size: 13px;
        font-weight: 700;
        color: #ffffff;
    }
    .agent-role {
        font-size: 10px;
        color: #94a3b8;
    }
    .agent-status {
        font-size: 11px;
        font-weight: 600;
        color: #00e400;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .agent-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #00e400;
        box-shadow: 0 0 6px #00e400;
    }
    .agent-dot.working {
        background-color: #00f0ff;
        box-shadow: 0 0 6px #00f0ff;
    }

    /* Custom alert box styling */
    .alert-item {
        background: rgba(17, 24, 39, 0.7);
        padding: 12px;
        margin-bottom: 8px;
        border-radius: 10px;
        border-left: 5px solid #2563eb;
        font-size: 13px;
        backdrop-filter: blur(12px);
    }
</style>
""", unsafe_allow_html=True)

# Initialize files
LOGS_FILE = "data/sensor_logs.csv"
os.makedirs("data", exist_ok=True)
os.makedirs("reports", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# Seed initial logs if database doesn't exist
if not os.path.exists(LOGS_FILE):
    df_init = pd.DataFrame(columns=[
        "timestamp", "temperature", "humidity", "gas_raw", 
        "pm25", "pm10", "aqi", "category", "alert_triggered", 
        "alert_message", "mode"
    ])
    df_init.to_csv(LOGS_FILE, index=False)
    
    # Pre-populate with default 24h data to avoid empty screen
    now = datetime.now()
    sim = AirQualitySimulator()
    readings = []
    for i in range(96):
        dt = now - timedelta(minutes=15 * (96 - i))
        readings.append(sim.get_reading(timestamp=dt))
    pd.DataFrame(readings).to_csv(LOGS_FILE, index=False)

# =====================================
# SIDEBAR CONTROLS
# =====================================
st.sidebar.title("⚙ Dashboard Controls")

# City Selection Filter
selected_city = st.sidebar.selectbox(
    "Select City",
    ["Delhi", "Mumbai", "Pune", "Bangalore", "Chennai", "Hyderabad"]
)

# Simulation Controls
intensity = st.sidebar.slider("Simulation Intensity", 1, 10, 5)
selected_scenario = st.sidebar.selectbox(
    "Atmospheric Scenario",
    ["normal", "gas_leak", "wildfire", "heavy_rain", "clean_air"]
)

st.sidebar.success("System Connected")
st.sidebar.markdown("---")

# Mock telemetry variables for the selected city
# We generate values seeded by city name to create distinct profiles
np.random.seed(sum(ord(c) for c in selected_city))
mock_battery = np.random.randint(85, 100)
mock_signal = np.random.randint(90, 100)
mock_temp = np.random.randint(22, 38)
mock_aqi = np.random.randint(25, 290)

# Render Sidebar Battery & Status Bars (matching the reference metrics)
st.sidebar.markdown("### 🔋 Sensor Health")
st.sidebar.metric("Battery Life", f"{mock_battery}%")
st.sidebar.metric("Signal Strength", f"{mock_signal}%")
st.sidebar.metric("Node Temperature", f"{mock_temp}°C")
st.sidebar.metric("Local AQI", mock_aqi)

# Reset data trigger
if st.sidebar.button("🗑️ Reset Telemetry Logs", type="secondary"):
    if os.path.exists(LOGS_FILE):
        os.remove(LOGS_FILE)
    st.rerun()

# =====================================
# HEADER HERO BANNER
# =====================================
st.markdown(f"""
<div style="
    padding: 30px;
    font-size: 32px;
    border-radius: 16px;
    background: linear-gradient(135deg, #00f0ff, #a855f7);
    color: white;
    box-shadow: 0px 8px 25px rgba(0, 0, 0, 0.4);
    margin-bottom: 25px;
">
    <h1 style="margin: 0; font-size: 28px; color: white; font-weight: 800; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
        🌍 AETHER Network: Sovereign Multi-Agent Command Center
    </h1>
    <p style="font-size: 14px; margin: 8px 0 0 0; opacity: 0.95;">
        📍 Station ID: <strong>STATION_{selected_city.upper()}_01</strong> &nbsp;&nbsp;|&nbsp;&nbsp; 
        🕒 Command Time: {datetime.now().strftime("%I:%M:%S %p")} &nbsp;&nbsp;|&nbsp;&nbsp; 
        🟢 Gateway Network: Online
    </p>
</div>
""", unsafe_allow_html=True)

# Read CSV telemetry log
df = pd.read_csv(LOGS_FILE)
if len(df) < 10:
    st.toast("Populating database...")
    time.sleep(0.5)

# Load the latest reading
latest_row = df.iloc[-1].to_dict()
current_aqi = int(latest_row['aqi'])
current_pm25 = float(latest_row['pm25'])
current_pm10 = float(latest_row['pm10'])
current_temp = float(latest_row['temperature'])
current_humidity = float(latest_row['humidity'])
current_gas = int(latest_row['gas_raw'])
current_category = latest_row['category']

# =====================================
# MULTI-AGENT CONTROL TOWER
# =====================================
st.markdown('<div class="section-title">🤖 Multi-Agent Executive Control Tower</div>', unsafe_allow_html=True)
col_a1, col_a2, col_a3, col_a4, col_a5, col_a6 = st.columns(6)

with col_a1:
    st.markdown(f"""
    <div class="agent-card">
        <div>
            <div class="agent-name">ORACLE</div>
            <div class="agent-role">Forecasting</div>
        </div>
        <div class="agent-status">
            <div class="agent-dot working"></div>
            <span style="color:#00f0ff;">Active</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_a2:
    st.markdown(f"""
    <div class="agent-card">
        <div>
            <div class="agent-name">NEXUS</div>
            <div class="agent-role">Routing</div>
        </div>
        <div class="agent-status">
            <div class="agent-dot"></div>
            <span>Online</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_a3:
    st.markdown(f"""
    <div class="agent-card">
        <div>
            <div class="agent-name">SOVEREIGN</div>
            <div class="agent-role">Confidence</div>
        </div>
        <div class="agent-status">
            <div class="agent-dot"></div>
            <span style="color:#ffff00;">Conf: 98%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_a4:
    st.markdown(f"""
    <div class="agent-card">
        <div>
            <div class="agent-name">PULSE</div>
            <div class="agent-role">Monitoring</div>
        </div>
        <div class="agent-status">
            <div class="agent-dot"></div>
            <span>Ready</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_a5:
    shield_color = "#ff7e00" if current_aqi > 100 else "#00e400"
    shield_label = "Mitigating" if current_aqi > 100 else "Guarding"
    st.markdown(f"""
    <div class="agent-card">
        <div>
            <div class="agent-name">SHIELD</div>
            <div class="agent-role">Protection</div>
        </div>
        <div class="agent-status">
            <div class="agent-dot" style="background-color: {shield_color}; box-shadow: 0 0 6px {shield_color};"></div>
            <span style="color: {shield_color};">{shield_label}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_a6:
    st.markdown(f"""
    <div class="agent-card">
        <div>
            <div class="agent-name">HELIX</div>
            <div class="agent-role">Self-Healing</div>
        </div>
        <div class="agent-status">
            <div class="agent-dot"></div>
            <span>Healthy</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================
# OVERVIEW METRICS SECTION
# =====================================
st.markdown('<div class="section-title">📊 Executive Dashboard Metrics</div>', unsafe_allow_html=True)
col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)

# Map category colors for cards
category_colors = {
    "Good": "linear-gradient(135deg, #16a34a, #22c55e)",
    "Moderate": "linear-gradient(135deg, #f59e0b, #eab308)",
    "Poor": "linear-gradient(135deg, #ea580c, #f97316)",
    "Hazardous": "linear-gradient(135deg, #be123c, #e11d48)"
}
card_bg = category_colors.get(current_category, "linear-gradient(135deg, #2563eb, #3b82f6)")

with col_m1:
    st.markdown(f"""
    <div class="metric-card" style="background: {card_bg};">
        <div class="metric-card-title" style="color: white; opacity: 0.8;">Overall AQI</div>
        <div class="metric-card-value" style="color: white;">{current_aqi}</div>
        <div class="metric-card-footer" style="color: white;">Category: {current_category}</div>
    </div>
    """, unsafe_allow_html=True)

with col_m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">Gas Raw (MQ135)</div>
        <div class="metric-card-value">{current_gas}</div>
        <div class="metric-card-footer">Analog Output</div>
    </div>
    """, unsafe_allow_html=True)

with col_m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">PM2.5 Dust</div>
        <div class="metric-card-value">{current_pm25}</div>
        <div class="metric-card-footer">µg / m³</div>
    </div>
    """, unsafe_allow_html=True)

with col_m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">PM10 Dust</div>
        <div class="metric-card-value">{current_pm10}</div>
        <div class="metric-card-footer">µg / m³</div>
    </div>
    """, unsafe_allow_html=True)

with col_m5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">Environment</div>
        <div class="metric-card-value">{current_temp}°C</div>
        <div class="metric-card-footer">Humidity: {current_humidity}%</div>
    </div>
    """, unsafe_allow_html=True)

# =====================================
# SENSOR HEALTH STATUS PANELS (GitHub Feature)
# =====================================
st.markdown('<div class="section-title">🩺 Sensor Health Status</div>', unsafe_allow_html=True)
col_h1, col_h2, col_h3, col_h4 = st.columns(4)
with col_h1:
    st.success("🌫 AQI Sensor\n\nOnline")
with col_h2:
    st.success("🌡 Temperature Sensor\n\nOnline")
with col_h3:
    st.success("💧 Humidity Sensor\n\nOnline")
with col_h4:
    st.success("📡 IoT Gateway\n\nConnected")

# =====================================
# LIVE ALERT CENTER (GitHub Feature)
# =====================================
st.markdown('<div class="section-title">🚨 Live Alert Center</div>', unsafe_allow_html=True)
alerts = []
if current_aqi > 100:
    alerts.append(("🔴 AQI exceeds recommended safe limit", "#ff007f"))
if current_pm25 > 50:
    alerts.append(("🟡 PM2.5 concentration is elevated", "#ff7e00"))
if current_temp > 32:
    alerts.append(("🟠 High environmental temperature detected", "#ff7e00"))
if current_humidity > 75:
    alerts.append(("🔵 Humidity level above normal", "#00f0ff"))

alerts.append(("🟢 All physical sensor units operational", "#00e400"))
alerts.append(("📡 IoT Gateway fully synchronized with public MQTT broker", "#00e400"))

for msg, color in alerts:
    st.markdown(f"""
    <div class="alert-item" style="border-left-color: {color};">
        {msg}
    </div>
    """, unsafe_allow_html=True)

# =====================================
# REGIONAL COMPARISON GRAPH
# =====================================
st.markdown('<div class="section-title">📊 Regional Air Quality Monitoring</div>', unsafe_allow_html=True)

# Generate values dynamically comparison chart
cities = ["Delhi", "Mumbai", "Pune", "Bangalore", "Chennai", "Hyderabad"]
city_aqi_values = []
for c in cities:
    np.random.seed(sum(ord(ch) for ch in c) + int(intensity))
    if c == "Delhi":
        val = np.random.randint(180, 310)
    elif c == "Bangalore":
        val = np.random.randint(35, 65)
    else:
        val = np.random.randint(60, 160)
    city_aqi_values.append(val)

# Set color array based on severity
bar_colors = []
for val in city_aqi_values:
    if val <= 50: bar_colors.append("#00e400")      # Green
    elif val <= 100: bar_colors.append("#ffff00")    # Yellow
    elif val <= 200: bar_colors.append("#ff7e00")    # Orange
    else: bar_colors.append("#ff007f")               # Red

fig_bar = go.Figure(data=[go.Bar(
    x=cities,
    y=city_aqi_values,
    marker_color=bar_colors,
    text=city_aqi_values,
    textposition='auto',
    hovertemplate="City: %{x}<br>AQI: %{y}<extra></extra>"
)])

fig_bar.update_layout(
    title="City-wise Air Quality Index (Live Comparison)",
    xaxis_title="City Name",
    yaxis_title="AQI Value",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#ffffff"),
    height=380,
    margin=dict(l=20, r=20, t=40, b=20),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)")
)

# Plot gauge and bar chart side-by-side
col_g1, col_g2 = st.columns([1, 2])

with col_g1:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=current_aqi,
        title={"text": f"Current AQI ({selected_city})", "font": {"size": 16, "color": "#ffffff"}},
        gauge={
            "axis": {"range": [0, 500], "tickcolor": "#ffffff"},
            "bar": {"color": "#00f0ff"},
            "steps": [
                {"range": [0, 50], "color": "#00e400"},
                {"range": [50, 100], "color": "#ffff00"},
                {"range": [100, 200], "color": "#ff7e00"},
                {"range": [200, 300], "color": "#ff007f"},
                {"range": [300, 500], "color": "#7f1d1d"}
            ]
        }
    ))
    fig_gauge.update_layout(height=380, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#ffffff"))
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_g2:
    st.plotly_chart(fig_bar, use_container_width=True)

# =====================================
# REAL-TIME TIMELINE GRAPHS
# =====================================
st.markdown('<div class="section-title">📈 Real-Time Environmental Timelines</div>', unsafe_allow_html=True)

# AQI Trend Chart & PM2.5 Trend Chart (GitHub Features)
df_trends = df.copy().tail(24)
df_trends['hour'] = list(range(len(df_trends)))

col_c1, col_c2 = st.columns(2)

with col_c1:
    fig_aqi_trend = px.line(
        df_trends,
        x='hour',
        y='aqi',
        markers=True,
        title="📈 24-Hour AQI Trend"
    )
    fig_aqi_trend.update_traces(line_color='#a855f7')
    fig_aqi_trend.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ffffff"),
        height=320,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)")
    )
    st.plotly_chart(fig_aqi_trend, use_container_width=True)

with col_c2:
    fig_pm25 = px.area(
        df_trends,
        x='hour',
        y='pm25',
        title="🌫 PM2.5 Concentration Trend"
    )
    fig_pm25.update_traces(line_color='#00f0ff', fillcolor='rgba(0, 240, 255, 0.12)')
    fig_pm25.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ffffff"),
        height=320,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)")
    )
    st.plotly_chart(fig_pm25, use_container_width=True)

# Temperature & Humidity Lines
st.markdown('<div class="section-title">🌡 Environmental Parameter Timelines</div>', unsafe_allow_html=True)
col_e1, col_e2 = st.columns(2)

with col_e1:
    fig_temp_trend = px.line(
        df_trends,
        x='hour',
        y='temperature',
        markers=True,
        title="🌡 Temperature Trend"
    )
    fig_temp_trend.update_traces(line_color='#ef4444')
    fig_temp_trend.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ffffff"),
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)")
    )
    st.plotly_chart(fig_temp_trend, use_container_width=True)

with col_e2:
    fig_hum_trend = px.bar(
        df_trends,
        x='hour',
        y='humidity',
        title="💧 Humidity Trend"
    )
    fig_hum_trend.update_traces(marker_color='#10b981')
    fig_hum_trend.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ffffff"),
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)")
    )
    st.plotly_chart(fig_hum_trend, use_container_width=True)

# =====================================
# DONUT + INSIGHTS SECTION (GitHub Feature)
# =====================================
st.markdown('<div class="section-title">📊 Pollution Composition & Insights</div>', unsafe_allow_html=True)
col_d1, col_d2 = st.columns(2)

with col_d1:
    pollution_df = pd.DataFrame({
        "Pollutant": ["PM2.5", "PM10", "CO", "NO₂", "SO₂"],
        "Value": [35, 25, 15, 15, 10]
    })
    
    fig_donut = px.pie(
        pollution_df,
        names="Pollutant",
        values="Value",
        hole=0.65,
        title="Pollution Source Distribution"
    )
    fig_donut.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )
    fig_donut.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ffffff"),
        height=320,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with col_d2:
    st.markdown("### 📊 Environmental Insights")
    
    # Calculate statistics from recent logs
    df_24 = df.copy().tail(24)
    best_row = df_24.loc[df_24["aqi"].idxmin()]
    worst_row = df_24.loc[df_24["aqi"].idxmax()]
    avg_aqi = round(df_24["aqi"].mean(), 1)
    trend = "Improving" if current_aqi < avg_aqi else "Needs Attention"
    
    st.info(f"""
    **🌟 Best AQI Hour (Recent):** Index {int(best_row.name % 24)}:00
    
    **AQI Value:** {int(best_row['aqi'])} ({best_row['category']})
    """)
    
    st.warning(f"""
    **⚠️ Worst AQI Hour (Recent):** Index {int(worst_row.name % 24)}:00
    
    **AQI Value:** {int(worst_row['aqi'])} ({worst_row['category']})
    """)
    
    st.success(f"""
    **📈 24-Hour Average AQI:** {avg_aqi}
    
    **🎯 Control Trend:** {trend}
    """)

# =====================================
# SMART SENSOR MONITORING CENTER (GitHub Feature)
# =====================================
st.markdown('<div class="section-title">🛰 Smart Sensor Monitoring Center</div>', unsafe_allow_html=True)
col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)
with col_s1:
    st.metric("🔋 Battery", f"{mock_battery}%")
with col_s2:
    st.metric("📡 Signal", f"{mock_signal}%")
with col_s3:
    st.metric("⏱ Uptime", "98.5%")
with col_s4:
    st.metric("🔄 Last Sync", "4s")
with col_s5:
    st.metric("🌐 Gateway", "Connected")

# =====================================
# GATEWAY NODES INFO CARDS
# =====================================
st.markdown('<div class="section-title">📡 Active Gateway Stations</div>', unsafe_allow_html=True)
col_n1, col_n2 = st.columns(2)

with col_n1:
    st.markdown(f"""
    <div class="node-row">
        <div class="node-info">
            <div class="node-name">Gateway Node 01 ({selected_city} North)</div>
            <div class="node-meta">Hardware: ESP32 + MQ135 + SDS011</div>
        </div>
        <div class="node-stat-grid">
            <div class="node-stat">
                <div class="node-stat-val">{mock_battery}%</div>
                <div class="node-stat-lbl">Battery</div>
            </div>
            <div class="node-stat">
                <div class="node-stat-val">{mock_signal}%</div>
                <div class="node-stat-lbl">Signal</div>
            </div>
            <div class="node-stat">
                <div class="node-stat-val">97%</div>
                <div class="node-stat-lbl">Uptime</div>
            </div>
            <div class="node-stat">
                <div class="node-stat-val">4s</div>
                <div class="node-stat-lbl">Sync</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_n2:
    st.markdown(f"""
    <div class="node-row">
        <div class="node-info">
            <div class="node-name">Auxiliary Node 02 ({selected_city} South)</div>
            <div class="node-meta">Hardware: ESP32 + DHT22 + SDS011</div>
        </div>
        <div class="node-stat-grid">
            <div class="node-stat">
                <div class="node-stat-val">{max(10, mock_battery - 8)}%</div>
                <div class="node-stat-lbl">Battery</div>
            </div>
            <div class="node-stat">
                <div class="node-stat-val">{max(10, mock_signal - 3)}%</div>
                <div class="node-stat-lbl">Signal</div>
            </div>
            <div class="node-stat">
                <div class="node-stat-val">99%</div>
                <div class="node-stat-lbl">Uptime</div>
            </div>
            <div class="node-stat">
                <div class="node-stat-val">6s</div>
                <div class="node-stat-lbl">Sync</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================
# HISTORICAL TELEMETRY LOGS
# =====================================
st.markdown('<div class="section-title">📋 Historical Air Quality Logs</div>', unsafe_allow_html=True)

df_logs = df.copy().tail(15).sort_values(by="timestamp", ascending=False)
def map_emoji(row):
    cat = str(row['category']).lower()
    if "good" in cat: return "🟢 Good"
    elif "moderate" in cat: return "🟡 Moderate"
    elif "poor" in cat or "unhealthy" in cat: return "🔴 Poor"
    else: return "⚫ Hazardous"

df_logs['Category Indicator'] = df_logs.apply(map_emoji, axis=1)

df_display = df_logs[["timestamp", "aqi", "pm25", "temperature", "humidity", "Category Indicator"]].rename(
    columns={
        "timestamp": "Timestamp",
        "aqi": "AQI",
        "pm25": "PM2.5",
        "temperature": "Temperature (°C)",
        "humidity": "Humidity (%)",
        "Category Indicator": "Status Category"
    }
)
st.dataframe(df_display, use_container_width=True, hide_index=True)

# Download CSV button (GitHub Feature)
csv_bytes = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Air Quality Log CSV",
    data=csv_bytes,
    file_name=f"{selected_city}_air_quality_logs.csv",
    mime="text/csv"
)

# Simulated Poll action
if st.button("📡 Poll Sensor Node"):
    simulator = AirQualitySimulator()
    simulator.set_mode(selected_scenario)
    
    # Generate new reading
    reading = simulator.get_reading()
    reading['temperature'] = float(mock_temp + np.random.normal(0, 0.5))
    reading['aqi'] = int(reading['aqi'] * (intensity / 5.0))
    reading['category'] = simulator.classify_aqi(reading['aqi'])
    
    # Append to CSV
    pd.DataFrame([reading]).to_csv(LOGS_FILE, mode='a', header=False, index=False)
    st.toast(f"Polled Node. AQI: {reading['aqi']} ({reading['category']})", icon="📡")
    time.sleep(0.5)
    st.rerun()

# =====================================
# FOOTER
# =====================================
st.markdown("---")
st.caption(
    "AETHER Network Core | Built using Streamlit, Plotly, Pandas, and NumPy | Zero-Trust Environmental Compliance"
)
