from typing import Callable

try:
    import RPi.GPIO as GPIO
    HAS_GPIO = True
except RuntimeError:
    HAS_GPIO = False

BOUNCE_TIME_MS = 50

class Button:
    @staticmethod
    def initialize():
        if HAS_GPIO:
            GPIO.setmode(GPIO.BCM)

    '''
    Represents a physical button with an associated LED.

    Note: Button.initialize() must be called before creating Button instances.
    '''
    def __init__(self, id: int, button_pin: int, on_down: Callable, on_up: Callable, led_pin: int = None):
        self.id = id
        self.button_pin = button_pin
        self.led_pin = led_pin
        self.led_state = False
        self.on_down = on_down
        self.on_up = on_up

        if HAS_GPIO:
            GPIO.setup(self.button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            if self.on_down:
                GPIO.add_event_detect(self.button_pin, GPIO.FALLING, callback=lambda channel: self.on_down(self.id), bouncetime=BOUNCE_TIME_MS)
            if self.on_up:
                GPIO.add_event_detect(self.button_pin, GPIO.RISING, callback=lambda channel: self.on_up(self.id), bouncetime=BOUNCE_TIME_MS)

            if self.led_pin is not None:
                GPIO.setup(self.led_pin, GPIO.OUT)
                GPIO.output(self.led_pin, GPIO.LOW)

    def set_led(self, state: bool):
        if HAS_GPIO and self.led_pin is not None and self.led_state != state:
            GPIO.output(self.led_pin, GPIO.HIGH if state else GPIO.LOW)
            self.led_state = state