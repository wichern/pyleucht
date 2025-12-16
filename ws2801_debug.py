#!/usr/bin/env python
# -*- coding: utf-8 -*-

import spidev
import argparse
import time
import sys
import board
import adafruit_ws2801

def print_spi_info():
    for bus in range(2):  # typically 0 and 1 on Raspberry Pi
        for device in range(2):  # typically 0 and 1
            try:
                spi = spidev.SpiDev()
                spi.open(bus, device)
                def fmt_speed(hz):
                    try:
                        hz = int(hz)
                    except Exception:
                        return str(hz)
                    if hz >= 1_000_000:
                        return f"{hz/1_000_000:.3g} MHz ({hz} Hz)"
                    if hz >= 1_000:
                        return f"{hz/1_000:.3g} kHz ({hz} Hz)"
                    return f"{hz} Hz"

                def present(name, val):
                    return f"{name}: {val}"

                devpath = f"/dev/spidev{bus}.{device}"
                max_speed = getattr(spi, 'max_speed_hz', 'N/A')
                mode = getattr(spi, 'mode', 'N/A')
                bits = getattr(spi, 'bits_per_word', getattr(spi, 'bits_per_word', 'N/A'))
                threewire = getattr(spi, 'threewire', 'N/A')
                cs_high = getattr(spi, 'cs_high', 'N/A')
                no_cs = getattr(spi, 'no_cs', 'N/A')
                lsbfirst = getattr(spi, 'lsbfirst', 'N/A')

                print("+----------------------------------------+")
                print(f"| SPI device: {devpath}")
                print("+----------------------------------------+")
                print(present('Max speed', fmt_speed(max_speed)))
                if isinstance(mode, int):
                    cpol = (mode & 0b10) >> 1
                    cpha = (mode & 0b01)
                    print(present('Mode', f"{mode} (0b{mode:02b}) CPOL={cpol} CPHA={cpha}"))
                else:
                    print(present('Mode', mode))
                print(present('Bits/word', bits))
                print(present('3-wire', threewire))
                print(present('CS high', cs_high))
                print(present('No CS', no_cs))
                print(present('LSB first', lsbfirst))
                print()
                spi.close()
            except FileNotFoundError:
                pass

def use_adafruit_ws2801(num_leds):
    # spi = board.SPI()
    # cs = board.D5  # Chip select pin; adjust as needed
    # ws2801 = adafruit_ws2801.WS2801(spi, cs, num_leds)
    ws2801 = adafruit_ws2801.WS2801(board.D2, board.D0, num_leds, brightness=1.0)

    print(f"Setting {num_leds} WS2801 LEDs using Adafruit library.")

    try:
        while True:
            for color in [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255), (0, 0, 0)]:
                for i in range(num_leds):
                    ws2801[i] = color
                ws2801.show()
                print(f"Set color: {color}")
                time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting Adafruit WS2801 test.")
        for i in range(num_leds):
            ws2801[i] = (0, 0, 0)
        ws2801.show()

def use_spiddev_ws2801(num_leds, bus=0, device=0, speed_hz=1_000_000):
    spi = spidev.SpiDev()
    spi.open(bus, device)  # Adjust bus and device as needed
    spi.max_speed_hz = speed_hz  # 1 MHz
    print(f"Setting {num_leds} WS2801 LEDs using spidev.")

    def show(colors):
        data = bytearray()
        for r, g, b in colors:
            data.extend((r & 0xFF, g & 0xFF, b & 0xFF))
        spi.xfer2(list(data))
        time.sleep(0.002)  # Latch delay

    try:
        while True:
            for color in [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255), (0, 0, 0)]:
                colors = [color] * num_leds
                show(colors)
                print(f"Set color: {color}")
                time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting spidev WS2801 test.")
        colors = [(0, 0, 0)] * num_leds
        show(colors)
    finally:
        spi.close()

def main():
    parser = argparse.ArgumentParser(description="WS2801 SPI LED Test")
    parser.add_argument('--leds', type=int, default=1, help='Number of LEDs in the chain')
    parser.add_argument('--adafruit', action='store_true', help='Use Adafruit WS2801 library')
    parser.add_argument('--bus', type=int, default=0, help='SPI bus number (default: 0)')
    parser.add_argument('--device', type=int, default=0, help='SPI device number (default: 0)')
    parser.add_argument('--speed', type=int, default=1_000_000, help='SPI speed in Hz (default: 1000000)')
    args = parser.parse_args()

    print_spi_info()
    if args.adafruit:
        use_adafruit_ws2801(args.leds)
    else:
        use_spiddev_ws2801(args.leds, bus=args.bus, device=args.device, speed_hz=args.speed)

if __name__ == '__main__':
    main()
