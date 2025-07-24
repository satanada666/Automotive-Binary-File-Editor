from subclass import srs  # <-- Импортируешь базовый класс srs

class _0285001639_Bosch_98820_BU900_HC12B32(srs):
    def __init__(self):
        super().__init__()
        self.size_min = 768
        self.size_max = 768

    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        return super().check(buffer)

    def encode(self, buffer: bytearray):
        # Проверка размера буфера перед любыми операциями
        if len(buffer) < self.size_min:
            print(f"Ошибка: размер буфера ({len(buffer)}) меньше минимального ({self.size_min})")
            return

        # Установка адреса 
        buffer[0x07] = 0xF6
        buffer[0x09] = 0xE6
        buffer[0x0A] = 0xA3
        buffer[0x0B] = 0x3E
        buffer[0x0D] = 0xEA
        buffer[0x0E] = 0xE7
        buffer[0x41] = 0xFD
        buffer[0x23B] = 0x04
        buffer[0x23C] = 0x09
        buffer[0x23D] = 0x33
        buffer[0x243] = 0x15
        buffer[0x244] = 0x03
        buffer[0x247] = 0x16
        buffer[0x248] = 0x79
        buffer[0x2C0] = 0xFF
        buffer[0x2C1] = 0xFF
        print(f"[Изменение] Адрес 0x126 ({0x294} десятичный): установлен в 0x00")

        # Заполнение адресов с 0x30 по 0x3F значениями FF
        start_addr = 0x30
        end_addr = 0x40
        
        for addr in range(start_addr, end_addr + 1):  # включая 
            if buffer[addr] != 0xFF:
                print(f"[Изменение] Адрес 0x{addr:04X} ({addr} десятичный): было 0x{buffer[addr]:02X} → стало 0xFF")
            buffer[addr] = 0xFF
        
        print(f"[Информация] Установлен 0x00 по адресу 0x294")
        print(f"[Информация] Заполнено 0xFF с адреса 0x295 по 0x3C6 ({end_addr - start_addr + 1} байт)")

        # Заполнение адресов с 0x30 по 0x3F значениями FF
        start_addr = 0x42
        end_addr = 0xA0
        
        for addr in range(start_addr, end_addr + 1):  # включая 
            if buffer[addr] != 0xFF:
                print(f"[Изменение] Адрес 0x{addr:04X} ({addr} десятичный): было 0x{buffer[addr]:02X} → стало 0xFF")
            buffer[addr] = 0xFF
        
        print(f"[Информация] Установлен 0x00 по адресу 0x294")
        print(f"[Информация] Заполнено 0xFF с адреса 0x295 по 0x3C6 ({end_addr - start_addr + 1} байт)")
        
        # Вызов метода encode родительского класса
        super().encode(buffer)
        
        print("Патч успешно применён к Continental_Reault_8201_385_569")