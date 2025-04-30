from encoder import Encoder

class My2(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 3

    def encode(self, buffer: bytearray):
        if len(buffer) > 0:
            buffer[0] = 0xBB

    def check(self, buffer: bytearray) -> bool:
        return super().check(buffer)