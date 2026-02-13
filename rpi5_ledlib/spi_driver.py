import time
from typing import Optional, Any


class SPIDriver:
    """
    Low-level SPI driver for deterministic byte transfer.
    Does not contain any LED-specific logic.

    Important: spidev is imported lazily inside open() so unit tests can run
    on non-Raspberry machines without spidev installed.
    """

    def __init__(
        self,
        bus: int = 0,
        device: int = 0,
        max_speed_hz: int = 2_400_000,
        mode: int = 0,
        reset_delay_us: int = 80,
    ):
        self._bus = bus
        self._device = device
        self._max_speed_hz = max_speed_hz
        self._mode = mode
        self._reset_delay_us = reset_delay_us

        self._spi: Optional[Any] = None  # set in open()

    def open(self) -> None:
        if self._spi is not None:
            return

        try:
            import spidev  # type: ignore
        except ImportError as e:
            raise ImportError(
                "spidev is required only on Raspberry Pi for real hardware access. "
                "It is not needed for unit tests on your PC."
            ) from e

        spi = spidev.SpiDev()
        spi.open(self._bus, self._device)
        spi.max_speed_hz = self._max_speed_hz
        spi.mode = self._mode
        spi.bits_per_word = 8

        self._spi = spi

    def close(self) -> None:
        if self._spi is not None:
            self._spi.close()
            self._spi = None

    def write(self, data: bytes) -> None:
        if self._spi is None:
            raise RuntimeError("SPI device not opened (call open() first)")
        # xfer2 keeps CS active during transfer; accepts list[int] or bytes depending on backend
        self._spi.xfer2(data)

    def reset_latch(self) -> None:
        """
        WS2812 requires >50us low time to latch the frame.
        With SPI we emulate this by a short delay.
        """
        time.sleep(self._reset_delay_us / 1_000_000)

    def transfer_frame(self, data: bytes) -> None:
        self.write(data)
        self.reset_latch()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()