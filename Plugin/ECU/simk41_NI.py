from encoder import Encoder

class simk41_NI(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 262144
        self.size_max = 262144
        
        # Два варианта поиска - программа выберет сама какой использовать
        self.patterns = [
            {
                'name': 'Паттерн 1',
                'search_pattern': bytes([0x01, 0x02, 0x02, 0x00, 0x00]),
                'expected_value': 0x00,
                'new_value': 0x01
            },
            {
                'name': 'Паттерн 2', 
                'search_pattern': bytes([0x00, 0x02, 0x01, 0x00, 0x00, 0x00]),
                'expected_value': 0x00,
                'new_value': 0x10
            }
        ]
        
        # Активный паттерн (будет выбран автоматически)
        self.active_pattern = None

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
    
    def find_pattern_addresses(self, buffer: bytearray, pattern_info) -> list:
        """Находит все адреса где встречается искомая последовательность байт"""
        pattern_addresses = []
        search_pattern = pattern_info['search_pattern']
        pattern_len = len(search_pattern)
        
        for i in range(len(buffer) - pattern_len + 1):
            if buffer[i:i + pattern_len] == search_pattern:
                # Адрес последнего байта в найденной последовательности 
                # Для 5-байтового паттерна: позиция 4 (индекс 4)
                # Для 6-байтового паттерна: позиция 5 (индекс 5)
                target_addr = i + (pattern_len - 1)
                pattern_addresses.append(target_addr)
                print(f"  Найдена последовательность по адресу 0x{i:05X}, изменяемый байт по адресу 0x{target_addr:05X}")
        
        return pattern_addresses
    
    def check_immobilizer_address(self, buffer: bytearray, addr, expected_value) -> bool:
        """Проверяет один адрес на наличие ожидаемого значения"""
        if addr >= len(buffer):
            return False
        if buffer[addr] != expected_value:
            return False
        return True
    
    def select_active_pattern(self, buffer: bytearray) -> bool:
        """Выбирает активный паттерн на основе того, что найдется в файле"""
        print("Автоматический выбор подходящего паттерна...")
        
        for i, pattern_info in enumerate(self.patterns):
            print(f"\nПроверка {pattern_info['name']}:")
            pattern_addresses = self.find_pattern_addresses(buffer, pattern_info)
            
            if len(pattern_addresses) > 0:
                # Проверяем, что найденные адреса содержат правильное значение
                valid_addresses = 0
                for addr in pattern_addresses:
                    if self.check_immobilizer_address(buffer, addr, pattern_info['expected_value']):
                        valid_addresses += 1
                
                if valid_addresses > 0:
                    self.active_pattern = pattern_info
                    print(f"✓ Выбран {pattern_info['name']} (найдено {valid_addresses} валидных адресов)")
                    return True
                else:
                    print(f"✗ {pattern_info['name']} не подходит (нет валидных адресов)")
            else:
                print(f"✗ {pattern_info['name']} не найден")
        
        print("Ошибка: ни один паттерн не найден!")
        return False
    
    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        
        # Выбираем подходящий паттерн
        if self.select_active_pattern(buffer):
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
        
        # Выбираем активный паттерн
        if not self.select_active_pattern(buffer):
            print("Файл не подходит для данного патча.")
            return
        
        print(f"\nПрименение патча с использованием {self.active_pattern['name']}...")
        
        # Ищем последовательность байт активного паттерна
        pattern_addresses = self.find_pattern_addresses(buffer, self.active_pattern)
        
        print(f"Найдено {len(pattern_addresses)} вхождений последовательности")
        print("Применение точного патча по найденным адресам...")
        
        patched_count = 0
        
        for addr in pattern_addresses:
            if self.check_immobilizer_address(buffer, addr, self.active_pattern['expected_value']):
                old_value = buffer[addr]
                new_value = self.active_pattern['new_value']
                buffer[addr] = new_value
                patched_count += 1
                print(f"  Адрес 0x{addr:05X}: 0x{old_value:02X} -> 0x{new_value:02X}")
            else:
                current_value = buffer[addr] if addr < len(buffer) else 0xFF
                print(f"  Адрес 0x{addr:05X}: пропущен (текущее значение 0x{current_value:02X}, ожидается 0x{self.active_pattern['expected_value']:02X})")
        
        if patched_count == 0:
            print("Ошибка: не найдено ни одного валидного адреса для патча!")
            return
        
        print(f"\n=== Результат обработки ===")
        print(f"Использован: {self.active_pattern['name']}")
        print(f"Область памяти 0x4000-0x8000 заполнена байтами 0xFF")
        print(f"Точный патч успешно применён!")
        print(f"Всего изменено байт: {patched_count}")
        print("Иммобилайзер отключен.")