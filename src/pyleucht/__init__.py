from dataclasses import dataclass

@dataclass
class RGB:
    r: int
    g: int
    b: int

    def clamp(self) -> "RGB":
        """Return a new RGB with each component clamped to 0–255."""
        return RGB(
            r=max(0, min(255, self.r)),
            g=max(0, min(255, self.g)),
            b=max(0, min(255, self.b)),
        )

    def to_rgba(self, a: int = 255) -> "RGBA":
        """Convert RGB to RGBA by adding an alpha value."""
        return RGBA(self.r, self.g, self.b, a)

    def to_tuple(self) -> tuple[int, int, int]:
        return (self.r, self.g, self.b)

    @staticmethod
    def from_hue(hue) -> "RGB":
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
        return RGB(r, g, b)

@dataclass
class RGBA:
    r: int
    g: int
    b: int
    a: int

    def clamp(self) -> "RGBA":
        """Return a new RGBA with each component clamped to 0–255."""
        return RGBA(
            r=max(0, min(255, self.r)),
            g=max(0, min(255, self.g)),
            b=max(0, min(255, self.b)),
            a=max(0, min(255, self.a)),
        )

@dataclass
class Point:
    x: int
    y: int

    def move(self, dx: int, dy: int) -> "Point":
        """Return a new point shifted by (dx, dy)."""
        return Point(self.x + dx, self.y + dy)

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point") -> "Point":
        return Point(self.x - other.x, self.y - other.y)

    @staticmethod
    def points(w: int, h: int):
        for y in range(h):
            for x in range(w):
                yield Point(x, y)


import pyleucht.font
import pyleucht.button
import pyleucht.screen
import pyleucht.animation
import pyleucht.event
import pyleucht.state
import pyleucht.app

