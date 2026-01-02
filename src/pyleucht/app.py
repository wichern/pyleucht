import time
import queue
import pyleucht as pl

class App:
    def __init__(self, screen: type[pl.screen.Base], buttons: type[pl.button.HandlerBase]):
        self.screen = screen
        self.event_queue = queue.Queue()
        self.buttons = buttons
        self.buttons.callback = lambda id, pressed: self.post_event(pl.event.ButtonPressed(id) if pressed else pl.event.ButtonReleased(id))
        self.state = pl.state.Idle(self.buttons)

    def run(self, fps: int):
        '''Run the main application loop at the specified frames per second.'''
        dt = 1.0 / fps
        next_frame_time = time.perf_counter()
        while True:
            # Dispatch events
            while not self.event_queue.empty():
                event = self.event_queue.get()
                print(f"Event: {event}")
                new_state = self.state.handle_event(event)
                if new_state is not self.state:
                    self.state = new_state

            # Update state and screen
            self.state.update(self.screen, dt)
            self.screen.update()

            # Frame limiting
            next_frame_time += dt
            sleep_time = next_frame_time - time.perf_counter()
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                # Frame overrun; skip sleeping
                next_frame_time = time.perf_counter()

    def post_event(self, event: type[pl.event.Event]):
        '''Post an event to the application's event queue.'''
        self.event_queue.put(event)
