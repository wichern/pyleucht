'''
An animation is anything that can be drawn to the LED wall over time.
'''

import pyleucht as pl

import math

class Base:
    def __init__(self):
        pass

    def start(self):
        '''Called when the animation starts'''
        pass

    def stop(self):
        '''Called when the animation stops'''
        pass

    def update(self, screen: type[pl.screen.Base], dt: float):
        '''
        Update the animation state and draw to the screen.

        :param screen: The screen object to draw on.
        :param dt: Time delta since last update in seconds.
        '''
        raise NotImplementedError("Subclasses must implement this method.")

class RainbowCycle(Base):
    def __init__(self, speed: float = 1.0):
        super().__init__()
        self.speed = speed
        self.position = 0.0

    def update(self, screen: type[pl.screen.Base], dt: float):
        self.position += self.speed * dt
        for point in screen.points():
            hue = (self.position + (point.x + point.y) * 10) % 360
            screen.set(point, pl.RGB.from_hue(hue))

class Kaleidoscope(Base):
    def __init__(self, speed: float = 1.0):
        super().__init__()
        self.speed = speed
        self.angle = 0.0

    def update(self, screen: type[pl.screen.Base], dt: float):
        self.angle += self.speed * dt
        center_x = screen.width / 2
        center_y = screen.height / 2
        for point in screen.points():
            dx = point.x - center_x
            dy = point.y - center_y
            distance = (dx**2 + dy**2) ** 0.5
            hue = (self.angle + distance * 10) % 360
            screen.set(point, pl.RGB.from_hue(hue))

class BreathingGlow(Base):
    def __init__(self, color: pl.RGB = pl.RGB(0, 0, 255), speed: float = 1.0):
        super().__init__()
        self.color = color
        self.speed = speed
        self.phase = 0.0

    def update(self, screen: type[pl.screen.Base], dt: float):
        self.phase += self.speed * dt
        brightness = (1 + math.sin(self.phase)) / 2  # Normalize to [0, 1]
        r = int(self.color.r * brightness)
        g = int(self.color.g * brightness)
        b = int(self.color.b * brightness)
        screen.fill(pl.RGB(r, g, b))

class Text(Base):
    def __init__(self, text: str, pos: pl.Point, *, initial_wait: float = 0.0, speed: float = 0.0, color: pl.RGB = (255, 255, 255)):
        super().__init__()
        self.text = text
        self.pos = pos
        self.initial_wait = initial_wait
        self.speed = speed
        self.color = color
        self.offset = 0.0

    def update(self, screen: type[pl.screen.Base], dt: float):
        if self.initial_wait > 0:
            self.initial_wait -= dt
        if self.initial_wait < 0:
            dt += -self.initial_wait
            self.initial_wait = 0
        if self.initial_wait == 0:
            self.offset += self.speed * dt

        # Draw visible characters
        draw_x = self.pos.x
        for ch in self.text:
            if draw_x >= screen.width:
                break

            char = pl.font.get_char(ch)
            self.draw_char(char, pl.Point(draw_x, self.pos.y), screen)
            draw_x += char.width + 1 # +1 for spacing

    def draw_char(self, char: pl.font.Char, pos: pl.Point, screen: type[pl.screen.Base]):
        for point in pl.Point.points(char.width, pl.font.HEIGHT):
            if char.is_set(point):
                screen.set(pos + point, self.color)
