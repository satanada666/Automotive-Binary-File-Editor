from subclass import eeprom

class Vag_simos_3_3_No_Immo(eeprom): 
    def __init__(self):
        super().__init__()
        self.size_min = 1024
        self.size_max = 1024

    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        return super().check(buffer)

    def encode(self, buffer: bytearray):
        if len(buffer) > 0x000:
            buffer[0x06] = 0x31
            buffer[0x07] = 0x00
            buffer[0x08] = 0x31
            buffer[0x0a] = 0x31
            
            print("Патч успешно применён к Vag_simos_3.3 (0x06 и 0x0a)")