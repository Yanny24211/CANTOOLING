import paho.mqtt.client as mqtt
import json
import time
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()

BROKER_HOST = os.getenv('BROKER_HOST')
BROKER_PORT = int(os.getenv('BROKER_PORT'))
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
VEHICLE_ID = os.getenv('VEHICLE_ID')
TOPIC = f"info/{MACADDR}"

print(BROKER_HOST)
print(BROKER_PORT)
print(USERNAME)
print(PASSWORD)


payload = {
    "device_id": "pi_vehicle_test_001",
    "risk_type": "unsafe_turn",
    "location": {"lat": 43.647994, "lon": -79.7291527},
    "severity": "low",
    # Modernized UTC timestamp to resolve the deprecation warning
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "additional_data": {
        "speed": 55,
        "road_condition": "wet"
    }
}


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set()


# 1. Define the message handler
def on_message(client, userdata, msg):
    try:
        # Decode the byte payload to string, then parse JSON
        data = json.loads(msg.payload.decode())
        print(f"\n[INCOMING] Received on {msg.topic}:")
        print(json.dumps(data, indent=4))
    except Exception as e:
        print(f"[RAS ERROR] Could not parse message: {e}")

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("[RAS] Connected to broker")
        
        # 2. Subscribe to the topic here
        # Subscribing inside on_connect ensures you resubscribe if the connection drops/reconnects
        client.subscribe(TOPIC)
        print(f"[RAS] Subscribed to {TOPIC}")
        
        # Publish your test payload
        client.publish(TOPIC, json.dumps(payload), qos=1)
        print(f"[RAS] Published test payload to {TOPIC}")
    else:
        print(f"[RAS ERROR] Connection failed with code {reason_code}")

# 3. Assign the callback
client.on_connect = on_connect
client.on_message = on_message

print("[RAS] Initiating transmission sequence...")
client.connect(BROKER_HOST, BROKER_PORT, 60)

client.loop_start()

# Keep it alive long enough to see your own message come back
time.sleep(1000000) 
client.loop_stop()
print("[RAS] Sequence complete. Socket closed.")