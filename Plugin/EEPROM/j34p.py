from subclass import eeprom

class j34p(eeprom):
    def __init__(self):
        super().__init__()
        self.size_min = 2048
        self.size_max = 2048

    def check(self, buffer: bytearray) -> bool:
        return super().check(buffer)

    def encode(self, buffer: bytearray):
        patch = [
            0xFE, 0x6C, 0xFE, 0x6C, 0x11, 0x11, 0x11, 0x11,
            0x00, 0xFF, 0xE0, 0x06, 0xC5, 0xA0, 0x00, 0xFF,
            0x39, 0x60, 0x00, 0x00
        ]

        if len(buffer) < 0x080 + 20:
            print("Файл слишком короткий для применения патча")
            return

        buffer[0x0000:0x0000 + 20] = bytearray(patch)
        buffer[0x0070:0x0070 + 20] = bytearray(patch)

        print("Патч успешно применён к j34p (0x0000 и 0x0070)")