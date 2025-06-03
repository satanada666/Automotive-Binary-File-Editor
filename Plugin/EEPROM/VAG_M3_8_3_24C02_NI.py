from subclass import eeprom

class VAG_M3_8_3_24C02_NI(eeprom): 
    def __init__(self):
        super().__init__()
        self.size_min = 256
        self.size_max = 256

    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        return super().check(buffer)

    def encode(self, buffer: bytearray):
        if len(buffer) > 0x6F:
            buffer[0xC] = 80
            buffer[0xE] = 67
            buffer[0xF] = 0xFA
            buffer[0x6C] = 80
            buffer[0x6E] = 67
            buffer[0x6F] = 0xFA
            print("Патч успешно применён к VAG_M3.8.3_24C02_NI (0xC и 0x6F)")