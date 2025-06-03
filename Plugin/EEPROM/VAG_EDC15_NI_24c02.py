from subclass import eeprom

class VAG_EDC15_NI_24c02(eeprom): 
    def __init__(self):
        super().__init__()
        self.size_min = 256
        self.size_max = 256

    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        return super().check(buffer)

    def encode(self, buffer: bytearray):
        if len(buffer) > 0x8B:
            buffer[0x65] = 96
            buffer[0x8B] = 96
            print("Патч успешно применён к EDC15_NI (0x65 и 0x8B)")