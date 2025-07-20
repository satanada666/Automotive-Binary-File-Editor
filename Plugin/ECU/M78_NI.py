from encoder import Encoder

class M78_NI(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 851968
        self.size_max = 2097152
        
        # Последовательность байт для точного поиска
        self.search_pattern = bytes([0xF8, 0xFF, 0x00, 0x3D, 0x0B])
        
        # Ожидаемые значения для проверки (4-й и 5-й байт)
        self.expected_value_4 = 0x3D
        self.expected_value_5 = 0x0B
        
        # Новые значения для отключения иммобилайзера (4-й и 5-й байт)
        self.new_value_4 = 0x0D
        self.new_value_5 = 0x08
    
    def find_pattern_addresses(self, buffer: bytearray) -> list:
        """Находит все адреса где встречается искомая последовательность байт"""
        pattern_addresses = []
        pattern_len = len(self.search_pattern)
        
        for i in range(len(buffer) - pattern_len + 1):
            if buffer[i:i + pattern_len] == self.search_pattern:
                # Адрес 4-го байта в найденной последовательности (позиция 3, индекс с 0)
                target_addr_4 = i + 3
                target_addr_5 = i + 4
                pattern_addresses.append((target_addr_4, target_addr_5))
                print(f"  Найдена последовательность по адресу 0x{i:06X}, 4-й байт по адресу 0x{target_addr_4:06X}, 5-й байт по адресу 0x{target_addr_5:06X}")
        
        return pattern_addresses
    
    def check_immobilizer_address(self, buffer: bytearray, addr_4, addr_5) -> bool:
        """Проверяет адреса на наличие ожидаемых значений"""
        if addr_4 >= len(buffer) or addr_5 >= len(buffer):
            return False
        if buffer[addr_4] != self.expected_value_4:
            return False
        if buffer[addr_5] != self.expected_value_5:
            return False
        return True
    
    def check(self, buffer: bytearray) -> bool:
        if len(buffer) < self.size_min or len(buffer) > self.size_max:
            return False
        
        # Ищем по последовательности байт
        pattern_addresses = self.find_pattern_addresses(buffer)
        if len(pattern_addresses) > 0:
            # Проверяем, что найденные адреса содержат правильные значения
            valid_pattern_addresses = 0
            for addr_4, addr_5 in pattern_addresses:
                if self.check_immobilizer_address(buffer, addr_4, addr_5):
                    valid_pattern_addresses += 1
            
            if valid_pattern_addresses > 0:
                return super().check(buffer)
        
        return False
    
    def encode(self, buffer: bytearray):
        # Проверяем размер буфера
        if len(buffer) < self.size_min or len(buffer) > self.size_max:
            print(f"Ошибка: неверный размер буфера {len(buffer)} байт (ожидается от {self.size_min} до {self.size_max})")
            return
        
        print("Поиск последовательности байт F8 FF 00 3D 0B...")
        
        # Ищем последовательность байт
        pattern_addresses = self.find_pattern_addresses(buffer)
        
        if len(pattern_addresses) == 0:
            print("Ошибка: последовательность байт не найдена!")
            print("Файл не подходит для данного патча.")
            return
        
        print(f"Найдено {len(pattern_addresses)} вхождений последовательности")
        print("Применение точного патча по найденным адресам...")
        
        patched_count = 0
        
        for addr_4, addr_5 in pattern_addresses:
            if self.check_immobilizer_address(buffer, addr_4, addr_5):
                # Меняем 4-й байт (3D -> 0D)
                old_value_4 = buffer[addr_4]
                buffer[addr_4] = self.new_value_4
                
                # Меняем 5-й байт (0B -> 08)
                old_value_5 = buffer[addr_5]
                buffer[addr_5] = self.new_value_5
                
                patched_count += 1
                print(f"  Адрес 0x{addr_4:06X}: 0x{old_value_4:02X} -> 0x{self.new_value_4:02X}")
                print(f"  Адрес 0x{addr_5:06X}: 0x{old_value_5:02X} -> 0x{self.new_value_5:02X}")
            else:
                current_value_4 = buffer[addr_4] if addr_4 < len(buffer) else 0xFF
                current_value_5 = buffer[addr_5] if addr_5 < len(buffer) else 0xFF
                print(f"  Адреса 0x{addr_4:06X}/0x{addr_5:06X}: пропущены")
                print(f"    (текущие значения 0x{current_value_4:02X}/0x{current_value_5:02X}, ожидается 0x{self.expected_value_4:02X}/0x{self.expected_value_5:02X})")
        
        if patched_count == 0:
            print("Ошибка: не найдено ни одного валидного адреса для патча!")
            return
        
        print(f"\nТочный патч успешно применён!")
        print(f"Всего изменено пар байтов: {patched_count}")
        print(f"Всего изменено байтов: {patched_count * 2}")
        print("Иммобилайзер отключен.")