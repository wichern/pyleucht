import argparse
import pyleucht as pl

SCREEN_WIDTH = 21
SCREEN_HEIGHT = 12

def main():
    parser = argparse.ArgumentParser(description="Pyleucht LED Wall with Wake Word Detection")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode with pygame screen")
    parser.add_argument("--spi-bus", type=int, default=0, help="SPI bus number (default: 0)")
    parser.add_argument("--spi-device", type=int, default=0, help="SPI device number (default: 0)")
    parser.add_argument("--spi-speed", type=int, default=1_000_000, help="SPI speed in Hz (default: 1,000,000)")
    parser.add_argument("--fps", type=int, default=30, help="Frame rate in frames per second (default: 30)")
    args = parser.parse_args()

    ui = None
    buttons = None
    if args.debug:
        buttons = pl.button.DebugHandler()
        ui = pl.screen.Debug(SCREEN_WIDTH, SCREEN_HEIGHT, buttons=buttons)
    else:
        buttons = pl.button.GPIOHandler(
            gpio_push=[17, 22, 5, 13, 26, 20],
            gpio_led=[27, 10, 6, 19, 21, 16]
        )
        ui = pl.screen.WS2801(SCREEN_WIDTH, SCREEN_HEIGHT, bus=args.spi_bus, device=args.spi_device, speed_hz=args.spi_speed)

    app = pl.app.App(ui, buttons)
    app.run(fps=args.fps)

if __name__ == "__main__":
    main()
