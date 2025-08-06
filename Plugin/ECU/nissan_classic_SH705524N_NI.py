from encoder import Encoder

class nissan_classic_SH705524N_NI(Encoder):

    def __init__(self):
        super().__init__()
        self.size_min = 524288
        self.size_max = 524288
    
    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        return super().check(buffer)
    
    def encode(self, buffer: bytearray):
        # Проверяем, что буфер соответствует размеру
        if not self.check(buffer):
            print(f"Ошибка: размер буфера {len(buffer)} не соответствует {self.size_min} байтам")
            return
        
        # Определяем паттерны с wildcard-байтами (None означает любое значение)
        patterns = [
            # D8 0A 8A 78 (AA) - 55
            {
                'pattern': [0xD8, 0x0A, 0x8A, 0x78, None],
                'changes': [(4, 0x55)],
                'name': 'D8 0A 8A 78 (XX)',
                'description': 'D8 0A 8A 78 (AA) -> 55'
            },
            # 2D 18 18 05 00 (0C) - 02
            {
                'pattern': [0x2D, 0x18, 0x18, 0x05, 0x00, None],
                'changes': [(5, 0x02)],
                'name': '2D 18 18 05 00 (XX)',
                'description': '2D 18 18 05 00 (0C) -> 02'
            },
            # D4 00 00 0E 2B 5C - двойная замена!
            {
                'pattern': [0xD4, 0x00, 0x00, 0x0E, 0x2B, 0x5C, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
                'changes': [(6, 0xAC), (7, 0xA4), (8, 0x90), (18, 0xE8), (19, 0x90), (20, 0xEB)],
                'name': 'D4 00 00 0E 2B 5C (двойная замена)',
                'description': 'D4 00 00 0E 2B 5C -> сразу AC A4 90, через 9 байт E8 90 EB'
            },
            # 00 00 00 00 00 00 00 00 00 00 00 10 00 00 (70) 00 3F 00 - 40
            {
                'pattern': [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00, None, 0x00, 0x3F, 0x00],
                'changes': [(14, 0x40)],
                'name': '00 00 00 00 00 00 00 00 00 00 00 10 00 00 (XX) 00 3F 00',
                'description': '00 00 00 00 00 00 00 00 00 00 00 10 00 00 (70) 00 3F 00 -> 40'
            }
        ]
        
        print("=== Поиск и замена wildcard-паттернов ===")
        applied_patterns = 0
        found_addresses = set()  # Возвращаю для избежания повторных применений
        
        # Проходим по всему буферу
        for i in range(len(buffer)):
            # Проверяем каждый паттерн на текущей позиции
            for pattern_info in patterns:
                pattern = pattern_info['pattern']
                
                # Проверяем, поместится ли паттерн
                if i + len(pattern) > len(buffer):
                    continue
                    
                # Проверяем совпадение паттерна (None = wildcard, любое значение подходит)
                match = True
                for j in range(len(pattern)):
                    if pattern[j] is not None and buffer[i + j] != pattern[j]:
                        match = False
                        break
                
                # Создаем уникальный ключ для каждого паттерна на каждом адресе
                pattern_key = f"{i}_{pattern_info['name']}"
                
                if match and pattern_key not in found_addresses:
                    # Нашли совпадение! Применяем изменения
                    print(f"\n✓ Найден паттерн: {pattern_info['name']}")
                    print(f"  Адрес: 0x{i:04X}")
                    print(f"  Описание: {pattern_info['description']}")
                    
                    # Показываем найденные байты (до изменения)
                    hex_str_before = " ".join([
                        f"({buffer[i+j]:02X})" if pattern[j] is None else f"{buffer[i+j]:02X}"
                        for j in range(len(pattern))
                    ])
                    print(f"  Байты до: {hex_str_before}")
                    
                    # Применяем изменения
                    changes = pattern_info['changes']
                    for pos, new_value in changes:
                        if i + pos < len(buffer):
                            old_value = buffer[i + pos]
                            buffer[i + pos] = new_value
                            print(f"    Изменен байт в позиции {pos} (0x{i+pos:04X}): 0x{old_value:02X} -> 0x{new_value:02X}")
                    
                    # Показываем байты после изменения
                    hex_str_after = " ".join([
                        f"({buffer[i+j]:02X})" if pattern[j] is None else f"{buffer[i+j]:02X}"
                        for j in range(len(pattern))
                    ])
                    print(f"  Байты после: {hex_str_after}")
                    
                    found_addresses.add(pattern_key)
                    applied_patterns += 1
                    print(f"  Применено паттернов: {applied_patterns}/{len(patterns)}")
        
        # Итоговая информация
        if applied_patterns == 0:
            print("\n❌ НИ ОДИН ПАТТЕРН НЕ НАЙДЕН!")
        elif applied_patterns < len(patterns):
            print(f"\n⚠️  Найдено только {applied_patterns}/{len(patterns)} паттернов.")
        else:
            print(f"\n🎯 УСПЕШНО! Найдены и применены все {applied_patterns} паттернов!")
        
        print(f"\nПатч успешно применён к wildcard_pattern_encoder")
        print("Все этапы обработки завершены")