import ipaddress
import json

class ConfigManager:
    _filename = ""
    _config = None

    _CONFIG_KEYS = [
        "log_level", "mqtt", "sections"
    ]

    def __init__(self, filename: str):
        self._filename = filename

        self._load_config()

    def _load_config(self):
        with open(self._filename, "r") as f:
            if not f.readable():
                raise Exception(f"Config file {self._filename} is not readable.")

            config_data = f.read()

            if self._validate_config(config_data):
                self._config = json.loads(config_data)
            else:
                self._config = {}

    def _validate_config(self, config_data: str):
        valid = True

        # try to parse JSON
        try:
            config = json.loads(config_data)
        except json.JSONDecodeError:
            print(f"[!] Contents of {self._filename} are not valid JSON data")
            valid = False

            return valid

        # check if log level is present and is within expected values
        if not config["log_level"]:
            print("[!] The log level must be specified by 'log' property")
            valid = False
        else:
            if config["log_level"] not in ["debug", "info", "warning", "error"]:
                print("[!] Invalid log level specified. Allowed values: debug, info, warning, error.")
                valid = False

        # check mqtt section
        if not config["mqtt"]:
            print("[!] The log level must be specified by 'log' property")
            valid = False
        else:
            config_node = config["mqtt"]

            if config_node["port"] not in range(2, 65535):
                print("[!] Invalid port number specified. Allowed values: 2 -> 65535")
                valid = False

            if type(config_node["timeout"]) != int:
                print("[!] Invalid timeout time specified. Number required.")
                valid = False

            if not config_node["topic_prefix"]:
                print("[!] Topic prefix has to be specified.")
                valid = False

            if type(config_node["topic_prefix"]) != str:
                print("[!] Topic prefix has to be a string.")
                valid = False

        return valid

    def get(self, section: str = None):
        if section and section not in self._CONFIG_KEYS:
            raise Exception("Section must be one of " + str(self._CONFIG_KEYS))
        elif not section:
            return self._config
        else:
            return self._config[section]