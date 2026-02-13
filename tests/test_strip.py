from rpi5_ledlib.strip import LEDStrip
from rpi5_ledlib.encoder import WS2812Encoder


class MockSPIDriver:
    def __init__(self):
        self.last_data: bytes | None = None
        self.frames_sent = 0

    def transfer_frame(self, data: bytes) -> None:
        self.last_data = data
        self.frames_sent += 1


def test_fill_and_show():
    spi = MockSPIDriver()
    encoder = WS2812Encoder()

    strip = LEDStrip(10, spi, encoder)
    strip.fill(255, 0, 0)  # red
    strip.show()

    assert spi.frames_sent == 1
    assert spi.last_data is not None
    assert len(spi.last_data) == 10 * 3 * 3  # leds * (GRB bytes) * (SPI expansion x3)