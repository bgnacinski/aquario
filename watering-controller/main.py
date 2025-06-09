from lib.gpiocontroller import GPIOController
from lib.schedule import ScheduleManager
from lib.settings import SettingsManager
from lib.config import ConfigManager
from lib.logger import Logger
import paho.mqtt.client as mqtt
import schedule
import json
import time

logger = Logger("main")

schedule_manager = ScheduleManager()
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
def status_update(message: str, error: bool = False):
    global mqtt_client

    topic = mqtt_config["topic_prefix"] + "message"
    payload = {
        "message": message,
        "error": error
    }

    mqtt_client.publish(topic, json.dumps(payload))

def section_watering(section: str, enable: bool = True):
    global SETTINGS

    if section not in list(SECTIONS.keys()):
        logger.error(f"Section '{section}' not found.")
        status_update(f"Section '{section}' not found.")
        return

    if SETTINGS["global_lock"]:
        logger.info(f"Global watering lock enabled - not proceeding.")
        status_update(f"Global watering lock enabled - not proceeding.")
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
    topic = msg.topic
    try:
        payload = json.loads(msg.payload.decode())
    except json.JSONDecodeError:
        payload = msg.payload.decode()

    if topic == mqtt_config["topic_prefix"] + "schedule":  # schedule set
        schedule.clear()

        tasks = []

        for task in payload["schedule"]:
            # schedule packet schema
            tasks.append({
                "section": task["section"],
                "start_at": task["start_at"],
                "end_at": task["end_at"],
                "every": task["every"] # day name(e.g. monday, tuesday...) / * for everyday
            })

        schedule_manager.save(tasks)
        settings_manager.save_schedule(tasks)
        set_schedule(tasks)
        logger.info(f"Schedule set. Schedule: {tasks}")
        status_update("Schedule set", False)

    elif topic == mqtt_config["topic_prefix"] + "manual":
        try:
            section = payload["section"]
            state = bool(payload["enabled"])
        except KeyError or ValueError:
            logger.error(f"Invalid payload {payload}")
            return

        section_watering(section, state)

    elif topic == mqtt_config["topic_prefix"] + "settings":
        global SETTINGS

        try:
            setting = payload["setting"]
            value = payload["value"]

            settings_manager.write(value, setting)
            SETTINGS = settings_manager.get()

        except KeyError:
            value = payload["value"]
            settings_manager.write(value)

            SETTINGS = settings_manager.get()

        except Exception as e:
            logger.error(f"Error: {e}")

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