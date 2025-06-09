from lib.logger import Logger
import json

class ScheduleManager:
    _filepath = ""
    _logger = None

    def __init__(self, filepath="writable/schedule.json"):
        self._logger = Logger("ScheduleManager")
        self._filepath = filepath

        try:
            self._file = open(filepath, "r")

        except FileNotFoundError:
            self._logger.error("Schedule file not found.")
            self.__del__()

    def __del__(self):
        del self._logger

    def read(self):
        with open(self._filepath, "r") as schedule:
            content = schedule.read()
            schedule.close()

        if content:
            try:
                schedule_json = json.loads(content)

            except json.JSONDecodeError:
                self._logger.error("Invalid schedule file.")

        else:
            schedule_json = None

        return schedule_json

    def save(self, schedule:list):
        try:
            json_data = json.dumps(schedule, indent=4)
            self._file.close()

            with open(self._filepath, "w") as f:
                f.write(json_data)
                f.close()

        except Exception as e:
            self._logger.error("An error has occured during schedule saving. Error: " + str(e))