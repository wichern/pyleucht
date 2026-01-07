import logging

BUTTON_TOP_LEFT = 0
BUTTON_BOTTOM_LEFT = 1
BUTTON_TOP_MIDDLE = 2
BUTTON_BOTTOM_MIDDLE = 3
BUTTON_TOP_RIGHT = 4
BUTTON_BOTTOM_RIGHT = 5

class HandlerBase:
    '''
    Base class for button and LED handlers.
    '''

    def __init__(self):
        self._states = [False] * 6
        self.callback = lambda button_id, pressed: None  # Placeholder for user-defined callback

    def set_led_state(self, button_id: int, state: bool):
        self._states[button_id] = state

    def get_led_state(self, button_id: int) -> bool:
        return self._states[button_id]
    
    def set_all_leds(self, state: bool):
        for i in range(6):
            self.set_led_state(i, state)

class GPIOHandler(HandlerBase):
    '''
    Handles physical buttons and LEDs using RPi.GPIO.
    Assumes 6 buttons and 6 LEDs connected to specified GPIO pins.
    '''

    BOUNCE_TIME_MS = 50

    def __init__(self, gpio_push: list[int], gpio_led: list[int]):
        super().__init__()

        try:
            import RPi.GPIO as GPIO
            self._GPIO = GPIO
        except Exception as e:
            logging.warning("RPi.GPIO not available or unusable: %s", e)
            return

        self._gpio_available = True
        assert len(gpio_push) == 6 and len(gpio_led) == 6, "Expected 6 GPIO pins for buttons and LEDs"
        self._gpio_push = list(gpio_push)
        self._gpio_led = list(gpio_led)

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Setup buttons and LEDs
        for i in range(6):
            GPIO.setup(self._gpio_push[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self._gpio_led[i], GPIO.OUT)
            GPIO.output(self._gpio_led[i], GPIO.LOW)

            GPIO.add_event_detect(
                self._gpio_push[i],
                GPIO.RISING,
                callback=self._button_up_callback,
                bouncetime=self.BOUNCE_TIME_MS,
            )

            GPIO.add_event_detect(
                self._gpio_push[i],
                GPIO.FALLING,
                callback=self._button_down_callback,
                bouncetime=self.BOUNCE_TIME_MS,
            )

    def _button_up_callback(self, channel):
        button_id = self._gpio_push.index(channel)
        self.callback(button_id, pressed=False)
    
    def _button_down_callback(self, channel):
        button_id = self._gpio_push.index(channel)
        self.callback(button_id, pressed=True)

class DebugHandler(HandlerBase):
    """
    Simple debug/no-op handler used when GPIO is not available.
    Keeps internal LED/button state and exposes the same API as GPIOHandler.
    """

    def __init__(self):
        super().__init__()