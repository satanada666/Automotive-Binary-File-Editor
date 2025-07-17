from encoder import Encoder

class delphi_MT_38_NI(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 2031616
        self.size_max = 2097152
        
        # Последовательность байт для точного поиска
        self.search_pattern = bytes([0x06, 0x00, 0x03, 0x00, 0x55])
        
        # Ожидаемое значение для проверки (последний байт в pattern)
        self.expected_value = 0x55
        
        # Новое значение для отключения иммобилайзера
        self.new_value = 0xAA
    
    def find_pattern_addresses(self, buffer: bytearray) -> list:
        """Находит все адреса где встречается искомая последовательность байт"""
        pattern_addresses = []
        pattern_len = len(self.search_pattern)
        
        for i in range(len(buffer) - pattern_len + 1):
            if buffer[i:i + pattern_len] == self.search_pattern:
                # Адрес байта 0x55 в найденной последовательности (позиция 4, индекс с 0)
                target_addr = i + 4  # Исправлено: было i + 5
                pattern_addresses.append(target_addr)
                print(f"  Найдена последовательность по адресу 0x{i:06X}, байт 0x55 по адресу 0x{target_addr:06X}")
        
        return pattern_addresses
    
    def check_immobilizer_address(self, buffer: bytearray, addr) -> bool:
        """Проверяет один адрес на наличие значения 0x55"""
        if addr >= len(buffer):
            return False
        if buffer[addr] != self.expected_value:
            return False
        return True
    
    def check(self, buffer: bytearray) -> bool:
        if not (self.size_min <= len(buffer) <= self.size_max):
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
        if not (self.size_min <= len(buffer) <= self.size_max):
            print(f"Ошибка: неверный размер буфера {len(buffer)} байт (ожидается от {self.size_min} до {self.size_max})")
            return
        
        print("Поиск последовательности байт 06 00 03 00 55...")
        
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