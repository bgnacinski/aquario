import paho.mqtt.client as mqtt
import time
import json

try:
    conn = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "manager")
except:
    conn = mqtt.Client("manager")

payload_schedule = {
    "operation": "set",
    "reply_to": "manager/replies",
    "setting": "schedule",
    "value": [
        {
            "section": "front_section",
            "start_at": "19:39",
            "end_at": "19:40",
            "every": "*"
        }
    ]
}
payload_section = {
    "operation": "set",
    "reply_to": "manager/replies",
    "setting": "section",
    "value": {
        "name": "front_section",
        "enabled": True
    }
}

payload_get = {
    "operation": "get",
    "reply_to": "manager/replies",
    "setting": "sections"
}

payload_lock = {
    "operation": "set",
    "reply_to": "manager/replies",
    "setting": "lock_until",
    "value": "2025-06-08"
}

conn.connect("10.0.3.21", 1883, 60)
conn.subscribe("manager/replies")
conn.subscribe("home/garden/watering/messages")
conn.publish("home/garden/watering/manage", json.dumps(payload_section))
conn.on_message = lambda client, userdata, msg: print(msg.topic + " | " + msg.payload.decode())
conn.loop_start()

time.sleep(2)