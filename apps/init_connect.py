import paho.mqtt.client as mqtt
import json
import subprocess
import os
import re
import time
from dotenv import load_dotenv

load_dotenv()

# --- 1. Get BT MAC via your specific Bash command ---
def get_vehicle_mac():
    print("[SYSTEM] Scanning for vehicle Bluetooth signatures...")
    # We run the scan for 10 seconds, then terminate it to read the output
    cmd = 'timeout 10s bluetoothctl scan on | grep -iE "car|honda|ford|toyota|chevrolet|sync|handsfree|audio|vw|audi"'
    
    try:
        # shell=True is needed here because of the pipe (|) and grep
        output = subprocess.check_output(cmd, shell=True).decode()
        
        # Use Regex to find the first MAC address (format XX:XX:XX:XX:XX:XX)
        match = re.search(r'([0-9A-F]{2}:){5}[0-9A-F]{2}', output, re.I)
        if match:
            mac = match.group(0)
            print(mac)
            print(f"[SYSTEM] Found Target Vehicle: {mac}")
            return mac.replace(":", "").lower()
    except subprocess.CalledProcessError:
        # timeout 10s will return a non-zero exit code, which is expected
        pass
    except Exception as e:
        print(f"[ERROR] Scan failed: {e}")
        
    return "unknown_device"

BT_MAC = get_vehicle_mac()
TOPIC = f"info/{BT_MAC}"
print(TOPIC)
received_payload = None

# --- 2. MQTT Callbacks ---
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f"[SYSTEM] Connected. Waiting for config on {TOPIC}...")
        client.subscribe(TOPIC)
    else:
        print(f"[ERROR] Connection failed: {reason_code}")

def on_message(client, userdata, msg):
    global received_payload
    try:
        received_payload = json.loads(msg.payload.decode())
        received_payload["VehicleId"] = BT_MAC
        print(f"[SUCCESS] Received data for: {received_payload.get('vehicleMake')}")
        client.disconnect() # Break the loop_forever()
    except Exception as e:
        print(f"[ERROR] Invalid JSON: {e}")

# --- 3. MQTT Execution ---
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(os.getenv('USERNAME'), os.getenv('PASSWORD'))
client.tls_set()
client.on_connect = on_connect
client.on_message = on_message

client.connect(os.getenv('BROKER_HOST'), int(os.getenv('BROKER_PORT')), 60)
client.loop_forever()

# --- 4. Launch Telemetry with Argument ---
if received_payload:
    # Pass the object as a JSON string to telemetry.py
    json_arg = json.dumps(received_payload)
    subprocess.run(["python3", "telemetry.py", json_arg])
else:
    print("[SYSTEM] No vehicle configuration received. Exiting.")