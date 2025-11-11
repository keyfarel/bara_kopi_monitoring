import streamlit as st
import numpy as np
import time
import plotly.graph_objects as go
import paho.mqtt.client as mqtt
import threading
import json
import math

# ==============================
# Konfigurasi halaman
# ==============================
st.set_page_config(page_title="Dashboard IoT Sensor", layout="wide")

# ==============================
# CSS UI (punya kamu, tidak diubah)
# ==============================
st.markdown("""
    <link rel="stylesheet"
    href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css">

    <style>
        body {
            background-color: #0b132b;
            color: #e0e0e0;
        }
        .main {
            background-color: #1c2541;
            color: #e0e0e0;
        }
        h1 {
            color: #5bc0be;
            font-weight: 700;
            margin-top: 0;
        }
        .data-card {
            background-color: #3a506b;
            border-radius: 12px;
            padding: 18px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            color: #ffffff;
            margin-bottom: 15px;
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        }
        .data-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        }
        .data-card h4 {
            color: #f4f4f9;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .status {
            text-align: right;
            font-weight: 600;
            color: #6fffe9;
        }
        hr {
            border: 1px solid #5bc0be;
            margin: 25px 0;
        }
        .chart-box {
            background-color: #3a506b;
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            margin-bottom: 20px;
        }
        [data-testid="stMetricValue"] {
            color: #ffffff !important;
            font-weight: 600;
        }
        @media (max-width: 768px) {
            .block-container {
                padding: 4.5rem 0.8rem 0.8rem 0.8rem !important;
            }
            h1 {
                font-size: 1.5rem !important;
                text-align: center;
                margin-top: 0 !important;
            }
            p { text-align: center; }
            .status { text-align: center; margin-top: 10px; }
            .data-card { padding: 12px !important; }
        }
    </style>
""", unsafe_allow_html=True)

# ==============================
# Header
# ==============================
st.markdown("""
    <h1 style="display:flex; align-items:center; gap:8px;">
        <i class="bi bi-broadcast-pin"></i> Dashboard IoT Sensor
    </h1>
    <p style="margin-top:-10px;">Monitoring Real-time</p>
""", unsafe_allow_html=True)
st.markdown('<div class="status"><i class="bi bi-circle-fill" style="color:#6fffe9;"></i> Terhubung</div>', unsafe_allow_html=True)

# ==============================
# MQTT setup
# ==============================
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "esp32/sensor"

latest_data = {"suhu": 0, "kelembapan": 0, "tanah": 0}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[SYSTEM] Terhubung ke broker MQTT!")
        client.subscribe(TOPIC)
    else:
        print(f"[ERROR] Gagal konek, kode: {rc}")

def on_message(client, userdata, msg):
    global latest_data
    try:
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)
        latest_data = {
            "suhu": data.get("suhu", 0),
            "kelembapan": data.get("kelembapan", 0),
            "tanah": data.get("tanah", 0)
        }
    except Exception as e:
        print("[ERROR] Gagal parsing:", e)

def mqtt_thread():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_forever()

threading.Thread(target=mqtt_thread, daemon=True).start()

# ==============================
# Helper aman
# ==============================
import math

def safe_float(x, fallback=0.0):
    try:
        if x is None: return fallback
        fx = float(x)
        if math.isnan(fx) or math.isinf(fx):
            return fallback
        return fx
    except: return fallback

def to_progress_percent(val, minv=0, maxv=100):
    v = safe_float(val)
    pct = (v - minv) / (maxv - minv) * 100
    return int(max(0, min(100, pct)))

# ==============================
# Placeholder & data grafik
# ==============================
placeholder = st.empty()
temp_data, humid_air_data, humid_soil_data, time_labels = [], [], [], []
MAX_POINTS = 10

# ==============================
# Loop real-time dashboard
# ==============================
while True:
    suhu = safe_float(latest_data.get("suhu"))
    kelembapan_udara = safe_float(latest_data.get("kelembapan"))
    kelembapan_tanah = safe_float(latest_data.get("tanah"))
    current_time = time.strftime("%H:%M:%S")

    temp_data.append(suhu)
    humid_air_data.append(kelembapan_udara)
    humid_soil_data.append(kelembapan_tanah)
    time_labels.append(current_time)

    if len(temp_data) > MAX_POINTS:
        temp_data = temp_data[-MAX_POINTS:]
        humid_air_data = humid_air_data[-MAX_POINTS:]
        humid_soil_data = humid_soil_data[-MAX_POINTS:]
        time_labels = time_labels[-MAX_POINTS:]

    with placeholder.container():
        col1, col2, col3 = st.columns(3)

        # === SUHU ===
        with col1:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            st.markdown('<h4><i class="bi bi-thermometer-half"></i> Suhu</h4>', unsafe_allow_html=True)
            st.metric(label="Suhu", value=f"{suhu:.1f} °C")
            st.progress(to_progress_percent(suhu, 15, 40))
            if suhu < 25:
                st.success("Normal")
            elif suhu < 35:
                st.warning("Hangat")
            else:
                st.error("Panas")
            st.markdown('</div>', unsafe_allow_html=True)

        # === KELEMBAPAN UDARA ===
        with col2:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            st.markdown('<h4><i class="bi bi-droplet"></i> Kelembapan Udara</h4>', unsafe_allow_html=True)
            st.metric(label="Kelembapan Udara", value=f"{kelembapan_udara:.1f} %")
            st.progress(to_progress_percent(kelembapan_udara, 0, 100))
            if kelembapan_udara > 70:
                st.info("Lembab")
            elif kelembapan_udara > 40:
                st.success("Normal")
            else:
                st.warning("Kering")
            st.markdown('</div>', unsafe_allow_html=True)

        # === KELEMBAPAN TANAH ===
        with col3:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            st.markdown('<h4><i class="bi bi-moisture"></i> Kelembapan Tanah</h4>', unsafe_allow_html=True)
            st.metric(label="Kelembapan Tanah", value=f"{kelembapan_tanah:.1f} %")
            st.progress(to_progress_percent(kelembapan_tanah, 0, 100))
            if kelembapan_tanah < 30:
                st.error("Kering")
            elif kelembapan_tanah < 60:
                st.success("Normal")
            else:
                st.info("Lembab")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # === GRAFIK ===
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(x=time_labels, y=temp_data, mode='lines+markers',
                                      name='Suhu (°C)', line=dict(color='#ff6b6b')))
            fig1.add_trace(go.Scatter(x=time_labels, y=humid_air_data, mode='lines+markers',
                                      name='Kelembapan Udara (%)', line=dict(color='#5bc0be')))
            fig1.update_layout(
                title="Grafik Suhu & Kelembapan Udara",
                xaxis_title="Waktu", yaxis_title="Nilai",
                template="plotly_dark", height=350,
                margin=dict(l=30, r=30, t=50, b=30),
                legend=dict(orientation="h", yanchor="top", y=-0.3, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig1, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_g2:
            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=time_labels, y=humid_soil_data, mode='lines+markers',
                                      name='Kelembapan Tanah (%)', line=dict(color='#9ef01a')))
            fig2.update_layout(
                title="Grafik Kelembapan Tanah",
                xaxis_title="Waktu", yaxis_title="Nilai (%)",
                template="plotly_dark", height=350,
                margin=dict(l=30, r=30, t=50, b=30),
                legend=dict(orientation="h", yanchor="top", y=-0.3, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    time.sleep(2)
