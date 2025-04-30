from subclass import eeprom

class edc16u1(eeprom): 
    def __init__(self):
        super().__init__()
        self.size_min = 4096
        self.size_max = 4096

    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        return super().check(buffer)

    def encode(self, buffer: bytearray):
        if len(buffer) > 0x017F:
            buffer[0x0156] = 96
            buffer[0x0176] = 96
            buffer[0x015f] = 0xBE
            buffer[0x017f] = 0xBE
            print("Патч успешно применён к EDC16U1(U34) (0x0156 и 0x017f)")