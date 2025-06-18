from subclass import srs  # <-- Импортируешь базовый класс srs

class Continental_Reault_8201_385_569(srs):
    def __init__(self):
        super().__init__()
        self.size_min = 2048
        self.size_max = 2048

    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        return super().check(buffer)

    def encode(self, buffer: bytearray):
        # Проверка размера буфера перед любыми операциями
        if len(buffer) < self.size_min:
            print(f"Ошибка: размер буфера ({len(buffer)}) меньше минимального ({self.size_min})")
            return

        # Установка адреса 0x126 в 00
        buffer[0x294] = 0x00
        print(f"[Изменение] Адрес 0x126 ({0x126} десятичный): установлен в 0x00")

        # Заполнение адресов с 0x127 по 0x3C6 значениями FF
        start_addr = 0x295
        end_addr = 0x3C6
        
        for addr in range(start_addr, end_addr + 1):  # включая 0x3C6
            if buffer[addr] != 0xFF:
                print(f"[Изменение] Адрес 0x{addr:04X} ({addr} десятичный): было 0x{buffer[addr]:02X} → стало 0xFF")
            buffer[addr] = 0xFF
        
        print(f"[Информация] Установлен 0x00 по адресу 0x294")
        print(f"[Информация] Заполнено 0xFF с адреса 0x295 по 0x3C6 ({end_addr - start_addr + 1} байт)")


        
        # Вызов метода encode родительского класса
        super().encode(buffer)
        
        print("Патч успешно применён к Continental_Reault_8201_385_569")