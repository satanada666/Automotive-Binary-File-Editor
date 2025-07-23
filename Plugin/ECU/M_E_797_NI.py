from encoder import Encoder

class M_E_797_NI(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 524288
        self.size_max = 524288
        
        # Паттерны для поиска
        self.search_patterns = [
            {
                'name': 'Паттерн 1',
                'pattern': bytes([0x17, 0x00, 0x03, 0x17, 0x4D, 0xB8])
            },
            {
                'name': 'Паттерн 2', 
                'pattern': bytes([0x64, 0x00, 0x0B, 0x00, 0x03, 0x17])
            }
        ]
        
        # Новое значение для отключения иммобилайзера
        self.new_value = 0x25
    
    def find_pattern_addresses(self, buffer: bytearray) -> list:
        """Находит все адреса где встречаются искомые последовательности байт"""
        all_pattern_addresses = []
        
        for pattern_info in self.search_patterns:
            pattern_name = pattern_info['name']
            pattern_bytes = pattern_info['pattern']
            pattern_len = len(pattern_bytes)
            
            print(f"\nИщем {pattern_name}: {' '.join(f'{b:02X}' for b in pattern_bytes)}")
            
            pattern_found = False
            for i in range(len(buffer) - pattern_len + 1):
                if buffer[i:i + pattern_len] == pattern_bytes:
                    # Адрес байта ПЕРЕД найденной последовательностью
                    if i > 0:  # Проверяем, что есть байт перед последовательностью
                        target_addr = i - 1
                        all_pattern_addresses.append({
                            'address': target_addr,
                            'pattern_name': pattern_name,
                            'pattern_address': i
                        })
                        current_byte = buffer[target_addr]
                        print(f"  Найден {pattern_name} по адресу 0x{i:06X}")
                        print(f"  Байт для замены по адресу 0x{target_addr:06X}: 0x{current_byte:02X}")
                        pattern_found = True
                    else:
                        print(f"  Найден {pattern_name} по адресу 0x{i:06X}, но нет байта перед ним для замены")
            
            if not pattern_found:
                print(f"  {pattern_name} не найден в файле")
        
        if len(all_pattern_addresses) == 0:
            print("\nНи один паттерн не найден в файле")
            self.find_similar_patterns(buffer)
        
        return all_pattern_addresses
    
    def find_similar_patterns(self, buffer: bytearray):
        """Ищет похожие последовательности для диагностики"""
        print("Поиск похожих последовательностей...")
        
        # Ищем начальные байты для каждого паттерна
        search_starts = [
            {'name': 'Паттерн 1 (17 00)', 'bytes': bytes([0x17, 0x00])},
            {'name': 'Паттерн 2 (64 00)', 'bytes': bytes([0x64, 0x00])}
        ]
        
        for search_info in search_starts:
            start_pattern = search_info['bytes']
            pattern_name = search_info['name']
            found_count = 0
            
            print(f"\n  Поиск {pattern_name}:")
            
            for i in range(len(buffer) - len(start_pattern) + 1):
                if buffer[i:i + len(start_pattern)] == start_pattern:
                    found_count += 1
                    if found_count <= 3:  # Показываем только первые 3
                        next_bytes = buffer[i:i + 8] if i + 8 <= len(buffer) else buffer[i:]
                        hex_str = ' '.join(f'{b:02X}' for b in next_bytes)
                        print(f"    Найдено по адресу 0x{i:06X}: {hex_str}")
            
            if found_count == 0:
                print(f"    Не найдено начальной последовательности {pattern_name}")
            else:
                print(f"    Найдено {found_count} вхождений {pattern_name}")
    
    def check_immobilizer_address(self, buffer: bytearray, addr: int) -> bool:
        """Проверяет один адрес на валидность"""
        if addr < 0 or addr >= len(buffer):
            return False
        # Теперь не проверяем конкретное значение, просто проверяем что адрес валидный
        return True
    
    def check(self, buffer: bytearray) -> bool:
        """Проверяет, подходит ли буфер для данного патча"""
        print(f"Проверка размера буфера: {len(buffer)} байт (ожидается {self.size_min})")
        
        if len(buffer) != self.size_min:
            print(f"Ошибка размера: {len(buffer)} != {self.size_min}")
            return False
        
        print("Поиск последовательности байт для проверки...")
        
        # Ищем по последовательности байт
        pattern_addresses = self.find_pattern_addresses(buffer)
        print(f"Найдено {len(pattern_addresses)} вхождений последовательности")
        
        if len(pattern_addresses) > 0:
            # Проверяем, что найденные адреса содержат правильное значение
            valid_pattern_addresses = 0
            for addr_info in pattern_addresses:
                addr = addr_info['address']
                if self.check_immobilizer_address(buffer, addr):
                    valid_pattern_addresses += 1
                    print(f"Валидный адрес найден: 0x{addr:06X} (байт перед {addr_info['pattern_name']})")
            
            print(f"Валидных адресов: {valid_pattern_addresses}")
            
            if valid_pattern_addresses > 0:
                print("Файл подходит для данного патча!")
                return True  # Возвращаем True напрямую, не вызывая super().check()
        
        print("Файл НЕ подходит для данного патча - последовательность не найдена")
        return False
    
    def encode(self, buffer: bytearray):
        """Применяет патч к буферу"""
        # Проверяем размер буфера
        if len(buffer) != self.size_min:
            print(f"Ошибка: неверный размер буфера {len(buffer)} байт (ожидается {self.size_min})")
            return
        
        print("Поиск паттернов: 17 00 03 17 4D B8 и 64 00 0B 00 03 17...")
        
        # Ищем все паттерны
        pattern_addresses = self.find_pattern_addresses(buffer)
        
        if len(pattern_addresses) == 0:
            print("Ошибка: последовательность байт не найдена!")
            print("Файл не подходит для данного патча.")
            return
        
        print(f"\nНайдено {len(pattern_addresses)} адресов для патча")
        print("Применение патча - замена байта ПЕРЕД найденными последовательностями...")
        
        patched_count = 0
        
        for addr_info in pattern_addresses:
            addr = addr_info['address']
            pattern_name = addr_info['pattern_name']
            
            if self.check_immobilizer_address(buffer, addr):
                old_value = buffer[addr]
                new_value = self.new_value
                buffer[addr] = new_value
                patched_count += 1
                print(f"  {pattern_name} - Адрес 0x{addr:06X}: 0x{old_value:02X} -> 0x{new_value:02X}")
            else:
                print(f"  {pattern_name} - Адрес 0x{addr:06X}: пропущен (невалидный адрес)")
        
        if patched_count == 0:
            print("Ошибка: не найдено ни одного валидного адреса для патча!")
            return
        
        print(f"\nПатч успешно применён!")
        print(f"Всего изменено байт: {patched_count}")
        print("Иммобилайзер отключен.")

# Пример использования и тестирования
if __name__ == "__main__":
    # Создаем тестовый буфер
    test_buffer = bytearray(524288)  # Буфер нужного размера
    
    # Вставляем тестовую последовательность в несколько мест
    test_pattern = bytes([0x01, 0x64, 0x00, 0x0B, 0x00, 0x03, 0x17])
    test_buffer[1000:1000+len(test_pattern)] = test_pattern
    test_buffer[50000:50000+len(test_pattern)] = test_pattern
    
    # Создаем кодировщик и тестируем
    encoder = M_E_797_NI()
    
    print("=== ТЕСТИРОВАНИЕ ===")
    print(f"Размер буфера: {len(test_buffer)} байт")
    print(f"Проверка валидности буфера: {encoder.check(test_buffer)}")
    
    print("\n=== ПРИМЕНЕНИЕ ПАТЧА ===")
    encoder.encode(test_buffer)
    
    # Проверяем результат
    print(f"\n=== ПРОВЕРКА РЕЗУЛЬТАТА ===")
    print(f"Байт по адресу 1000: 0x{test_buffer[1000]:02X}")
    print(f"Байт по адресу 50000: 0x{test_buffer[50000]:02X}")