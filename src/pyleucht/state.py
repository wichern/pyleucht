'''
A state consists of:
* A list of animations to be drawn on top of each other
* A list of button callbacks
* A button state initialization method
'''

import pyleucht as pl

class UserAction:
    ''' Main actions '''
    NONE = 0
    BACK = 1
    SELECT = 2
    WAKEUP = 3

class Base:
    def __init__(self, buttons: type[pl.button.HandlerBase]):
        self.buttons = buttons
        self.animations = []

    def on_enter(self):
        self.buttons.set_all_leds(False)

    def on_leave(self):
        self.animations.clear()

    def on_frame(self):
        pass

    def update(self, screen, dt):
        self.on_frame()
        for animation in self.animations:
            animation.update(screen, dt)

    def handle_event(self, event: type[pl.event.Event]):
        if isinstance(event, pl.event.ButtonPressed):
            return self.on_button_pressed(event)
        if isinstance(event, pl.event.ButtonReleased):
            return self.on_button_released(event)

    def on_button_pressed(self, event: pl.event.ButtonPressed):
        return (UserAction.NONE, None)

    def on_button_released(self, event: pl.event.ButtonReleased):
        return (UserAction.NONE, None)


class Idle(Base):
    MAX_IDLE_FRAMES = 100

    def __init__(self, buttons: type[pl.button.HandlerBase]):
        super().__init__(buttons)

    def on_enter(self):
        super().on_enter()
        self.animations.append(pl.animation.Kaleidoscope(speed=-100.0))
        self.idle = 0

    def on_frame(self):
        self.idle += 1
        if self.idle > self.MAX_IDLE_FRAMES:
            self.animations.clear()
            self.animations.append(pl.animation.FillColor(pl.RGB(0, 0, 0)))

    def on_button_pressed(self, event: pl.event.ButtonPressed):
        # if any button is pressed we want to switch to main menu state
        return (UserAction.WAKEUP, None)


class TableTennis(Base):
    BUTTON_PLAYER0_UP = pl.button.BUTTON_TOP_LEFT
    BUTTON_PLAYER0_DOWN = pl.button.BUTTON_BOTTOM_LEFT
    BUTTON_PLAYER1_UP = pl.button.BUTTON_TOP_RIGHT
    BUTTON_PLAYER1_DOWN = pl.button.BUTTON_BOTTOM_RIGHT
    BUTTON_BACK = pl.button.BUTTON_BOTTOM_MIDDLE

    COLOR_TIE = pl.RGB(255, 255, 255)
    COLOR_AHEAD = pl.RGB(0, 255, 0)
    COLOR_BEHIND = pl.RGB(255, 0, 0)

    BASE_POS_X_0_1DIGIT = 6
    BASE_POS_X_0_2DIGIT = 2
    BASE_POS_X_1_1DIGIT = 17
    BASE_POS_X_1_2DIGIT = 13

    ''' Table tennis score board '''
    def __init__(self, buttons: type[pl.button.HandlerBase]):
        super().__init__(buttons)
        self.background = pl.animation.FillColor(pl.RGB(0, 0, 0))
        self.label0 = pl.animation.Text(text='0', pos=pl.Point(self.BASE_POS_X_0_1DIGIT, 3), color=self.COLOR_TIE)
        self.label1 = pl.animation.Text(text='0', pos=pl.Point(self.BASE_POS_X_1_1DIGIT, 3), color=self.COLOR_TIE)

    def on_enter(self):
        super().on_enter()
        self.buttons.set_led_state(self.BUTTON_PLAYER0_UP, True)
        self.buttons.set_led_state(self.BUTTON_PLAYER1_UP, True)
        self.buttons.set_led_state(self.BUTTON_BACK, True)
        self.score0 = 0
        self.score1 = 0
        self.game_over = False
        self.animations.append(self.background)
        self.animations.append(pl.animation.VLine(pl.RGB(127, 127, 127), 10))
        self.animations.append(self.label0)
        self.animations.append(self.label1)
        self._update_score(self.label0, self.score0, self.score1, self.BASE_POS_X_0_1DIGIT, self.BASE_POS_X_0_2DIGIT)
        self._update_score(self.label1, self.score1, self.score0, self.BASE_POS_X_1_1DIGIT, self.BASE_POS_X_1_2DIGIT)

    def on_button_pressed(self, event: pl.event.ButtonPressed):
        if event.button_id == self.BUTTON_PLAYER0_UP and not self.game_over:
            self.score0 += 1
        if event.button_id == self.BUTTON_PLAYER0_DOWN and not self.game_over:
            self.score0 = max(0, self.score0 - 1)
        if event.button_id == self.BUTTON_PLAYER1_UP and not self.game_over:
            self.score1 += 1
        if event.button_id == self.BUTTON_PLAYER1_DOWN and not self.game_over:
            self.score1 = max(0, self.score1 - 1)

        if event.button_id == self.BUTTON_BACK:
            if self.score0 == 0 and self.score1 == 0:
                return (UserAction.BACK, None)
            self.score0 = 0
            self.score1 = 0
            self.game_over = False

        self._update_score(self.label0, self.score0, self.score1, self.BASE_POS_X_0_1DIGIT, self.BASE_POS_X_0_2DIGIT)
        self._update_score(self.label1, self.score1, self.score0, self.BASE_POS_X_1_1DIGIT, self.BASE_POS_X_1_2DIGIT)

        self.buttons.set_led_state(self.BUTTON_PLAYER0_DOWN, self.score0 > 0 and not self.game_over)
        self.buttons.set_led_state(self.BUTTON_PLAYER1_DOWN, self.score1 > 0 and not self.game_over)
        self.buttons.set_led_state(self.BUTTON_PLAYER0_UP, not self.game_over)
        self.buttons.set_led_state(self.BUTTON_PLAYER1_UP, not self.game_over)

        return (UserAction.NONE, None)

    def _update_score(self, label, score, opponent_score, base_pos_1d, base_pos_2d):
        if score == opponent_score:
            label.color = self.COLOR_TIE
        elif score < opponent_score:
            label.color = self.COLOR_BEHIND
        else:
            label.color = self.COLOR_AHEAD
        
        label.text = str(score)

        if score < 10:
            label.pos.x = base_pos_1d
        else:
            label.pos.x = base_pos_2d

        self.game_over = score >= 11 and (score - opponent_score) >= 2

