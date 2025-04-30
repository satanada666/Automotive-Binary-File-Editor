from encoder import Encoder

class bcm_valeo(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 512

    def encode(self, buffer: bytearray):
        if len(buffer) >= 4:
            buffer[0:4] = b"BCM!"
            print("Редактор BCM: записано 'BCM!' в начало файла")