'''
An animation is anything that can be drawn to the LED wall over time.
'''

import pyleucht as pl

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
        for y in range(screen.height):
            for x in range(screen.width):
                hue = (self.position + (x + y) * 10) % 360
                screen.pixels[y][x] = self.hue_to_rgb(hue)

    @staticmethod
    def hue_to_rgb(hue: float) -> pl.Color:
        """Convert hue (0-360) to RGB color."""
        h = hue / 60.0
        c = 1.0
        x = c * (1 - abs(h % 2 - 1))
        if 0 <= h < 1:
            r, g, b = c, x, 0
        elif 1 <= h < 2:
            r, g, b = x, c, 0
        elif 2 <= h < 3:
            r, g, b = 0, c, x
        elif 3 <= h < 4:
            r, g, b = 0, x, c
        elif 4 <= h < 5:
            r, g, b = x, 0, c
        elif 5 <= h < 6:
            r, g, b = c, 0, x
        else:
            r, g, b = 0, 0, 0

        m = 0
        r = int((r + m) * 255)
        g = int((g + m) * 255)
        b = int((b + m) * 255)
        return (r, g, b)

class Kaleidoscope(Base):
    def __init__(self, speed: float = 1.0):
        super().__init__()
        self.speed = speed
        self.angle = 0.0

    def update(self, screen: type[pl.screen.Base], dt: float):
        self.angle += self.speed * dt
        center_x = screen.width / 2
        center_y = screen.height / 2
        for y in range(screen.height):
            for x in range(screen.width):
                dx = x - center_x
                dy = y - center_y
                distance = (dx**2 + dy**2) ** 0.5
                hue = (self.angle + distance * 10) % 360
                screen.pixels[y][x] = RainbowCycle.hue_to_rgb(hue)