class Animations(Base):
    BUTTON_UP = pl.button.BUTTON_TOP_RIGHT
    BUTTON_DOWN = pl.button.BUTTON_BOTTOM_RIGHT
    BUTTON_BACK = pl.button.BUTTON_BOTTOM_MIDDLE

    def __init__(self, buttons: type[pl.button.HandlerBase]):
        super().__init__(buttons)

    def on_enter(self):
        super().on_enter()

    def on_button_pressed(self, event: pl.event.ButtonPressed):
        return (UserAction.NONE, None)


class ProgramSelection(Base):
    BUTTON_UP = pl.button.BUTTON_TOP_RIGHT
    BUTTON_DOWN = pl.button.BUTTON_BOTTOM_RIGHT
    BUTTON_SELECT = pl.button.BUTTON_TOP_MIDDLE
    BUTTON_BACK = pl.button.BUTTON_BOTTOM_MIDDLE

    def __init__(self, buttons: type[pl.button.HandlerBase], app_names: list[str]):
        super().__init__(buttons)
        self.selected = 0
        self.app_names = app_names

    def on_enter(self):
        super().on_enter()
        self.buttons.set_led_state(self.BUTTON_UP, True)
        self.buttons.set_led_state(self.BUTTON_DOWN, True)
        self.buttons.set_led_state(self.BUTTON_SELECT, True)
        self.buttons.set_led_state(self.BUTTON_BACK, True)

        self.animations.append(pl.animation.BreathingGlow(color=pl.RGB(0, 0, 255), speed=1.0))
        self.label = pl.animation.Text(text=self.app_names[self.selected], pos=pl.Point(0, 3), color=pl.RGB(255, 255, 255), initial_wait=0.5, speed=8.0)
        self.animations.append(self.label)

    def on_button_pressed(self, event: pl.event.ButtonPressed):
        if event.button_id == self.BUTTON_UP:
            self.selected = (self.selected - 1) % len(self.app_names)
            self._update_label()
        elif event.button_id == self.BUTTON_DOWN:
            self.selected = (self.selected + 1) % len(self.app_names)
            self._update_label()
        elif event.button_id == self.BUTTON_SELECT:
            return (UserAction.SELECT, self.app_names[self.selected])
        elif event.button_id == self.BUTTON_BACK:
            return (UserAction.BACK, None)
        return (UserAction.NONE, None)
    
    def _update_label(self):
        self.label = pl.animation.Text(text=self.app_names[self.selected], pos=pl.Point(0, 3), color=pl.RGB(255, 255, 255), initial_wait=0.5, speed=8.0)
        self.animations[1] = self.label

