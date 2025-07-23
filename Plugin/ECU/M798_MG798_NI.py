from encoder import Encoder

class M798_MG798_NI(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 851968
        self.size_max = 851968
        
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
            
            # Поиск первого вхождения текущего паттерна
            for i in range(len(buffer) - pattern_len):
                if buffer[i:i + pattern_len] == pattern:
                    # Адрес байта, который нужно изменить (следующий после паттерна)
                    target_addr = i + pattern_len
                    if target_addr < len(buffer):
                        found_pattern = True
                        pattern_hex = ' '.join([f'0x{b:02X}' for b in pattern])
                        print(f"✓ Найден {group_name} паттерн #{pattern_index + 1}: {pattern_hex}")
                        
                        # Применяем изменение только к первому найденному адресу
                        old_value = buffer[target_addr]
                        buffer[target_addr] = replace_value
                        print(f"  Паттерн по адресу 0x{i:05X}, изменён байт 0x{target_addr:05X}: 0x{old_value:02X} -> 0x{replace_value:02X}")
                        
                        # Прерываем поиск после первого найденного паттерна
                        break
            
            # Если нашли паттерн, не проверяем остальные из группы
            if found_pattern:
                break
        
        return found_pattern


    
    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        
        # Проверяем наличие хотя бы одного паттерна из первой группы (только первое вхождение)
        group1_found = False
        for pattern in self.pattern_group_1:
            pattern_len = len(pattern)
            for i in range(len(buffer) - pattern_len):
                if buffer[i:i + pattern_len] == pattern:
                    group1_found = True
                    break
            if group1_found:
                break
        
        if not group1_found:
            print("Файл не прошел проверку: не найден ни один паттерн первой группы")
            return False
        
        # Проверяем наличие хотя бы одного паттерна из второй группы (только первое вхождение)
        group2_found = False
        for pattern in self.pattern_group_2:
            pattern_len = len(pattern)
            for i in range(len(buffer) - pattern_len):
                if buffer[i:i + pattern_len] == pattern:
                    group2_found = True
                    break
            if group2_found:
                break
        
        if not group2_found:
            print("Файл не прошел проверку: не найден ни один паттерн второй группы")
            return False
        
        return super().check(buffer)
    
    def encode(self, buffer: bytearray):
        # Проверяем размер буфера
        if len(buffer) != self.size_min:
            print(f"Ошибка: неверный размер буфера {len(buffer)} байт (ожидается {self.size_min})")
            return
        
        print("=== Начало обработки файла ===")
        
        print("Поиск и применение паттернов...")
        
        # Ищем и изменяем первую группу паттернов
        print("\n--- Обработка первой группы паттернов ---")
        group1_success = self.find_pattern_and_modify(
            buffer, self.pattern_group_1, self.replace_value_group_1, "первой группы"
        )
        
        if not group1_success:
            print("✗ Не найден ни один паттерн первой группы!")
            print("Файл не подходит для данного патча.")
            return
        
        # Ищем и изменяем вторую группу паттернов
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