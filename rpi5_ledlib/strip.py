from typing import Iterable, Tuple

from .spi_driver import SPIDriver
from .encoder import WS2812Encoder


class LEDStrip:
    """
    High-level LED strip controller.

    Responsibilities:
    - Store framebuffer (GRB format internally)
    - Provide pixel manipulation API
    - Encode and send frame via SPI
    """

    def __init__(
        self,
        num_leds: int,
        spi_driver: SPIDriver,
        encoder: WS2812Encoder,
    ):
        if num_leds <= 0:
            raise ValueError("num_leds must be positive")

        self._num_leds = num_leds
        self._spi = spi_driver
        self._encoder = encoder

        # GRB per LED (3 bytes)
        self._framebuffer = bytearray(num_leds * 3)

    @property
    def num_leds(self) -> int:
        return self._num_leds

    def set_pixel(self, index: int, r: int, g: int, b: int) -> None:
        if not (0 <= index < self._num_leds):
            raise IndexError("LED index out of range")

        if not all(0 <= v <= 255 for v in (r, g, b)):
            raise ValueError("Color values must be in range 0-255")

        base = index * 3

        # WS2812 expects GRB order
        self._framebuffer[base] = g
        self._framebuffer[base + 1] = r
        self._framebuffer[base + 2] = b

    def fill(self, r: int, g: int, b: int) -> None:
        if not all(0 <= v <= 255 for v in (r, g, b)):
            raise ValueError("Color values must be in range 0-255")

        # WS2812 uses GRB
        pixel = bytes((g, r, b))
        self._framebuffer[:] = pixel * self._num_leds

    def set_pixels(self, colors: Iterable[Tuple[int, int, int]]) -> None:
        for i, (r, g, b) in enumerate(colors):
            if i >= self._num_leds:
                break
            self.set_pixel(i, r, g, b)

    def clear(self) -> None:
        self._framebuffer[:] = b"\x00" * len(self._framebuffer)

    def show(self) -> None:
        """
        Encode framebuffer and transmit via SPI.
        """
        encoded = self._encoder.encode(self._framebuffer)
        self._spi.transfer_frame(encoded)