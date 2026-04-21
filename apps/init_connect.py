import paho.mqtt.client as mqtt
import json
import subprocess
import os
import re
import time
from dotenv import load_dotenv

load_dotenv()

def get_known_wifi_networks():
    """Returns a sorted list of dictionaries with Wi-Fi SSIDs and their priorities."""
    try:
        # Added AUTOCONNECT-PRIORITY to the requested fields
        result = subprocess.run(
            ['nmcli', '-t', '-f', 'NAME,TYPE,AUTOCONNECT-PRIORITY', 'connection', 'show'],
            capture_output=True, text=True, check=True
        )
        
        networks = []
        for line in result.stdout.strip().splitlines():
            # nmcli separates fields with colons. 
            parts = line.split(':')
            
            if len(parts) >= 3:
                priority_str = parts[-1]
                net_type = parts[-2]
                
                # Rejoin the name just in case the SSID itself contained a colon
                name = ":".join(parts[:-2]).replace('\\:', ':')

                if net_type == '802-11-wireless':
                    # Convert priority to an integer (default to 0 if it's missing/empty)
                    priority = int(priority_str) if priority_str.lstrip('-').isdigit() else 0
                    
                    networks.append({
                        'ssid': name,
                        'priority': priority
                    })
                    
        # Sort the list so the highest priority networks show up first
        networks.sort(key=lambda x: x['priority'], reverse=True)
        return networks
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to fetch networks: {e}")
        return []

# To add wifi from provided hotspot information
def add_prioritized_wifi(ssid, password, priority=999):
    try:
        # Create the base connection profile
        subprocess.run([
            'nmcli', 'connection', 'add',
            'type', 'wifi',
            'con-name', ssid,      # Name of the saved profile
            'ifname', 'wlan0',     # The wireless interface
            'ssid', ssid           # The actual Wi-Fi name
        ], check=True, capture_output=True)

        # Add WPA2 Personal security and the password
        subprocess.run([
            'nmcli', 'connection', 'modify', ssid,
            'wifi-sec.key-mgmt', 'wpa-psk',
            'wifi-sec.psk', password
        ], check=True, capture_output=True)

        # Set the autoconnect priority (higher number = higher priority)
        subprocess.run([
            'nmcli', 'connection', 'modify', ssid,
            'connection.autoconnect-priority', str(priority)
        ], check=True, capture_output=True)

        print(f"[SUCCESS] Added '{ssid}' with priority {priority}.")

    except subprocess.CalledProcessError as e:
        # e.stderr contains the exact error NetworkManager threw
        print(f"[RAS ERROR] Could not add network: {e.stderr.decode('utf-8').strip()}")

# Get mac addr from vehicle
def get_vehicle_mac():
    print("[RAS] Scanning for vehicle Bluetooth signatures...")
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
            print(f"[RAS] Found Target Vehicle: {mac}")
            return mac.replace(":", "").lower()
    except subprocess.CalledProcessError:
        # timeout 10s will return a non-zero exit code, which is expected
        pass
    except Exception as e:
        print(f"[RAS ERROR] Scan failed: {e}")
        
    return "unknown_device"

BT_MAC = get_vehicle_mac()
TOPIC = f"info/{BT_MAC}"
print(TOPIC)
received_payload = None

# --- 2. MQTT Callbacks ---
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f"[RAS] Connected. Waiting for config on {TOPIC}...")
        client.subscribe(TOPIC)
    else:
        print(f"[RAS ERROR] Connection failed: {reason_code}")

def on_message(client, userdata, msg):
    global received_payload
    try:
        received_payload = json.loads(msg.payload.decode())
        received_payload["VehicleId"] = BT_MAC
        print(f"[SUCCESS] Received data for: {received_payload.get('vehicleMake')}")
        client.disconnect() # Break the loop_forever()
    except Exception as e:
        print(f"[RAS ERROR] Invalid JSON: {e}")

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
    
    # find highest priority network and add passed hotspot as the highest priority connection
    networks = get_known_wifi_networks()
    highestPriority = networks[0]["priority"] + 5
    add_prioritized_wifi(json_arg["ssid"], json_arg["pass"], highestPriority)

    subprocess.run(["python3", "telemetry.py", json_arg])
else:
    print("[RAS] No vehicle configuration received. Exiting.")