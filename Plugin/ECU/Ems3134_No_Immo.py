from encoder import Encoder

class Ems3134_No_Immo(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 524288
        self.size_max = 524288

    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        return super().check(buffer)
    


    def encode(self, buffer: bytearray):
        if len(buffer) > 0x71381:
            buffer[0x71380] = 0x09

            print("Патч успешно применён к Ems3134_No_Immo (0x71380)")