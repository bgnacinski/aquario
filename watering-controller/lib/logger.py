from lib.config import ConfigManager
import datetime

class Logger:
    log_filename = ""
    log_level = None
    module_name = ""

    _LOG_LEVELS = {
        "debug": 4,
        "info": 3,
        "warning": 2,
        "error": 1
    }
    _file_obj = None

    def __init__(self, module_name: str):
        config_manager = ConfigManager("config.json")

        self.module_name = module_name
        self.log_level = config_manager.get("log_level")

        date = datetime.datetime.now()
        self.log_filename = f"writable/logs/aquario-{date.year}-{date.month}-{date.day}.log"

        self._file_obj = open(self.log_filename, "a")

    def _base_log(self, message: str, level: str):
        if self._LOG_LEVELS[self.log_level] < self._LOG_LEVELS[level]:
            return

        now = datetime.datetime.now()
        time_str = f"[{now.year}-{now.month}-{now.day} {now.hour}:{now.minute}:{now.second}]"

        entry = "".join([time_str, " " + level.upper(), f" {self.module_name} | ", message]) + "\n"

        print(entry, end="")

        self._file_obj.write(entry)
        self._file_obj.flush()

    def debug(self, message: str):
        self._base_log(message, "debug")

    def info(self, message: str):
        self._base_log(message, "info")

    def warning(self, message: str):
        self._base_log(message, "warning")

    def error(self, message: str):
        self._base_log(message, "error")