from lib.logger import Logger
import RPi.GPIO as GPIO

class GPIOController:
    _logger = None
    def __init__(self):
        self._logger = Logger("GPIOController")
        GPIO.setmode(GPIO.BCM)

    def _set_as_output(self, pin:int):
        GPIO.setup(pin, GPIO.OUT)

    def set_high(self, pin:int):
        self._set_as_output(pin)

        GPIO.output(pin, GPIO.HIGH)

    def set_low(self, pin:int):
        self._set_as_output(pin)

        GPIO.output(pin, GPIO.LOW)

    def __del__(self):
        GPIO.cleanup()