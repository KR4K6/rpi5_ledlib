from typing import ByteString


class WS2812Encoder:
    """
    Encodes RGB byte stream into SPI-compatible waveform
    using 3-bit expansion per WS2812 bit.

    0 -> 100
    1 -> 110
    """

    _BIT_PATTERNS = {
        0: 0b100,
        1: 0b110,
    }

    def __init__(self):
        self._lut = self._build_lut()

    @classmethod
    def _build_lut(cls) -> list[bytes]:
        """
        Precompute 256-byte lookup table.
        Each input byte becomes 24 bits (3 bytes) of SPI data.
        """
        lut = []

        for byte in range(256):
            encoded = 0
            total_bits = 0

            for bit_pos in range(7, -1, -1):
                bit = (byte >> bit_pos) & 1
                pattern = cls._BIT_PATTERNS[bit]

                encoded = (encoded << 3) | pattern
                total_bits += 3

            # Convert 24-bit integer into 3 bytes
            lut.append(encoded.to_bytes(3, byteorder="big"))

        return lut

    def encode(self, data: ByteString) -> bytes:
        """
        Expand raw GRB bytes into SPI waveform bytes.
        """
        output = bytearray(len(data) * 3)

        idx = 0
        for byte in data:
            encoded = self._lut[byte]
            output[idx:idx + 3] = encoded
            idx += 3

        return bytes(output)