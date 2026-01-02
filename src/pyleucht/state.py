'''
A stat consists of:
* A list of animations to be drawn on top of each other
* A list of button callbacks
* A button state initialization method
'''

import pyleucht as pl

class Base:
    def __init__(self, buttons: type[pl.button.HandlerBase]):
        self.buttons = buttons
        self.buttons.set_all_leds(False)
        self.animations = []

    def update(self, screen, dt):
        for animation in self.animations:
            animation.update(screen, dt)

    def handle_event(self, event: type[pl.event.Event]):
        if isinstance(event, pl.event.ButtonPressed):
            return self.on_button_pressed(event)
        if isinstance(event, pl.event.ButtonReleased):
            return self.on_button_released(event)

    def on_button_pressed(self, event: pl.event.ButtonPressed):
        return self

    def on_button_released(self, event: pl.event.ButtonReleased):
        return self


class Idle(Base):
    def __init__(self, buttons: type[pl.button.HandlerBase]):
        super().__init__(buttons)
        self.animations.append(pl.animation.Kaleidoscope(speed=-100.0))

    def on_button_pressed(self, event: pl.event.ButtonPressed):
        # if any button is pressed we want to switch to main menu state
        return pl.state.ProgramSelection(self.buttons)


class ProgramSelection(Base):
    BUTTON_UP = pl.button.BUTTON_TOP_MIDDLE
    BUTTON_DOWN = pl.button.BUTTON_BOTTOM_MIDDLE
    BUTTON_SELECT = pl.button.BUTTON_BOTTOM_RIGHT

    PROGRAMS = [
        "Rainbow",
        "Blink",
        "Wave",
    ]

    def __init__(self, buttons: type[pl.button.HandlerBase]):
        super().__init__(buttons)

        # Initialize button states for program selection
        self.buttons.set_led_state(self.BUTTON_UP, True)
        self.buttons.set_led_state(self.BUTTON_DOWN, True)
        self.buttons.set_led_state(self.BUTTON_SELECT, True)

        self.selected = 0

    def on_button_pressed(self, event: pl.event.ButtonPressed):
        if event.button_id == self.BUTTON_UP:
            self.selected = (self.selected - 1) % len(self.PROGRAMS)
        elif event.button_id == self.BUTTON_DOWN:
            self.selected = (self.selected + 1) % len(self.PROGRAMS)
        elif event.button_id == self.BUTTON_SELECT:
            pass #TODO: return new state based on selected program
        return self
