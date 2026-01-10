import time
import queue
import pyleucht as pl

class App:
    MAX_IDLE_FRAMES = 1000

    def __init__(self, screen: type[pl.screen.Base], buttons: type[pl.button.HandlerBase]):
        self.screen = screen
        self.event_queue = queue.Queue()
        self.buttons = buttons
        self.buttons.callback = lambda id, pressed: self.post_event(pl.event.ButtonPressed(id) if pressed else pl.event.ButtonReleased(id))
        
        self.apps = {
            "Tischtennis" : pl.state.TableTennis(self.buttons),
            "Animationen" : pl.state.Animations(self.buttons),
        }
        self.idle_state = pl.state.Idle(self.buttons)
        self.selection_state = pl.state.ProgramSelection(self.buttons, list(self.apps.keys()))
        self.state = self.idle_state
        self.state.on_enter()  # Initialize LED state for the initial state

    def run(self, fps: int):
        '''Run the main application loop at the specified frames per second.'''
        idle_frames = 0
        dt = 1.0 / fps
        next_frame_time = time.perf_counter()
        while True:
            # Dispatch events
            while not self.event_queue.empty():
                event = self.event_queue.get()
                action, selection = self.state.handle_event(event)
                if action != pl.state.UserAction.NONE:
                    self._handle_user_action(action, selection)
                idle_frames = 0

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

            if idle_frames > self.MAX_IDLE_FRAMES:
                self._change_state(self.idle_state)

            idle_frames += 1

    def post_event(self, event: type[pl.event.Event]):
        '''Post an event to the application's event queue.'''
        self.event_queue.put(event)

    def _handle_user_action(self, action, selection):
        if action == pl.state.UserAction.BACK:
            # When we are in program selection, we go back to idle
            if self.state == self.selection_state:
                self._change_state(self.idle_state)
            else:
                # When we are in an app, we go back to program selection
                # We assume that IdleState never calls BACK, so we must be in an app now
                self._change_state(self.selection_state)

        if action == pl.state.UserAction.SELECT:
            self._change_state(self.apps[selection])
        
        if action == pl.state.UserAction.WAKEUP:
            # Wakeup is called when any button is pressed in idle state
            self._change_state(self.selection_state)


    def _change_state(self, state):
        self.state.on_leave()
        self.state = state
        self.state.on_enter()