from encoder import Encoder

class dash_vdo(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 512

    def encode(self, buffer: bytearray):
        if len(buffer) >= 4:
            buffer[0:4] = b"DASH"
            print("Редактор DASH: записано 'DASH' в начало файла")