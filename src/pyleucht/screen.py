import time
import pyleucht as pl

class Base:
    width: int
    height: int
    pixels: list[pl.Color]

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        # Initialize all pixels to black
        self.pixels = [
            [(0, 0, 0) for _ in range(self.width)]
            for _ in range(self.height)
        ]

    def fill(self, color: pl.Color):
        for y in range(self.height):
            for x in range(self.width):
                self.pixels[y][x] = color

    def update(self):
        raise NotImplementedError("Subclasses must implement this method.")

class WS2801(Base):
    """ WS2801-based screen using raw SPI """

    def __init__(self, width: int, height: int, bus: int = 0, device: int = 0, speed_hz: int = 1_000_000):
        super().__init__(width, height)

        print("Initializing WS2801 LED strip (SPI)...")

        self.num_leds = width * height
        try:
            import spidev
        except ImportError as e:
            raise RuntimeError("spidev is required for WS2801 screen") from e

        self._spi = spidev.SpiDev()
        self._spi.open(bus, device)
        self._spi.max_speed_hz = speed_hz

    def update(self):
        """
        Push the pixel buffer to the WS2801 strip.
        WS2801 expects raw RGB bytes.
        """
        data = bytearray()

        # Extend data and consider that the strip is wired in serpentine order
        for y in range(self.height):
            if y % 2 == 0:
                # even row: left to right
                for x in range(self.width):
                    r, g, b = self.pixels[y][x]
                    data.extend((r & 0xFF, g & 0xFF, b & 0xFF))
            else:
                # odd row: right to left
                for x in reversed(range(self.width)):
                    r, g, b = self.pixels[y][x]
                    data.extend((r & 0xFF, g & 0xFF, b & 0xFF))

        self._spi.xfer2(list(data))
        time.sleep(0.002)  # Latch delay

    def close(self):
        self._spi.close()


class Debug(Base):
    ''' pygame based screen for testing with optional wakeword visual indicator '''

    COLOR_BUTTON_OFF = (50, 50, 50)
    COLOR_BUTTON_ON = (0, 255, 0)
    BUTTON_HEIGHT = 30
    BUTTON_WIDTH = 30

    def __init__(self, width: int, height: int, buttons: pl.button.DebugHandler, pixel_size: int = 20):
        super().__init__(width, height)
        self._pixel_size = pixel_size
        self._buttons = buttons

        try:
            import pygame
        except ImportError as e:
            raise RuntimeError("pygame is required for Debug screen") from e

        self._pygame = pygame
        # buttons keys now on the instance since they depend on pygame
        self.BUTTON_KEYS = [
            self._pygame.K_1,
            self._pygame.K_2,
            self._pygame.K_3,
            self._pygame.K_4,
            self._pygame.K_5,
            self._pygame.K_6,
        ]

        # positions for the six buttons: left top/bottom, middle top/bottom, right top/bottom
        self._button_positions = [
            (0, height * self._pixel_size),
            (0, height * self._pixel_size + self.BUTTON_HEIGHT),
            (width * self._pixel_size // 2 - self.BUTTON_WIDTH // 2, height * self._pixel_size),
            (width * self._pixel_size // 2 - self.BUTTON_WIDTH // 2, height * self._pixel_size + self.BUTTON_HEIGHT),
            (width * self._pixel_size - self.BUTTON_WIDTH, height * self._pixel_size),
            (width * self._pixel_size - self.BUTTON_WIDTH, height * self._pixel_size + self.BUTTON_HEIGHT),
        ]

        self._pygame.init()
        self.surface = self._pygame.display.set_mode((self.width * self._pixel_size, self.height * self._pixel_size + 2 * self.BUTTON_HEIGHT))
        self._pygame.display.set_caption('Emulated LED Wall')

    def update(self):
        for y in range(self.height):
            for x in range(self.width):
                color = self.pixels[y][x]
                rect = self._pygame.Rect(x * self._pixel_size, y * self._pixel_size, self._pixel_size, self._pixel_size)
                self._pygame.draw.rect(self.surface, color, rect)
        
        # Buttons can also be on or off based on their LED state
        for i in range(6):
            x, y = self._button_positions[i]
            rect = self._pygame.Rect(x, y, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
            color = self.COLOR_BUTTON_ON if self._buttons.get_led_state(i) else self.COLOR_BUTTON_OFF
            self._pygame.draw.rect(self.surface, color, rect)

        self._pygame.display.flip()

        # Handle events: support window close, keyboard 1-6, and mouse clicks on simulated buttons
        for event in self._pygame.event.get():
            if event.type == self._pygame.QUIT:
                self._pygame.quit()
                exit()
            if event.type == self._pygame.KEYDOWN:
                if event.key in self.BUTTON_KEYS:
                    index = self.BUTTON_KEYS.index(event.key)
                    self._buttons.callback(index, True)
            if event.type == self._pygame.KEYUP:
                if event.key in self.BUTTON_KEYS:
                    index = self.BUTTON_KEYS.index(event.key)
                    self._buttons.callback(index, False)

            if event.type == self._pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for i in range(len(self.BUTTON_KEYS)):
                    x, y = self._button_positions[i]
                    rect = self._pygame.Rect(x, y, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
                    if rect.collidepoint(mx, my):
                        self._buttons.callback(i, True)
            if event.type == self._pygame.MOUSEBUTTONUP:
                mx, my = event.pos
                for i in range(len(self.BUTTON_KEYS)):
                    x, y = self._button_positions[i]
                    rect = self._pygame.Rect(x, y, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
                    if rect.collidepoint(mx, my):
                        self._buttons.callback(i, False)
