from encoder import Encoder

class M798_MG798_NI(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 851968
        self.size_max = 917504
        
        # Первая группа паттернов (изменяем следующий байт на 0x26)
        self.pattern_group_1 = [
            bytes([0x02, 0x02, 0x02, 0x01, 0x04]),
            bytes([0x02, 0x02, 0x02, 0x01, 0x01])
        ]
        
        # Вторая группа паттернов (изменяем следующий байт на 0x25)
        self.pattern_group_2 = [
            bytes([0x03, 0x00, 0x04, 0xAF, 0xAF]),
            bytes([0x03, 0x00, 0x04, 0xAF, 0x7D])
        ]
        
        # Значения для замены
        self.replace_value_group_1 = 0x26
        self.replace_value_group_2 = 0x25

    def find_pattern_and_modify(self, buffer: bytearray, patterns: list, replace_value: int, group_name: str) -> bool:
        """Ищет паттерны из списка и изменяет следующий байт на указанное значение только один раз"""
        found_pattern = False
        
        for pattern_index, pattern in enumerate(patterns):
            pattern_len = len(pattern)
            for i in range(len(buffer) - pattern_len):
                if buffer[i:i + pattern_len] == pattern:
                    target_addr = i + pattern_len
                    if target_addr < len(buffer):
                        found_pattern = True
                        pattern_hex = ' '.join([f'0x{b:02X}' for b in pattern])
                        print(f"✓ Найден {group_name} паттерн #{pattern_index + 1}: {pattern_hex}")
                        old_value = buffer[target_addr]
                        buffer[target_addr] = replace_value
                        print(f"  Паттерн по адресу 0x{i:05X}, изменён байт 0x{target_addr:05X}: 0x{old_value:02X} -> 0x{replace_value:02X}")
                        break
            if found_pattern:
                break
        
        return found_pattern

    def check(self, buffer: bytearray) -> bool:
        if len(buffer) not in (self.size_min, self.size_max):
            print(f"Неверный размер файла: {len(buffer)} байт (допустимо {self.size_min} или {self.size_max})")
            return False

        # Проверка первой группы паттернов
        if not any(
            buffer[i:i+len(p)] == p
            for p in self.pattern_group_1
            for i in range(len(buffer) - len(p))
        ):
            print("Файл не прошел проверку: не найден ни один паттерн первой группы")
            return False

        # Проверка второй группы паттернов
        if not any(
            buffer[i:i+len(p)] == p
            for p in self.pattern_group_2
            for i in range(len(buffer) - len(p))
        ):
            print("Файл не прошел проверку: не найден ни один паттерн второй группы")
            return False

        return super().check(buffer)

    def encode(self, buffer: bytearray):
        if len(buffer) not in (self.size_min, self.size_max):
            print(f"Ошибка: неверный размер буфера {len(buffer)} байт (ожидается {self.size_min} или {self.size_max})")
            return

        print("=== Начало обработки файла ===")
        print("Поиск и применение паттернов...")

        # Обработка первой группы
        print("\n--- Обработка первой группы паттернов ---")
        group1_success = self.find_pattern_and_modify(
            buffer, self.pattern_group_1, self.replace_value_group_1, "первой группы"
        )
        if not group1_success:
            print("✗ Не найден ни один паттерн первой группы!")
            print("Файл не подходит для данного патча.")
            return

        # Обработка второй группы
        print("\n--- Обработка второй группы паттернов ---")
        group2_success = self.find_pattern_and_modify(
            buffer, self.pattern_group_2, self.replace_value_group_2, "второй группы"
        )
        if not group2_success:
            print("✗ Не найден ни один паттерн второй группы!")
            print("Файл не подходит для данного патча.")
            return

        print(f"\n=== Результат обработки ===")
        print(f"✓ Найдены и обработаны паттерны обеих групп")
        print(f"✓ Форматирование завершено успешно!")
        print("Иммобилайзер отключен.")
