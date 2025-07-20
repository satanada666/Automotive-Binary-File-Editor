from encoder import Encoder

class Me_17_kia_Hyundai(Encoder):
    def __init__(self):
        super().__init__()
        self.allowed_sizes = [1540096, 1572864, 2097152]
        
        # Определяем все паттерны поиска
        self.patterns = [
            {
                'name': 'Основной паттерн',
                'search_pattern': bytes([0x1F, 0x02, 0xF9, 0x8B]),
                'target_offset': 2,  # смещение от начала паттерна до целевого байта
                'expected_value': 0xF9,
                'new_value': 0xFF,
                'description': 'Поиск 1F 02 F9 8B, замена F9 на FF'
            },
            {
                'name': 'Паттерн F4 01 00 20',
                'search_pattern': bytes([0xF4, 0x01, 0x00, 0x20]),
                'target_offset': 2,  # третий байт (00)
                'expected_value': 0x00,
                'new_value': 0x25,
                'description': 'Поиск F4 01 00 20, замена 00 на 25'
            },
            {
                'name': 'Паттерн F4 01 01 20',
                'search_pattern': bytes([0xF4, 0x01, 0x01, 0x20]),
                'target_offset': 2,  # третий байт (01)
                'expected_value': 0x01,
                'new_value': 0x25,
                'description': 'Поиск F4 01 01 20, замена 01 на 25'
            }
        ]

    def is_valid_size(self, buffer: bytearray) -> bool:
        return len(buffer) in self.allowed_sizes

    def find_pattern_addresses(self, buffer: bytearray, pattern_info: dict) -> list:
        pattern_addresses = []
        search_pattern = pattern_info['search_pattern']
        target_offset = pattern_info['target_offset']
        pattern_len = len(search_pattern)
        
        for i in range(len(buffer) - pattern_len + 1):
            if buffer[i:i + pattern_len] == search_pattern:
                target_addr = i + target_offset
                pattern_addresses.append(target_addr)
                pattern_hex = ' '.join(f'{b:02X}' for b in search_pattern)
                print(f"  Найдена последовательность {pattern_hex} по адресу 0x{i:06X}, целевой байт по адресу 0x{target_addr:06X}")
        
        return pattern_addresses

    def check_immobilizer_address(self, buffer: bytearray, addr: int, expected_value: int) -> bool:
        return addr < len(buffer) and buffer[addr] == expected_value

    def check(self, buffer: bytearray) -> bool:
        if not self.is_valid_size(buffer):
            return False
        
        # Проверяем все паттерны
        total_valid_addresses = 0
        for pattern_info in self.patterns:
            pattern_addresses = self.find_pattern_addresses(buffer, pattern_info)
            if pattern_addresses:
                valid_addresses = sum(
                    1 for addr in pattern_addresses 
                    if self.check_immobilizer_address(buffer, addr, pattern_info['expected_value'])
                )
                total_valid_addresses += valid_addresses
        
        if total_valid_addresses > 0:
            return super().check(buffer)
        
        return False

    def encode(self, buffer: bytearray):
        if not self.is_valid_size(buffer):
            print(f"Ошибка: неверный размер буфера {len(buffer)} байт (ожидается один из: {self.allowed_sizes})")
            return

        print("Поиск всех паттернов...")
        
        total_patched = 0
        found_patterns = []
        
        # Обрабатываем каждый паттерн
        for pattern_info in self.patterns:
            print(f"\n--- {pattern_info['name']} ---")
            print(f"Описание: {pattern_info['description']}")
            
            pattern_addresses = self.find_pattern_addresses(buffer, pattern_info)
            
            if not pattern_addresses:
                print(f"Последовательность не найдена для паттерна '{pattern_info['name']}'")
                continue
            
            print(f"Найдено {len(pattern_addresses)} вхождений для паттерна '{pattern_info['name']}'")
            
            patched_count = 0
            pattern_results = {
                'name': pattern_info['name'],
                'addresses': [],
                'patched_count': 0
            }
            
            for addr in pattern_addresses:
                if self.check_immobilizer_address(buffer, addr, pattern_info['expected_value']):
                    old_value = buffer[addr]
                    buffer[addr] = pattern_info['new_value']
                    patched_count += 1
                    pattern_results['addresses'].append(addr)
                    print(f"  Адрес 0x{addr:06X}: 0x{old_value:02X} -> 0x{pattern_info['new_value']:02X}")
                else:
                    current_value = buffer[addr] if addr < len(buffer) else 0xFF
                    print(f"  Адрес 0x{addr:06X}: пропущен (текущее значение 0x{current_value:02X}, ожидается 0x{pattern_info['expected_value']:02X})")
            
            pattern_results['patched_count'] = patched_count
            total_patched += patched_count
            
            if patched_count > 0:
                found_patterns.append(pattern_results)
                print(f"Для паттерна '{pattern_info['name']}' изменено {patched_count} байт(ов)")
            else:
                print(f"Для паттерна '{pattern_info['name']}' не найдено валидных адресов для патча")

        # Итоговый отчет
        print(f"\n{'='*50}")
        print(f"ИТОГОВЫЙ ОТЧЕТ:")
        print(f"{'='*50}")
        
        if total_patched == 0:
            print("Ошибка: не найдено ни одного валидного адреса для патча!")
            print("Файл не подходит ни для одного из доступных патчей.")
            return
        
        print(f"Всего обработано паттернов: {len([p for p in found_patterns if p['patched_count'] > 0])}")
        print(f"Общее количество измененных байт: {total_patched}")
        
        for pattern_result in found_patterns:
            if pattern_result['patched_count'] > 0:
                print(f"  - {pattern_result['name']}: {pattern_result['patched_count']} изменений")
        
        print(f"\nПатч успешно применён!")
        print("Иммобилайзер отключен.")