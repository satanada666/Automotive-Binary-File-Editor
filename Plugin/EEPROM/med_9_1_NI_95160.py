from subclass import eeprom

class med_9_1_NI_95160(eeprom): 
    def __init__(self):
        super().__init__()
        self.size_min = 2048
        self.size_max = 2048

    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        return super().check(buffer)

    def encode(self, buffer: bytearray):
        if len(buffer) > 0x7F:
            # Увеличиваем байт по адресам 0x59 и 0x79
            buffer[0x59] = (buffer[0x59] + 1) % 0x100
            buffer[0x79] = (buffer[0x79] + 1) % 0x100
            
            # Уменьшаем байт по адресам 0x5F и 0x7F
            buffer[0x5F] = (buffer[0x5F] - 1) % 0x100
            buffer[0x7F] = (buffer[0x7F] - 1) % 0x100

            print("Патч успешно применён к med_9_1_NI_95160 (0x59/0x79 +1, 0x5F/0x7F -1)")
