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
        except ImportError as e:
            raise RuntimeError("RPi.GPIO module is required for GPIO button handling") from e

        assert len(gpio_push) == 6 and len(gpio_led) == 6, "Expected 6 GPIO pins for buttons and LEDs"
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Setup buttons and LEDs
        for i in range(6):
            GPIO.setup(gpio_push[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(gpio_led[i], GPIO.OUT)
            GPIO.output(gpio_led[i], GPIO.LOW)
            
            # Try to use hardware edge detection; on failure, fall back to polling.
            def _make_cb(index):
                def _cb(channel):
                    pressed = GPIO.input(channel) == GPIO.LOW
                    self.callback(index, pressed)
                return _cb

            try:
                GPIO.add_event_detect(
                    gpio_push[i],
                    GPIO.BOTH,
                    callback=_make_cb(i),
                    bouncetime=GPIOHandler.BOUNCE_TIME_MS
                )
            except RuntimeError:
                # Fall back to polling if edge detection cannot be added.
                if not hasattr(self, '_polling_needed'):
                    self._polling_needed = True
                    self._last_states = {}
                self._last_states[gpio_push[i]] = GPIO.input(gpio_push[i])

class DebugHandler(HandlerBase):
    '''
        # If any add_event_detect failed above, start a single polling thread.
        if getattr(self, '_polling_needed', False):
            import threading, time

            def _poll():
                while True:
                    for idx, pin in enumerate(gpio_push):
                        try:
                            state = GPIO.input(pin)
                        except Exception:
                            continue
                        last = self._last_states.get(pin, state)
                        if state != last:
                            pressed = state == GPIO.LOW
                            self.callback(idx, pressed)
                            self._last_states[pin] = state
                    time.sleep(0.02)

            self._polling_thread = threading.Thread(target=_poll, daemon=True)
            self._polling_thread.start()
    '''

    def __init__(self):
        super().__init__()