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
    def __init__(self, screen: type[pl.screen.Base], buttons: type[pl.button.HandlerBase]):
        self.screen = screen
        self.buttons = buttons
        self.animations = []

    def on_enter(self):
        self.buttons.set_all_leds(False)

    def on_leave(self):
        self.animations.clear()

    def on_frame(self):
        pass

    def update(self, dt):
        self.on_frame()
        for animation in self.animations:
            animation.update(self.screen, dt)

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

    def __init__(self, screen: type[pl.screen.Base], buttons: type[pl.button.HandlerBase]):
        super().__init__(screen, buttons)

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
    ''' A score board for table tennis matches '''

    BUTTON_PLAYER0_UP = pl.button.BUTTON_TOP_LEFT
    BUTTON_PLAYER0_DOWN = pl.button.BUTTON_BOTTOM_LEFT
    BUTTON_PLAYER1_UP = pl.button.BUTTON_TOP_RIGHT
    BUTTON_PLAYER1_DOWN = pl.button.BUTTON_BOTTOM_RIGHT
    BUTTON_BACK = pl.button.BUTTON_BOTTOM_MIDDLE

    COLOR_TIE = pl.RGB(255, 255, 255)
    COLOR_AHEAD = pl.RGB(0, 255, 0)
    COLOR_BEHIND = pl.RGB(255, 0, 0)

    LABEL_OFFSET_Y = 3

    def __init__(self, screen: type[pl.screen.Base], buttons: type[pl.button.HandlerBase]):
        super().__init__(screen, buttons)

        self.scores = [0, 0]

        self.bboxes = [
            pl.BBox(pl.Point(0, 0), pl.Point(screen.width // 2, screen.height)),
            pl.BBox(pl.Point(screen.width // 2 + 1, 0), pl.Point(screen.width, screen.height))
        ]

        self.backgrounds_default = [
            pl.animation.FillColor(pl.RGB(12, 12, 12), bbox=self.bboxes[0]),
            pl.animation.FillColor(pl.RGB(55, 55, 55), bbox=self.bboxes[1])
        ]
        self.backgrounds_won = [
            pl.animation.Kaleidoscope(100.0, bbox=self.bboxes[0]),
            pl.animation.Kaleidoscope(100.0, bbox=self.bboxes[1])
        ]
        self.backgrounds = self.backgrounds_default
        self.labels= []
        for player in range(2):
            self.labels.append(pl.animation.Text(text=str(self.scores[player]), pos=pl.Point(self._label_offset_x(str(self.scores[player]), player), self.LABEL_OFFSET_Y), color=self.COLOR_TIE))

    def on_enter(self):
        super().on_enter()
        self.buttons.set_led_state(self.BUTTON_PLAYER0_UP, True)
        self.buttons.set_led_state(self.BUTTON_PLAYER1_UP, True)
        self.buttons.set_led_state(self.BUTTON_BACK, True)
        for player in range(2):
            self.scores[player] = 0
        self.game_over = False
        self.animations.extend(self.backgrounds)
        self.animations.append(pl.animation.VLine(pl.RGB(127, 127, 127), self.screen.width // 2))
        self.animations.extend(self.labels)
        self._update_scores()

    def on_button_pressed(self, event: pl.event.ButtonPressed):
        if event.button_id == self.BUTTON_PLAYER0_UP and not self.game_over:
            self.scores[0] += 1
        if event.button_id == self.BUTTON_PLAYER0_DOWN and not self.game_over:
            self.scores[0] = max(0, self.scores[0] - 1)
        if event.button_id == self.BUTTON_PLAYER1_UP and not self.game_over:
            self.scores[1] += 1
        if event.button_id == self.BUTTON_PLAYER1_DOWN and not self.game_over:
            self.scores[1] = max(0, self.scores[1] - 1)

        if event.button_id == self.BUTTON_BACK:
            if self.scores[0] == 0 and self.scores[1] == 0:
                return (UserAction.BACK, None)
            for player in range(2):
                self.scores[player] = 0
                self.animations[player] = self.backgrounds_default[player]
            self.game_over = False

        self._update_scores()

        self.buttons.set_led_state(self.BUTTON_PLAYER0_DOWN, self.scores[0] > 0 and not self.game_over)
        self.buttons.set_led_state(self.BUTTON_PLAYER1_DOWN, self.scores[1] > 0 and not self.game_over)
        self.buttons.set_led_state(self.BUTTON_PLAYER0_UP, not self.game_over)
        self.buttons.set_led_state(self.BUTTON_PLAYER1_UP, not self.game_over)

        return (UserAction.NONE, None)

    def _update_scores(self):
        for player in range(2):
            score = self.scores[player]
            opponent_score = self.scores[(player + 1) % 2]

            if score == opponent_score:
                self.labels[player].color = self.COLOR_TIE
            elif score < opponent_score:
                self.labels[player].color = self.COLOR_BEHIND
            else:
                self.labels[player].color = self.COLOR_AHEAD
            
            self.labels[player].text = str(score)
            self.labels[player].pos.x = self._label_offset_x(self.labels[player].text, player)
            if not self.game_over:
                if score >= 11 and (score - opponent_score) >= 2:
                    self.game_over = True
                    self.animations[player] = self.backgrounds_won[player]

    def _label_offset_x(self, text: str, player: int):
        if player == 0:
            base = self.screen.width // 2
        else:
            base = self.screen.width

        return base - len(text) * (pl.font.get_char('0').width + 1)


class Animations(Base):
    BUTTON_UP = pl.button.BUTTON_TOP_RIGHT
    BUTTON_DOWN = pl.button.BUTTON_BOTTOM_RIGHT
    BUTTON_BACK = pl.button.BUTTON_BOTTOM_MIDDLE

    def __init__(self, screen: type[pl.screen.Base], buttons: type[pl.button.HandlerBase]):
        super().__init__(screen, buttons)

    def on_enter(self):
        super().on_enter()

    def on_button_pressed(self, event: pl.event.ButtonPressed):
        return (UserAction.NONE, None)


class ProgramSelection(Base):
    BUTTON_UP = pl.button.BUTTON_TOP_RIGHT
    BUTTON_DOWN = pl.button.BUTTON_BOTTOM_RIGHT
    BUTTON_SELECT = pl.button.BUTTON_TOP_MIDDLE
    BUTTON_BACK = pl.button.BUTTON_BOTTOM_MIDDLE

    def __init__(self, screen: type[pl.screen.Base], buttons: type[pl.button.HandlerBase], app_names: list[str]):
        super().__init__(screen, buttons)
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

