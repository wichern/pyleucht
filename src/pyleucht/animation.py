'''
An animation is anything that can be drawn to the LED wall over time.
'''

import pyleucht as pl

from collections.abc import Generator
import math
from PIL import Image

class Base:
    def __init__(self, bbox: pl.BBox = None):
        self.bbox = bbox

    def start(self):
        '''Called when the animation starts'''
        pass

    def stop(self):
        '''Called when the animation stops'''
        pass

    def points(self, screen) -> Generator[pl.Point, None, None]:
        if self.bbox:
            for point in self.bbox.points():
                yield point
        else:
            for point in screen.points():
                yield point

    def update(self, screen: type[pl.screen.Base], dt: float):
        '''
        Update the animation state and draw to the screen.

        :param screen: The screen object to draw on.
        :param dt: Time delta since last update in seconds.
        '''
        raise NotImplementedError("Subclasses must implement this method.")


class FillColor(Base):
    def __init__(self, color: pl.RGB, *, bbox: pl.BBox = None):
        super().__init__(bbox)
        self.color = color

    def update(self, screen: type[pl.screen.Base], dt: float):
        for point in self.points(screen):
            screen.set(point, self.color)


class VLine(Base):
    def __init__(self, color: pl.RGB, x: int):
        super().__init__()
        self.color = color
        self.x = x

    def update(self, screen: type[pl.screen.Base], dt: float):
        for y in range(screen.height):
            screen.set(pl.Point(self.x, y), self.color)


class HLine(Base):
    def __init__(self, color: pl.RGB, y: int):
        super().__init__()
        self.color = color
        self.y = y

    def update(self, screen: type[pl.screen.Base], dt: float):
        for x in range(screen.width):
            screen.set(pl.Point(x, self.y), self.color)


class RainbowCycle(Base):
    def __init__(self, speed: float = 1.0, *, bbox: pl.BBox = None):
        super().__init__(bbox)
        self.speed = speed
        self.position = 0.0

    def update(self, screen: type[pl.screen.Base], dt: float):
        self.position += self.speed * dt
        for point in self.points():
            hue = (self.position + (point.x + point.y) * 10) % 360
            screen.set(point, pl.RGB.from_hue(hue))


class Kaleidoscope(Base):
    def __init__(self, speed: float = 1.0, *, bbox: pl.BBox = None):
        super().__init__(bbox)
        self.speed = speed
        self.angle = 0.0

    def update(self, screen: type[pl.screen.Base], dt: float):
        self.angle += self.speed * dt
        if self.bbox:
            center = self.bbox.center_f()
        else:
            center = (
                float(screen.width) / 2.0,
                float(screen.height) / 2.0,
            )
        for point in self.points(screen):
            dx = float(point.x) - center[0]
            dy = float(point.y) - center[1]
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
        for point in self.points(screen):
            screen.set(point, pl.RGB(r, g, b))


class Text(Base):
    def __init__(self, text: str, pos: pl.Point, *, initial_wait: float = 0.0, speed: float = 0.0, color: pl.RGB = (255, 255, 255)):
        '''        
        :param text: Text
        :param pos: Top-Left position
        :param initial_wait: seconds to wait before starting to move
        :param speed: pixels in seconds
        :param color: Text color
        '''
        super().__init__()
        self.text = text
        self.pos = pos
        self.initial_wait = initial_wait
        self.speed = speed
        self.color = color
        self.offset = 0.0
        self.text_width = pl.font.text_width(self.text)

    def update(self, screen: type[pl.screen.Base], dt: float):
        if self.initial_wait > 0:
            self.initial_wait -= dt
        if self.initial_wait < 0:
            dt += -self.initial_wait
            self.initial_wait = 0
        if self.initial_wait == 0:
            self.offset += self.speed * dt

        # Draw visible characters
        draw_x = self.pos.x - int(self.offset)

        # if draw_x is less than -|text-width|, reset to screen.w
        if draw_x < -self.text_width:
            self.offset -= float(self.text_width) + screen.width

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


class PiggyLives(Base):
    def __init__(self):
        super().__init__()
        self.lives = 4

    def update(self, screen: type[pl.screen.Base], dt: float):
        color = pl.RGB(0, 127, 0)
        if self.lives == 3:
            color = pl.RGB(127, 255, 127)
        elif self.lives == 2:
            color = pl.RGB(255, 255, 0)
        if self.lives == 1:
            color = pl.RGB(255, 0, 0)
        # TODO: 0 lives is different
    
        for x in range(self.lives):
            for y in range(4):
                screen.set(pl.Point(screen.width - 4 + x, y), color)


class Sprite(Base):
    def __init__(self, image_path: str, pos: pl.Point = pl.Point(0, 0)):
        self.image = Image.open(image_path).convert('RGBA')
        super().__init__(pl.BBox(pl.Point(pos.x, pos.y), pl.Point(pos.x + self.image.width - 1, pos.y + self.image.height - 1)))
        self.pos = pos

    def update(self, screen: type[pl.screen.Base], dt: float):
        for x in range(self.image.width):
            for y in range(self.image.height):
                r, g, b, a = self.image.getpixel((x, y))
                if a == 255:
                    screen.set(pl.Point(int(self.pos.x + x), int(self.pos.y + y)), pl.RGB(r, g, b))


class SpriteAnimation(Base):
    def __init__(self, sprites: list[Sprite], speed: float, pos: pl.Point = pl.Point(0, 0)):
        """
        :param sprites: List of Sprite objects, all must have the same dimensions.
        :param speed: Animation speed in frames per second.
        :param pos: Top-left position where the animation is drawn.
        """
        if not sprites:
            raise ValueError("At least one sprite is required")
        # Assume all sprites have the same dimensions
        width = sprites[0].image.width
        height = sprites[0].image.height
        for sprite in sprites[1:]:
            if sprite.image.width != width or sprite.image.height != height:
                raise ValueError("All sprites must have the same dimensions")
        super().__init__(pl.BBox(pl.Point(pos.x, pos.y), pl.Point(pos.x + width - 1, pos.y + height - 1)))
        self.sprites = sprites
        self.speed = speed  # frames per second
        self.pos = pos
        self.current_frame = 0
        self.time_since_last = 0.0

    def update(self, screen: type[pl.screen.Base], dt: float):
        self.time_since_last += dt
        if self.time_since_last >= 1.0 / self.speed:
            self.current_frame = (self.current_frame + 1) % len(self.sprites)
            self.time_since_last = 0.0

        sprite = self.sprites[self.current_frame]
        for x in range(sprite.image.width):
            for y in range(sprite.image.height):
                r, g, b, a = sprite.image.getpixel((x, y))
                if a == 255:
                    screen.set(pl.Point(int(self.pos.x + x), int(self.pos.y + y)), pl.RGB(r, g, b))


class SpriteCharacter(Base):
    def __init__(self, animations: dict[str, SpriteAnimation], initial_state: str, pos: pl.Point = pl.Point(0, 0), velocity: pl.Point = pl.Point(0, 0)):
        super().__init__()
        self.animations = animations
        self.state = initial_state
        self.pos = pos
        self.velocity = velocity

    def set_state(self, state: str):
        self.state = state

    def update(self, screen: type[pl.screen.Base], dt: float):
        self.pos = pl.Point(math.floor(self.pos.x + self.velocity.x * dt), math.floor(self.pos.y + self.velocity.y * dt))
        if self.state in self.animations:
            anim = self.animations[self.state]
            anim.pos.x = int(self.pos.x)
            anim.pos.y = int(self.pos.y)
            anim.update(screen, dt)

