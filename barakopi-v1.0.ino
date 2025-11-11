#include <WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"

// ===========================
// Konfigurasi WiFi & MQTT
// ===========================
const char* ssid = "P SENGGEL";
const char* password = "inpotobrut";
const char* mqtt_server = "broker.hivemq.com";  // Bisa ganti ke broker kamu
const int mqtt_port = 1883;
const char* mqtt_topic = "esp32/sensor";

// ===========================
// Konfigurasi pin dan tipe sensor
// ===========================
#define DHTPIN 4
#define DHTTYPE DHT11
#define SOIL_PIN 34

DHT dht(DHTPIN, DHTTYPE);
WiFiClient espClient;
PubSubClient client(espClient);

// ===========================
// Fungsi bantu
// ===========================
void connectWiFi() {
  Serial.print("[SYSTEM] Menghubungkan ke WiFi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n[SYSTEM] WiFi terhubung!");
  Serial.print("[SYSTEM] IP Address: ");
  Serial.println(WiFi.localIP());
}

void reconnectMQTT() {
  while (!client.connected()) {
    Serial.print("[SYSTEM] Menghubungkan ke MQTT...");
    String clientId = "ESP32Client-" + String(random(0xffff), HEX);

    if (client.connect(clientId.c_str())) {
      Serial.println("BERHASIL!");
    } else {
      Serial.print("GAGAL (rc=");
      Serial.print(client.state());
      Serial.println("), coba lagi dalam 5 detik...");
      delay(5000);
    }
  }
}

// Fungsi untuk waktu simulasi
String getCurrentTime() {
  unsigned long totalSeconds = millis() / 1000;
  int hours = (totalSeconds / 3600) % 24;
  int minutes = (totalSeconds / 60) % 60;
  int seconds = totalSeconds % 60;

  char buffer[10];
  sprintf(buffer, "%02d:%02d:%02d", hours, minutes, seconds);
  return String(buffer);
}

// ===========================
// Setup
// ===========================
void setup() {
  Serial.begin(115200);
  dht.begin();
  delay(1000);
  Serial.println("=== Sensor DHT11 + Soil Hygrometer + MQTT ===");

  connectWiFi();
  client.setServer(mqtt_server, mqtt_port);
}

// ===========================
// Loop utama
// ===========================
void loop() {
  if (!client.connected()) {
    reconnectMQTT();
  }
  client.loop();

  String waktu = getCurrentTime();

  // ===== Baca sensor =====
  float kelembapan = dht.readHumidity();
  float suhu = dht.readTemperature();
  int soilRaw = analogRead(SOIL_PIN);
  int soilPercent = map(soilRaw, 4095, 0, 0, 100);
  soilPercent = constrain(soilPercent, 0, 100);

  // ===== Log ke Serial (format tetap seperti aslinya) =====
  Serial.print("[");
  Serial.print(waktu);
  Serial.print("] : [INFO] Suhu Udara       : ");
  Serial.print(suhu, 1);
  Serial.println(" °C");

  Serial.print("[");
  Serial.print(waktu);
  Serial.print("] : [INFO] Kelembapan Udara : ");
  Serial.print(kelembapan, 1);
  Serial.println(" %");

  Serial.print("[");
  Serial.print(waktu);
  Serial.print("] : [INFO] Kelembapan Tanah  : ");
  Serial.print(soilPercent);
  Serial.println(" %");

  // ===== Kirim ke MQTT dalam JSON =====
  String payload = "{";
  payload += "\"waktu\":\"" + waktu + "\",";
  payload += "\"suhu\":" + String(suhu, 1) + ",";
  payload += "\"kelembapan\":" + String(kelembapan, 1) + ",";
  payload += "\"tanah\":" + String(soilPercent);
  payload += "}";

  client.publish(mqtt_topic, payload.c_str());

  Serial.print("[");
  Serial.print(waktu);
  Serial.println("] : [MQTT] Data terkirim ke broker.");

  delay(2000); // jeda 2 detik antar pembacaan
}
