from subclass import srs  # <-- Импортируешь базовый класс srs

class mazda_95320_GR6B_57K30B(srs):
    def __init__(self):
        super().__init__()
        self.size_min = 4096
        self.size_max = 4096

    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        return super().check(buffer)

    def encode(self, buffer: bytearray):
        # Проверка размера буфера перед любыми операциями
        if len(buffer) < self.size_min:
            print(f"Ошибка: размер буфера ({len(buffer)}) меньше минимального ({self.size_min})")
            return

        # Первая группа адресов
        if len(buffer) > 0x0850:
            addresses_to_zero = [
                0x0850, 0x0852, 0x0854, 0x0855, 0x0856, 0x0857, 0x0858, 0x0859, 
                0x085A, 0x085B, 0x08A0, 0x08A1, 0x08A5, 0x08E0, 0x08E1, 0x08E3, 
                0x08E4, 0x08E5, 0x08E6, 0x08ED, 0x091F
            ]
            for addr in addresses_to_zero:
                buffer[addr] = 0x00
            
            # Установка значений 0x55 и 0xFF
            buffer[0x092F] = 0x55
            
            # Диапазон от 0x0930 до 0x094C устанавливаем в 0xFF
            for addr in range(0x0930, 0x094D):
                buffer[addr] = 0xFF
        
        # Дополнительная очистка: от 0x0920 до 0x0AEE должны быть FF
        if len(buffer) > 0x0AEE:
            modified = False
            for addr in range(0x0920, 0x0AEF):
                if buffer[addr] != 0xFF:
                    print(f"[Изменение] Адрес 0x{addr:04X}: было 0x{buffer[addr]:02X} → стало 0xFF")
                    buffer[addr] = 0xFF
                    modified = True
                    
            if not modified:
                print("Никаких изменений не потребовалось в диапазоне 0x0920-0x0AEE")
        
        # Вызов метода encode родительского класса
        super().encode(buffer)
        
        print("Патч успешно применён к mazda_95320_GR6B_57K30B")