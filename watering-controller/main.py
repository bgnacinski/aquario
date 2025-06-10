from lib.gpiocontroller import GPIOController
from lib.settings import SettingsManager
from lib.config import ConfigManager
from lib.logger import Logger
import paho.mqtt.client as mqtt
import datetime
import schedule
import json
import time

logger = Logger("main")

config = ConfigManager("config.json")
settings_manager = SettingsManager()
SETTINGS = settings_manager.get()
gpio_controller = GPIOController()

mqtt_config = config.get("mqtt")
SECTIONS = config.get("sections")

# --------------------------------------
#TODO: stworzenie pliku testowego testującego całość zakresu działania
#TODO: sprawdzanie pogody w funkcji section_watering, gdy pada - nie podlewamy, chyba że ręcznie zostało to włączone.
# -------------------------------------
def send_message(topic:str, message: dict):
    global mqtt_client

    logger.debug(f"Sending message on '{topic}': {message}")
    mqtt_client.publish(topic, json.dumps(message))

def status_update(message: str, error: bool = False):
    topic = mqtt_config["topic_prefix"] + "messages"
    payload = {
        "message": message,
        "error": error
    }

    send_message(topic, payload)

def section_watering(section: str, enable: bool = True):
    global SETTINGS

    if section not in list(SECTIONS.keys()):
        logger.error(f"Section '{section}' not found.")
        status_update(f"Section '{section}' not found.", True)
        return

    if SETTINGS["lock_until"] and SETTINGS["lock_until"] != "none":
        date_now = datetime.date.today()
        date_until = datetime.datetime.strptime(SETTINGS["lock_until"], "%Y-%m-%d").date()

        if date_now <= date_until:
            logger.info(f"Global watering lock enabled until {date_until} - not proceeding.")
            # returning status as error for UI(?)
            status_update(f"Global watering lock enabled until {date_until} - not proceeding.", True)
            return

    valve_pin = SECTIONS[section]["valve_pin"]

    # reversed logic because of low-activated relays
    if enable:
        msg = f"Section '{section}' enabled."
        gpio_controller.set_low(valve_pin)

    else:
        msg = f"Section '{section}' disabled."
        gpio_controller.set_high(valve_pin)

    logger.info(msg)
    status_update(msg)

def set_schedule(tasks: list):
    for task in tasks:
        section = task["section"] # section to water
        start_at = task["start_at"] # start at hour
        end_at = task["end_at"] # duration in minutes

        # interval check
        try:
            task["every"] == int(task["every"])
        except ValueError:
            if task["every"] in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                if task["every"] == "monday":
                    schedule.every().monday.at(start_at).do(section_watering, section, True)
                    schedule.every().monday.at(end_at).do(section_watering, section, False)

                elif task["every"] == "tuesday":
                    schedule.every().tuesday.at(start_at).do(section_watering, section, True)
                    schedule.every().tuesday.at(end_at).do(section_watering, section, False)

                elif task["every"] == "wednesday":
                    schedule.every().wednesday.at(start_at).do(section_watering, section, True)
                    schedule.every().wednesday.at(end_at).do(section_watering, section, False)

                elif task["every"] == "thursday":
                    schedule.every().thursday.at(start_at).do(section_watering, section, True)
                    schedule.every().thursday.at(end_at).do(section_watering, section, False)

                elif task["every"] == "friday":
                    schedule.every().friday.at(start_at).do(section_watering, section, True)
                    schedule.every().friday.at(end_at).do(section_watering, section, False)

                elif task["every"] == "saturday":
                    schedule.every().saturday.at(start_at).do(section_watering, section, True)
                    schedule.every().saturday.at(end_at).do(section_watering, section, False)

                elif task["every"] == "sunday":
                    schedule.every().sunday.at(start_at).do(section_watering, section, True)
                    schedule.every().sunday.at(end_at).do(section_watering, section, False)

            else:
                if task["every"] == "*":
                    schedule.every().days.at(start_at).do(section_watering, section, True)
                    schedule.every().days.at(end_at).do(section_watering, section, False)

                else:
                    schedule.every(task["every"]).days.at(start_at).do(section_watering, section, True)
                    schedule.every(task["every"]).days.at(end_at).do(section_watering, section, False)

