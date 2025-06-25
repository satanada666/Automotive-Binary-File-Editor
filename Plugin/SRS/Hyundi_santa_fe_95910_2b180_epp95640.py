from subclass import srs  # <-- Импортируешь базовый класс srs

class Hyundi_santa_fe_95910_2b180_epp95640(srs):
    def __init__(self):
        super().__init__()
        self.size_min = 8192
        self.size_max = 8192
    
    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        return super().check(buffer)
    
    def encode(self, buffer: bytearray):
        # Проверка размера буфера перед любыми операциями
        if len(buffer) < self.size_min:
            print(f"Ошибка: размер буфера ({len(buffer)}) меньше минимального ({self.size_min})")
            return
        
        # Заполнение адресов с 0x7D4 по 0x967 значением FF
        start_addr = 0x7D4
        end_addr = 0x967
        
        for addr in range(start_addr, end_addr + 1):
            if buffer[addr] != 0xFF:
                print(f"[Изменение] Адрес 0x{addr:04X} ({addr} десятичный): было 0x{buffer[addr]:02X} → стало 0xFF")
            buffer[addr] = 0xFF
        
        print(f"[Информация] Заполнено 0xFF с адреса 0x{start_addr:04X} по 0x{end_addr:04X} ({end_addr - start_addr + 1} байт)")
        
        # Установка адреса 0xA41 в 01
        if buffer[0xA41] != 0x01:
            print(f"[Изменение] Адрес 0xA41 ({0xA41} десятичный): было 0x{buffer[0xA41]:02X} → стало 0x01")
        buffer[0xA41] = 0x01
        print(f"[Информация] Установлен 0x01 по адресу 0xA41")
        
        # Заполнение адресов с 0xA45 по 0xA4C значением 00
        start_addr = 0xA45
        end_addr = 0xA4C
        
        for addr in range(start_addr, end_addr + 1):
            if buffer[addr] != 0x00:
                print(f"[Изменение] Адрес 0x{addr:04X} ({addr} десятичный): было 0x{buffer[addr]:02X} → стало 0x00")
            buffer[addr] = 0x00
        
        print(f"[Информация] Заполнено 0x00 с адреса 0x{start_addr:04X} по 0x{end_addr:04X} ({end_addr - start_addr + 1} байт)")
        
        # Заполнение адресов с 0xA4E по 0xA67 значением 00
        start_addr = 0xA4E
        end_addr = 0xA67
        
        for addr in range(start_addr, end_addr + 1):
            if buffer[addr] != 0x00:
                print(f"[Изменение] Адрес 0x{addr:04X} ({addr} десятичный): было 0x{buffer[addr]:02X} → стало 0x00")
            buffer[addr] = 0x00
        
        print(f"[Информация] Заполнено 0x00 с адреса 0x{start_addr:04X} по 0x{end_addr:04X} ({end_addr - start_addr + 1} байт)")
        
        # Заполнение адресов с 0xA68 по 0x1170 значением FF
        start_addr = 0xA68
        end_addr = 0x1170
        
        for addr in range(start_addr, end_addr + 1):
            if buffer[addr] != 0xFF:
                print(f"[Изменение] Адрес 0x{addr:04X} ({addr} десятичный): было 0x{buffer[addr]:02X} → стало 0xFF")
            buffer[addr] = 0xFF
        
        print(f"[Информация] Заполнено 0xFF с адреса 0x{start_addr:04X} по 0x{end_addr:04X} ({end_addr - start_addr + 1} байт)")
        
        # Вызов метода encode родительского класса
        super().encode(buffer)
        
        print("Патч успешно применён к Hyundi_santa_fe_95910_2b180_epp95640")