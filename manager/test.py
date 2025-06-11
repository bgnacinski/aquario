import paho.mqtt.client as mqtt
import time
import json

try:
    conn = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "manager")
except:
    conn = mqtt.Client("manager")

conn.username_pw_set("tester", "tester")

payload_schedule = {
    "operation": "set",
    "reply_to": "manager/replies",
    "setting": "schedule",
    "value": [
        {
            "section": "front_section",
            "start_at": "14:00",
            "end_at": "14:02",
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
        "enabled": False
    }
}

payload_get = {
    "operation": "get",
    "reply_to": "manager/replies",
    "setting": "lock_until"
}

payload_lock_days = {
    "operation": "set",
    "reply_to": "manager/replies",
    "setting": "lock_until",
    "value": {
        "type": "days",
        "value": 10
    }
}

payload_lock_date = {
    "operation": "set",
    "reply_to": "manager/replies",
    "setting": "lock_until",
    "value": {
        "type": "date",
        "value": "2025-07-01"
    }
}

payload_lock_none = {
    "operation": "set",
    "reply_to": "manager/replies",
    "setting": "lock_until",
    "value": {
        "type": "none"
    }
}

payload_thin = {
    "pin": 17,
    "enable": False
}

conn.connect("10.0.3.21", 1883, 60)
conn.subscribe("watering/status")
conn.publish("watering/controller1", json.dumps(payload_thin))
conn.on_message = lambda client, userdata, msg: print(msg.topic + " | " + msg.payload.decode())
conn.loop_start()

time.sleep(1)