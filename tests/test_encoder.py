from rpi5_ledlib.encoder import WS2812Encoder


def test_encoder_output_length():
    enc = WS2812Encoder()
    raw = bytes([0x00, 0xFF, 0x12])
    out = enc.encode(raw)
    assert len(out) == len(raw) * 3


def test_encoder_known_bytes_single():
    enc = WS2812Encoder()

    # Для схемы 0->100, 1->110 (MSB first):
    # 0x00 -> 924924
    # 0xFF -> db6db6
    assert enc.encode(bytes([0x00])) == bytes.fromhex("924924")
    assert enc.encode(bytes([0xFF])) == bytes.fromhex("db6db6")


def test_encoder_known_bytes_concat():
    enc = WS2812Encoder()

    # 0xA5 -> d349a6, 0x5A -> 9a6d34
    raw = bytes([0xA5, 0x5A])
    out = enc.encode(raw)

    assert out == bytes.fromhex("d349a69a6d34")