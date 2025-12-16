import argparse
from pyleucht import ScreenTest, ScreenWS2801, Button, EventBus, ButtonPressed, ButtonReleased
import time

SCREEN_WIDTH = 21
SCREEN_HEIGHT = 12

class State:
    STARTING = 0
    IDLE = 1
    PROGRAM_SELECTION = 2
    LISTENING = 3
    RUNNING_PROGRAM = 4

def main():
    parser = argparse.ArgumentParser(description="Pyleucht LED Wall with Wake Word Detection")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode with pygame screen")
    parser.add_argument("--spi-bus", type=int, default=0, help="SPI bus number (default: 0)")
    parser.add_argument("--spi-device", type=int, default=0, help="SPI device number (default: 0)")
    parser.add_argument("--spi-speed", type=int, default=1_000_000, help="SPI speed in Hz (default: 1,000,000)")
    parser.add_argument("--fps", type=int, default=30, help="Frame rate in frames per second (default: 30)")
    args = parser.parse_args()

    events = EventBus()
    
    ui = None
    buttons = None
    if args.debug:
        # Create callbacks pushing ButtonPressed/ButtonReleased events
        button_callbacks = [lambda pressed, id=i+1: events.post(ButtonPressed(id)) if pressed else events.post(ButtonReleased(id)) for i in range(6)]
        ui = ScreenTest(SCREEN_WIDTH, SCREEN_HEIGHT, button_cbs=button_callbacks)
    else:
        ui = ScreenWS2801(SCREEN_WIDTH, SCREEN_HEIGHT, bus=args.spi_bus, device=args.spi_device, speed_hz=args.spi_speed)
        Button.initialize()
        buttons = [
            Button(id=1, button_pin=17, led_pin=27, on_down=lambda id: events.post(ButtonPressed(id)), on_up=lambda id: events.post(ButtonReleased(id))),
            Button(id=2, button_pin=22, led_pin=10, on_down=lambda id: events.post(ButtonPressed(id)), on_up=lambda id: events.post(ButtonReleased(id))),
            Button(id=3, button_pin=5,  led_pin=6,  on_down=lambda id: events.post(ButtonPressed(id)), on_up=lambda id: events.post(ButtonReleased(id))),
            Button(id=4, button_pin=13, led_pin=19, on_down=lambda id: events.post(ButtonPressed(id)), on_up=lambda id: events.post(ButtonReleased(id))),
            Button(id=5, button_pin=26, led_pin=21, on_down=lambda id: events.post(ButtonPressed(id)), on_up=lambda id: events.post(ButtonReleased(id))),
            Button(id=6, button_pin=20, led_pin=16, on_down=lambda id: events.post(ButtonPressed(id)), on_up=lambda id: events.post(ButtonReleased(id))),
        ]

    state = State.STARTING

    events.register(ButtonPressed, lambda event: print(f"Button {event.button_id} pressed"))
    events.register(ButtonReleased, lambda event: print(f"Button {event.button_id} released"))

    dt = 1.0 / args.fps
    next_frame_time = time.perf_counter()
    while True:
        events.dispatch_all()
        ui.update()

        # Frame limiting
        next_frame_time += dt
        sleep_time = next_frame_time - time.perf_counter()
        if sleep_time > 0:
            time.sleep(sleep_time)
        else:
            # Frame overrun; skip sleeping
            next_frame_time = time.perf_counter()

if __name__ == "__main__":
    main()
