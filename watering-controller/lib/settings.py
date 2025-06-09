from lib.logger import Logger
import json

class SettingsManager:
    _filepath = "writable/user-settings.json"
    _file = None
    settings = None

    _logger = None

    def __init__(self):
        self._logger = Logger("SettingsManager")
        self.settings = self._read()

        try:
            self._file = open(self._filepath, "r")

        except FileNotFoundError:
            self._logger.error("[!] Settings file not found.")
            self.__del__()

    def __del__(self):
        del self._logger

    def _read(self):
        with open(self._filepath, "r") as f:
            buffer = f.read()
            f.close()

        if buffer:
            try:
                settings = json.loads(buffer)

            except json.JSONDecodeError:
                self._logger.error("Invalid settings file.")
                settings = None
        else:
            settings = None

        return settings

    def get(self, setting = None):
        if setting:
            try:
                return self.settings[setting]

            except KeyError:
                self._logger.error(f"Undefined setting '{setting}'")
                return

        else:
            return self.settings

    def write(self, data, section: str = None):
        if section:
            self.settings = self._read()
            self.settings[section] = data

        else:
            self.settings = data

        with open(self._filepath, "w") as f:
            f.write(json.dumps(self.settings, indent=4))
            f.close()

        self._read()

    # schedule
    def save_schedule(self, schedule: list):
        self.write(schedule, "schedule")

    def read_schedule(self):
        return self.get("schedule")