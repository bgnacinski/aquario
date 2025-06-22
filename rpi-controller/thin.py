import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import json

def annouce_state(relay_pin:int, watering:bool):
    global config

    payload = {
        "watering": watering,
        "relay_pin": relay_pin
    }

    print("Annoucing payload: ", payload)

    mqtt_client.publish(config["topic_prefix"] + "/status", json.dumps(payload))

def toggle_relay(relay_pin:int, enable:bool = True):
    GPIO.setup(relay_pin, GPIO.OUT)
    # due to reversed low_powered relays, logic is reversed
    if enable:
        GPIO.output(relay_pin, GPIO.LOW)

    else:
        GPIO.output(relay_pin, GPIO.HIGH)

    annouce_state(relay_pin, enable)
    print(f"Relay at {relay_pin} {'opened(off)' if enable else 'closed(on)'}.")

def on_connect(client, userdata, flags, rc, properties=None):
    global config

    print("Connected to Aquario MQTT broker with result code: " + str(rc))
    client.subscribe(config["topic_prefix"] + config["client_id"])

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload)

        toggle_relay(int(payload["relay_pin"]), payload["enable"])

    except (KeyError, ValueError) as e:
        print("Error: " + repr(e) + " | Invalid payload: " + str(msg.payload))

# load config
with open("config.json", "r") as f:
    config = json.load(f)

GPIO.setmode(GPIO.BCM)

mqtt_client = mqtt.Client(client_id=config["client_id"], callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.username_pw_set(config["auth"]["username"], config["auth"]["password"])

mqtt_client.connect(config["server_address"], config["port"], config["timeout"])
mqtt_client.loop_forever()