# 🌱 **Bara Kopi Monitoring**

> **Bara Kopi Monitoring** adalah proyek **IoT berbasis ESP32, MQTT, dan Streamlit** yang berfungsi untuk memantau kondisi lingkungan tanaman kopi secara **real-time**.  
> Sistem ini membaca **suhu udara**, **kelembapan udara**, dan **kelembapan tanah**, lalu menampilkan datanya melalui **dashboard web interaktif**.

---

## 🧩 **Fitur Utama**

✅ Monitoring **suhu udara**, **kelembapan udara**, dan **kelembapan tanah** secara langsung  
✅ Tampilan **dashboard real-time** berbasis Streamlit  
✅ Pengiriman data melalui **protokol MQTT**  
✅ Tampilan **grafik interaktif** dan indikator status tanaman  
✅ Dokumentasi wiring dan struktur proyek yang jelas  

---

## 📁 **Struktur Proyek**

| File | Deskripsi |
|------|------------|
| `esp32_bara_kopi.ino` | Program utama untuk **ESP32**. Membaca data dari sensor DHT11 dan Soil Hygrometer, lalu mengirimkannya ke broker MQTT dalam format JSON. |
| `app.py` | Aplikasi **Streamlit** untuk menampilkan dashboard IoT secara real-time dengan grafik dan indikator status. |
| `README.md` | Dokumentasi utama proyek (file ini). |

---

## ⚙️ **Komponen yang Digunakan**

| Komponen | Fungsi |
|-----------|--------|
| 🧠 **ESP32** | Mikrokontroler utama yang menghubungkan sensor ke jaringan WiFi dan broker MQTT. |
| 🌡️ **DHT11** | Sensor untuk membaca **suhu** dan **kelembapan udara**. |
| 🌱 **Soil Hygrometer / Humidity Tester** | Sensor analog untuk mengukur **kelembapan tanah**. |

---

## 🔌 **Tabel Wiring ESP32 + DHT11 + Soil Hygrometer**

| Sensor | Pin Sensor | Pin ESP32 | Keterangan |
|---------|-------------|-----------|-------------|
| **DHT11 (Suhu & Kelembapan Udara)** | VCC | **3.3V** *(atau 5V, keduanya aman)* | Daya untuk sensor DHT11 |
|  | GND | **GND** | Ground bersama dengan semua sensor |
|  | DATA | **GPIO 4** | Jalur data sesuai `#define DHTPIN 4` |
|  | NC | - | Abaikan jika modul memiliki pin NC |
| **Soil Hygrometer (Analog Out)** | VCC | **5V** *(disarankan untuk pembacaan stabil)* | Daya sensor kelembapan tanah |
|  | GND | **GND** | Ground bersama |
|  | A0 (Analog Out) | **GPIO 34** | Jalur sinyal analog sesuai `#define SOIL_PIN 34` |
|  | DO (Digital Out) | - | Tidak digunakan (mode analog) |