# mqtt
def on_connect(client, userdata, flags, rc, properties=None):
    logger.info("Connected to Aquario MQTT broker with result code: " + str(rc))
    client.subscribe(mqtt_config["topic_prefix"] + "#")

def on_message(client, userdata, msg):
    global SETTINGS

    topic = msg.topic
    try:
        payload = json.loads(msg.payload.decode())
    except json.JSONDecodeError:
        payload = msg.payload.decode()

    try:
        if topic == mqtt_config["topic_prefix"] + "manage":
            if not payload["operation"] or not payload["reply_to"]:
                raise KeyError("'operation' and 'reply_to' are required.")

            operation = payload["operation"]
            reply_to = payload["reply_to"]

            # settings or state manipulation
            if operation == "set":
                setting = payload["setting"]
                value = payload["value"]

                if setting not in ["*", "section", "schedule", "lock_until"]:
                    raise KeyError(f"Undefined setting '{setting}'")

                elif setting == "section" and type(value) != dict:
                    raise KeyError("'section' requires object with 'name' and 'enabled' properties as 'value' key.")

                # if manual section switch, perform only switching
                if setting == "section":
                    section_watering(value["name"], value["enabled"])
                    return

                elif setting == "lock_until":
                    lock_type = value["type"]

                    if lock_type == "date":
                        lock_until = value["value"]

                        try:
                            value = datetime.datetime.strptime(lock_until, "%Y-%m-%d").strftime("%Y-%m-%d")

                        except ValueError:
                            raise ValueError("Invalid date format. Expected format: YYYY-MM-DD")

                    elif lock_type == "days":
                        lock_until = value["value"]

                        lock_until = int(lock_until)

                        lock_until = datetime.date.today() + datetime.timedelta(days=lock_until)
                        value = lock_until.strftime("%Y-%m-%d")

                    elif lock_type == "none":
                        value = "none"

                    else:
                        raise ValueError("Invalid lock_until.type value. Allowed values: date, time, none")

                settings_manager.write(value, setting)
                SETTINGS = settings_manager.get()
                send_message(reply_to, {
                    "success": True,
                    "message": f"Updated setting '{setting}' to '{value}'."
                })

                # update schedule if needed
                if setting == "schedule":
                    set_schedule(value)

                logger.info(f"Updated setting '{setting}' to '{value}'.")

            # information request
            elif operation == "get":
                if payload["setting"] and payload["setting"] in ["*", "schedule", "lock_until"]:
                    response_value = settings_manager.get(payload["setting"])

                # getting sections defined in config, read-only property
                elif payload["setting"] == "sections":
                    response_value = SECTIONS

                else:
                    response_value = settings_manager.get()

                response = {
                    "setting": payload["setting"] or "*",
                    "value": response_value
                }

                send_message(reply_to, response)

            else:
                raise ValueError("'operation' may be only 'set' or 'get'")

    except (KeyError, ValueError) as e:
        logger.error(f"Error: {repr(e)} | Invalid payload {payload}.")
        status_update(f"Error: {repr(e)} | Invalid payload {payload}", True)
        return

# load schedule from file
schedule_json = settings_manager.read_schedule()

if schedule_json:
    set_schedule(schedule_json)
    logger.info("Loaded schedule from file.")

try:
    # unix
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "Aquario")
except:
    # windows
    mqtt_client = mqtt.Client("Aquario")

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

try:
    mqtt_client.connect(mqtt_config["server_address"], mqtt_config["port"], mqtt_config["timeout"])
    mqtt_client.loop_start()

except TimeoutError:
    logger.error("Cannot connect to the MQTT server")

try:
    while True:
        schedule.run_pending()
        time.sleep(1)

except KeyboardInterrupt:
    print("[!] Terminating...")

finally:
    del gpio_controller