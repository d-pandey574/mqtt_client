import serial
import time
import json
import paho.mqtt.client as mqtt
from datetime import datetime, timezone

# UART Configuration
UART_PORT = 'COM5'
BAUD_RATE = 115200
TIMEOUT = 5

# MQTT Configuration
MQTT_BROKER = 'mqtt.eclipseprojects.io'
MQTT_PORT = 1883
MQTT_TOPIC = 'test/india/gj/ahm/sensor'

def parse_uart_payload(data_bytes):
    try:
        # Parse MAC address (bytes 0-5, reversed for little-endian)
        mac = "".join(f"{b:02X}" for b in reversed(data_bytes[0:6]))

        
        # Packet Count (bytes 8-9)-
        packet_count = int.from_bytes(data_bytes[8:10], byteorder='little')

        # Temperature (bytes 10-11), scaled by 10 for Celsius
        temperature_raw = int.from_bytes(data_bytes[10:12], 'little')
        temperature_c = round(temperature_raw / 10.0, 2)

        # Humidity (bytes 12-13), as percentage
        humidity_raw = int.from_bytes(data_bytes[12:14], 'little')
        humidity_percent = humidity_raw

        # Pressure (bytes 14-17), in Pascals
        pressure_raw = int.from_bytes(data_bytes[14:18], 'little')
        pressure_pa = pressure_raw

        # UTC Timestamp
        current_time_gmt = datetime.now(timezone.utc)
        timestamp = current_time_gmt.strftime('%Y-%m-%d %H:%M:%S %Z')

        return {
            "timestamp": timestamp,
            "device_mac": mac,
            "packet_no": packet_count,
            "temperature": temperature_c,
            "humidity": humidity_percent,
            "pressure": pressure_pa
        }

    except Exception as e:
        return {
            "error": str(e),
            "raw_data": data_bytes.hex()
        }

def uart_reader(client):
    try:
        ser = serial.Serial(UART_PORT, BAUD_RATE, timeout=TIMEOUT)
        print(f"[UART] Connected to {UART_PORT}")
    except Exception as e:
        print(f"[UART ERROR] {e}")
        return

    while True:
        try:
            if ser.in_waiting:
                raw = ser.read(18)
                print(f"[UART] Raw: {raw.hex().upper()}")
                parsed = parse_uart_payload(raw)
                json_payload = json.dumps(parsed)
                print(f"[MQTT] Published: {json_payload}")
                client.publish(MQTT_TOPIC, json_payload)
            time.sleep(0.1)
        except Exception as e:
            print(f"[UART READ ERROR] {e}")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[MQTT] Connected to broker")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"[MQTT] Connection failed with code {rc}")

def on_message(client, userdata, msg):
    print(f"[MQTT] Received: {msg.payload.decode()}")

def start_services():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    uart_reader(client)

if __name__ == '__main__':
    start_services()
