from dataclasses import dataclass
from collections.abc import Generator

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
class Point:
    x: int
    y: int

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point") -> "Point":
        return Point(self.x - other.x, self.y - other.y)

    @staticmethod
    def points(w: int, h: int) -> Generator["Point", None, None]:
        for y in range(h):
            for x in range(w):
                yield Point(x, y)

class BBox:
    def __init__(self, min: Point, max: Point):
        self.min = min
        self.max = max

    def points(self) -> Generator[Point, None, None]:
        for y in range(self.min.y, self.max.y):
            for x in range(self.min.x, self.max.x):
                yield Point(x, y)

    def center(self) -> Point:
        return Point(
            self.min.x + ((self.max.x - self.min.x) // 2),
            self.min.y + ((self.max.y - self.min.y) // 2)
        )
    
    def center_f(self) -> tuple[float]:
        return (
            float(self.min.x) + (float(self.max.x - self.min.x) / 2.0),
            float(self.min.y) + (float(self.max.y - self.min.y) / 2.0)
        )

import pyleucht.font
import pyleucht.button
import pyleucht.screen
import pyleucht.animation
import pyleucht.event
import pyleucht.state
import pyleucht.app

