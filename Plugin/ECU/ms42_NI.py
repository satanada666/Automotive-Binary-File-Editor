from encoder import Encoder

class ms42_NI(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 524288
        self.size_max = 524288
        
        self.patterns = [
            {
                'name': 'Паттерн 1',
                'search_pattern': bytes([0x88, 0x90, 0x88, 0x60, 0x8A, 0x0E, 0x02, 0xF0, 0xEA]),
                'expected_value': bytes([0x88, 0x90, 0x88, 0x60, 0x8A, 0x0E, 0x02, 0xF0, 0xEA]),
                'new_value':      bytes([0xDA, 0x07, 0xC8, 0x59, 0xFE, 0x0E, 0x2E, 0x0F, 0xDB]),
            },
            {
                'name': 'Паттерн 2',
                'search_pattern': bytes([0x47, 0xF3, 0x07, 0x00, 0xA4, 0x00, 0x05, 0x00, 0x05, 0x03]),
                'expected_value': bytes([0x47, 0xF3, 0x07, 0x00, 0xA4, 0x00, 0x05, 0x00, 0x05, 0x03]),
                'new_value':      bytes([0x3E, 0x48, 0x07, 0x00, 0xA4, 0x00, 0x05, 0x00, 0x05, 0x03]),
            }
        ]
        
        self.active_pattern = None

    def find_pattern_addresses(self, buffer: bytearray, pattern_info) -> list:
        pattern_addresses = []
        search_pattern = pattern_info['search_pattern']
        pattern_len = len(search_pattern)
        
        for i in range(len(buffer) - pattern_len + 1):
            if buffer[i:i + pattern_len] == search_pattern:
                pattern_addresses.append(i)
                print(f"  Найдена последовательность по адресу 0x{i:05X}")
        
        return pattern_addresses

    def check_immobilizer_address(self, buffer: bytearray, addr: int, expected_bytes: bytes) -> bool:
        if addr < 0 or addr + len(expected_bytes) > len(buffer):
            return False
        return buffer[addr:addr + len(expected_bytes)] == expected_bytes

    def check_patterns_exist(self, buffer: bytearray) -> bool:
        print("Проверка наличия всех паттернов...")
        
        found_patterns = []
        
        for pattern_info in self.patterns:
            print(f"\nПроверка {pattern_info['name']}:")
            pattern_addresses = self.find_pattern_addresses(buffer, pattern_info)
            
            if pattern_addresses:
                valid = sum(
                    1 for addr in pattern_addresses
                    if self.check_immobilizer_address(buffer, addr, pattern_info['expected_value'])
                )
                if valid:
                    found_patterns.append(pattern_info)
                    print(f"✓ Найден {pattern_info['name']} (валидных: {valid})")
                else:
                    print("✗ Нет валидных совпадений")
            else:
                print("✗ Паттерн не найден")
        
        if len(found_patterns) == len(self.patterns):
            print(f"\n✓ Все {len(self.patterns)} паттерна найдены")
            return True
        else:
            print(f"\n✗ Найдено только {len(found_patterns)} из {len(self.patterns)} паттернов")
            return False

    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        return self.check_patterns_exist(buffer)

    def encode(self, buffer: bytearray):
        if len(buffer) != self.size_min:
            print(f"Ошибка: размер буфера {len(buffer)} (ожидается {self.size_min})")
            return

        print("=== Начало обработки файла ===")

        if not self.check_patterns_exist(buffer):
            print("Файл не подходит для патча - не найдены все необходимые паттерны.")
            return
        
        total_patched = 0

        # Применяем все найденные паттерны
        for pattern in self.patterns:
            print(f"\n=== Обработка {pattern['name']} ===")
            pattern_addresses = self.find_pattern_addresses(buffer, pattern)

            if not pattern_addresses:
                print(f"Паттерн {pattern['name']} не найден в файле.")
                continue

            patched = 0
            for addr in pattern_addresses:
                expected = pattern['expected_value']
                new = pattern['new_value']

                if self.check_immobilizer_address(buffer, addr, expected):
                    print(f"  Патч @ 0x{addr:05X}: {buffer[addr:addr+len(new)].hex().upper()} → {new.hex().upper()}")
                    buffer[addr:addr+len(new)] = new
                    patched += 1
                else:
                    actual = buffer[addr:addr+len(expected)].hex().upper()
                    print(f"  Пропущено @ 0x{addr:05X}: ожидалось {expected.hex().upper()}, найдено {actual}")

            print(f"✓ Применено {patched} патч(ей) для {pattern['name']}")
            total_patched += patched

        if total_patched:
            print(f"\n✓ Всего применено {total_patched} патч(ей). Иммобилайзер отключен.")
        else:
            print("✗ Патчи не применены.")