from encoder import Encoder

class sim2k_240_241_242_245(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 2097152
        self.size_max = 2097152
        
        # Последовательность байт для точного поиска
        self.search_pattern = bytes([0x49, 0xFF, 0x10, 0x0A, 0xDA, 0x01, 0x34, 0xFF, 0xD9, 0x0C])
        
        # Ожидаемое значение для проверки
        self.expected_value = 0x01
        
        # Новое значение для отключения иммобилайзера
        self.new_value = 0x00
    
    def find_pattern_addresses(self, buffer: bytearray) -> list:
        """Находит все адреса где встречается искомая последовательность байт"""
        pattern_addresses = []
        pattern_len = len(self.search_pattern)
        
        for i in range(len(buffer) - pattern_len + 1):
            if buffer[i:i + pattern_len] == self.search_pattern:
                # Адрес байта 0x01 в найденной последовательности (позиция 5)
                target_addr = i + 5
                pattern_addresses.append(target_addr)
                print(f"  Найдена последовательность по адресу 0x{i:06X}, байт 0x01 по адресу 0x{target_addr:06X}")
        
        return pattern_addresses
    
    def check_immobilizer_address(self, buffer: bytearray, addr) -> bool:
        """Проверяет один адрес на наличие значения 01"""
        if addr >= len(buffer):
            return False
        if buffer[addr] != self.expected_value:
            return False
        return True
    
    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        
        # Ищем по последовательности байт
        pattern_addresses = self.find_pattern_addresses(buffer)
        if len(pattern_addresses) > 0:
            # Проверяем, что найденные адреса содержат правильное значение
            valid_pattern_addresses = 0
            for addr in pattern_addresses:
                if self.check_immobilizer_address(buffer, addr):
                    valid_pattern_addresses += 1
            
            if valid_pattern_addresses > 0:
                return super().check(buffer)
        
        return False
    
    def encode(self, buffer: bytearray):
        # Проверяем размер буфера
        if len(buffer) != self.size_min:
            print(f"Ошибка: неверный размер буфера {len(buffer)} байт (ожидается {self.size_min})")
            return
        
        print("Поиск последовательности байт 49 FF 10 0A DA 01 34 FF D9 0C...")
        
        # Ищем последовательность байт
        pattern_addresses = self.find_pattern_addresses(buffer)
        
        if len(pattern_addresses) == 0:
            print("Ошибка: последовательность байт не найдена!")
            print("Файл не подходит для данного патча.")
            return
        
        print(f"Найдено {len(pattern_addresses)} вхождений последовательности")
        print("Применение точного патча по найденным адресам...")
        
        patched_count = 0
        
        for addr in pattern_addresses:
            if self.check_immobilizer_address(buffer, addr):
                old_value = buffer[addr]
                new_value = self.new_value
                buffer[addr] = new_value
                patched_count += 1
                print(f"  Адрес 0x{addr:06X}: 0x{old_value:02X} -> 0x{new_value:02X}")
            else:
                current_value = buffer[addr] if addr < len(buffer) else 0xFF
                print(f"  Адрес 0x{addr:06X}: пропущен (текущее значение 0x{current_value:02X}, ожидается 0x{self.expected_value:02X})")
        
        if patched_count == 0:
            print("Ошибка: не найдено ни одного валидного адреса для патча!")
            return
        
        print(f"\nТочный патч успешно применён!")
        print(f"Всего изменено байт: {patched_count}")
        print("Иммобилайзер отключен.")