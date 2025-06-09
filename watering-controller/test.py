import paho.mqtt.client as mqtt
import json

try:
    conn = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "tester")
except:
    conn = mqtt.Client("tester")

payload = {
    "schedule":[
        {
            "section": "front_section",
            "start_at": "20:02",
            "end_at": "20:03",
            "every": "*"
        }
    ]
}

payload2 = {
    "section": "front_section",
    "enabled": False,
}

payload3 = {
    "setting": "global_lock",
    "value": True
}

conn.connect("10.0.3.21", 1883, 60)
conn.subscribe("home/garden/watering/#")
conn.publish("home/garden/watering/schedule", json.dumps(payload))