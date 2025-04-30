from subclass import eeprom

class Vag_simos_2_1_No_Immo(eeprom): 
    def __init__(self):
        super().__init__()
        self.size_min = 256
        self.size_max = 256

    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        return super().check(buffer)

    def encode(self, buffer: bytearray):
        if len(buffer) > 0x000:
            buffer[0x06] = 0x31
            buffer[0x07] = 0x31
            buffer[0x08] = 0x31
            
            print("Патч успешно применён к Vag_simos_2.1 (0x06 и 0x08)")