class MockSPIDriver:
    def __init__(self):
        self.last_data = None
        self.frames_sent = 0

    def transfer_frame(self, data: bytes):
        self.last_data = data
        self.frames_sent += 1