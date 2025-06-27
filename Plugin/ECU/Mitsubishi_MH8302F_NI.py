from encoder import Encoder

class Mitsubishi_MH8302F_NI(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 524288
        self.size_max = 524288

    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        return super().check(buffer)
    
    def encode(self, buffer: bytearray):
        # Проверяем размер буфера
        if len(buffer) < 0x3ffc4:
            print("Ошибка: недостаточный размер буфера")
            return
        
        # Записываем значение D6 по адресу 0x27B
        buffer[0x27B] = 0xD6
        
        # Записываем значение D6 по адресу 0x27D
        buffer[0x27D] = 0xD6
        
        # Расчитываем и записываем контрольную сумму
        # Получаем текущие значения по адресам 0x3ffc1 и 0x3ffc3
        checksum_addr1 = 0x3ffc1
        checksum_addr2 = 0x3ffc3
        
        # Читаем текущие значения
        current_value1 = buffer[checksum_addr1]
        current_value2 = buffer[checksum_addr2]
        
        # Добавляем 8 к каждому значению
        new_value1 = (current_value1 + 8) & 0xFF  # Ограничиваем байтом
        new_value2 = (current_value2 + 8) & 0xFF  # Ограничиваем байтом
        
        # Записываем новые значения
        buffer[checksum_addr1] = new_value1
        buffer[checksum_addr2] = new_value2
        
        print(f"Патч успешно применён к Mitsubishi_MH8302F_NI:")
        print(f"  0x27B = 0xD6")
        print(f"  0x27D = 0xD6")
        print(f"  0x3ffc1: 0x{current_value1:02X} -> 0x{new_value1:02X}")
        print(f"  0x3ffc3: 0x{current_value2:02X} -> 0x{new_value2:02X}")