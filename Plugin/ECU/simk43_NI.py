from encoder import Encoder

class simk43_NI(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 524288
        self.size_max = 524288
        
        # Последовательность байт для точного поиска
        self.search_pattern = bytes([0x01, 0x02, 0x02, 0x00, 0x00])
        
        # Ожидаемое значение для проверки (последний байт последовательности)
        self.expected_value = 0x00
        
        # Новое значение для отключения иммобилайзера
        self.new_value = 0x01
    
    def fill_memory_range(self, buffer: bytearray, start_addr: int, end_addr: int, fill_value: int = 0xFF):
        """Заполняет указанный диапазон памяти указанным значением"""
        if start_addr >= len(buffer) or end_addr > len(buffer):
            print(f"Ошибка: адреса выходят за пределы буфера (0x{start_addr:05X}-0x{end_addr:05X})")
            return False
        
        if start_addr >= end_addr:
            print(f"Ошибка: начальный адрес больше конечного")
            return False
        
        for i in range(start_addr, end_addr):
            buffer[i] = fill_value
        
        print(f"Заполнен диапазон 0x{start_addr:05X}-0x{end_addr:05X} значением 0x{fill_value:02X}")
        return True
    
    def find_pattern_addresses(self, buffer: bytearray) -> list:
        """Находит все адреса где встречается искомая последовательность байт"""
        pattern_addresses = []
        pattern_len = len(self.search_pattern)
        
        for i in range(len(buffer) - pattern_len + 1):
            if buffer[i:i + pattern_len] == self.search_pattern:
                # Адрес последнего байта в найденной последовательности (позиция 4, индекс с 0)
                target_addr = i + 4
                pattern_addresses.append(target_addr)
                print(f"  Найдена последовательность по адресу 0x{i:05X}, последний байт 0x00 по адресу 0x{target_addr:05X}")
        
        return pattern_addresses
    
    def check_immobilizer_address(self, buffer: bytearray, addr) -> bool:
        """Проверяет один адрес на наличие ожидаемого значения"""
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
        
        print("=== Начало обработки файла ===")
        
        # Заполняем область 0x4000-0x8000 байтами 0xFF
        print("Заполнение области памяти 0x4000-0x8000 байтами 0xFF...")
        if not self.fill_memory_range(buffer, 0x4000, 0x8000, 0xFF):
            print("Ошибка при заполнении области памяти!")
            return
        
        print("\nПоиск последовательности байт 0x01, 0x02, 0x02, 0x00, 0x00...")
        
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
                print(f"  Адрес 0x{addr:05X}: 0x{old_value:02X} -> 0x{new_value:02X}")
            else:
                current_value = buffer[addr] if addr < len(buffer) else 0xFF
                print(f"  Адрес 0x{addr:05X}: пропущен (текущее значение 0x{current_value:02X}, ожидается 0x{self.expected_value:02X})")
        
        if patched_count == 0:
            print("Ошибка: не найдено ни одного валидного адреса для патча!")
            return
        
        print(f"\n=== Результат обработки ===")
        print(f"Область памяти 0x4000-0x8000 заполнена байтами 0xFF")
        print(f"Точный патч успешно применён!")
        print(f"Всего изменено байт: {patched_count}")
        print("Иммобилайзер отключен.")