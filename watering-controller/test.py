import paho.mqtt.client as mqtt
import json

try:
    conn = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "manager")
except:
    conn = mqtt.Client("manager")

payload = {
    "schedule":[
        {
            "section": "front_section",
            "start_at": "17:17",
            "end_at": "17:18",
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
    "value": False
}

payload4 = {
    "setting": "schedule",
    "value": [
        {
            "section": "front_section",
            "start_at": "18:20",
            "end_at": "18:21",
            "every": "*"
        }
    ]
}

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
        "enabled": False
    }
}

conn.connect("10.0.3.21", 1883, 60)
conn.subscribe("manager/replies")
conn.publish("home/garden/watering/manage", json.dumps(payload_section))
conn.on_message = lambda client, userdata, msg: print(msg.payload.decode())
conn.loop_start()