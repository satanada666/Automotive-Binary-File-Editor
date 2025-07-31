from encoder import Encoder

class sirius_d3_d4_NI(Encoder):
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
        
        # 1) Затираем FF с адреса 0x4000-0x8000
        print("Шаг 1: Затираем область 0x4000-0x8000 значениями 0xFF")
        for address in range(0x4000, 0x8000):  # до 0x8000 включ
            if address < len(buffer):
                buffer[address] = 0xFF
        print(f"Обнулена область 0x4000-0x8000 ({0x8000 - 0x4000 + 1} байт)")
        
        # Определяем паттерны для двух вариантов
        variant1_patterns = [
            # Паттерн 1: (03) 03 08 C8 C8 - меняем первый байт 03 на FE
            {
                'pattern': [0x03, 0x03, 0x08, 0xC8, 0xC8],
                'changes': [(0, 0xFE)],  # позиция 0, новое значение FE
                'name': '03 03 08 C8 C8'
            },
            # Паттерн 2: (88) 00 (88) 00 00 01 FF - меняем 1-й и 3-й байты 88 на 80
            {
                'pattern': [0x88, 0x00, 0x88, 0x00, 0x00, 0x01, 0xFF],
                'changes': [(0, 0x80), (2, 0x80)],  # позиции 0 и 2, новое значение 80
                'name': '88 00 88 00 00 01 FF'
            },
            # Паттерн 3: 00 C2 80 00 80 00 86 86 (04) 04 - меняем предпоследний байт 04 на 00
            {
                'pattern': [0x00, 0xC2, 0x80, 0x00, 0x80, 0x00, 0x86, 0x86, 0x04, 0x04],
                'changes': [(8, 0x00)],  # позиция 8 (предпоследний), новое значение 00
                'name': '00 C2 80 00 80 00 86 86 04 04'
            }
        ]
        
        variant2_patterns = [
            # Паттерн 1: (03) 03 08 C8 C8 - меняем первый байт 03 на FE
            {
                'pattern': [0x03, 0x03, 0x08, 0xC8, 0xC8],
                'changes': [(0, 0xFE)],  # позиция 0, новое значение FE
                'name': '03 03 08 C8 C8'
            },
            # Паттерн 2: 00 (8C) 00 (8C) 00 01 FF - меняем 2-й и 4-й байты 8C на 80
            {
                'pattern': [0x00, 0x8C, 0x00, 0x8C, 0x00, 0x01, 0xFF],
                'changes': [(1, 0x80), (3, 0x80)],  # позиции 1 и 3, новое значение 80
                'name': '00 8C 00 8C 00 01 FF'
            },
            # Паттерн 3: 00 C2 80 00 80 00 86 86 86 (04) 04 - меняем предпоследний байт 04 на 00
            {
                'pattern': [0x00, 0xC2, 0x80, 0x00, 0x80, 0x00, 0x86, 0x86, 0x86, 0x04, 0x04],
                'changes': [(9, 0x00)],  # позиция 9 (предпоследний), новое значение 00
                'name': '00 C2 80 00 80 00 86 86 86 04 04'
            }
        ]
        
        # Функция для поиска паттернов (без применения изменений)
        def find_patterns(patterns, variant_name):
            print(f"\n=== Поиск паттернов для {variant_name} ===")
            found_patterns = []
            
            for step, pattern_info in enumerate(patterns, 2):
                print(f"\nШаг {step}: Поиск последовательности {pattern_info['name']}")
                pattern = pattern_info['pattern']
                found_count = 0
                
                for i in range(len(buffer) - len(pattern) + 1):
                    # Проверяем совпадение паттерна
                    match = True
                    for j in range(len(pattern)):
                        if buffer[i + j] != pattern[j]:
                            match = False
                            break
                    
                    if match:
                        found_patterns.append((i, pattern_info))
                        print(f"Найдена последовательность {pattern_info['name']} по адресу 0x{i:04X}")
                        # Показываем найденные байты для отладки
                        hex_str = " ".join([f"{buffer[i+j]:02X}" for j in range(len(pattern))])
                        print(f"Байты: {hex_str}")
                        found_count += 1
                
                if found_count == 0:
                    print(f"Последовательность {pattern_info['name']} не найдена")
                else:
                    print(f"Найдено {found_count} вхождений последовательности {pattern_info['name']}")
            
            return found_patterns
        
        # Функция для применения изменений
        def apply_changes(found_patterns, variant_name):
            print(f"\n=== Применение изменений для {variant_name} ===")
            total_applied = 0
            
            for address, pattern_info in found_patterns:
                changes = pattern_info['changes']
                print(f"\nПрименяем изменения для {pattern_info['name']} по адресу 0x{address:04X}")
                
                for pos, new_value in changes:
                    if address + pos < len(buffer):
                        old_value = buffer[address + pos]
                        buffer[address + pos] = new_value
                        print(f"Изменен байт в позиции {pos} (0x{address+pos:04X}): 0x{old_value:02X} -> 0x{new_value:02X}")
                        total_applied += 1
            
            return total_applied
        
        # Объединяем все паттерны из обоих вариантов в один список
        all_patterns = [
            # Из варианта 1
            {
                'pattern': [0x03, 0x03, 0x08, 0xC8, 0xC8],
                'changes': [(0, 0xFE)],
                'name': '03 03 08 C8 C8 (вар.1)',
                'variant': 1
            },
            {
                'pattern': [0x88, 0x00, 0x88, 0x00, 0x00, 0x01, 0xFF],
                'changes': [(0, 0x80), (2, 0x80)],
                'name': '88 00 88 00 00 01 FF (вар.1)',
                'variant': 1
            },
            {
                'pattern': [0x00, 0xC2, 0x80, 0x00, 0x80, 0x00, 0x86, 0x86, 0x04, 0x04],
                'changes': [(8, 0x00)],
                'name': '00 C2 80 00 80 00 86 86 04 04 (вар.1)',
                'variant': 1
            },
            # Из варианта 2
            {
                'pattern': [0x03, 0x03, 0x08, 0xC8, 0xC8],
                'changes': [(0, 0xFE)],
                'name': '03 03 08 C8 C8 (вар.2)',
                'variant': 2
            },
            {
                'pattern': [0x00, 0x8C, 0x00, 0x8C, 0x00, 0x01, 0xFF],
                'changes': [(1, 0x80), (3, 0x80)],
                'name': '00 8C 00 8C 00 01 FF (вар.2)',
                'variant': 2
            },
            {
                'pattern': [0x00, 0xC2, 0x80, 0x00, 0x80, 0x00, 0x86, 0x86, 0x86, 0x04, 0x04],
                'changes': [(9, 0x00)],
                'name': '00 C2 80 00 80 00 86 86 86 04 04 (вар.2)',
                'variant': 2
            }
        ]
        
        print("\n=== Поиск всех 6 паттернов ===")
        applied_patterns = 0
        found_addresses = set()  # Чтобы не применять дважды к одному адресу
        
        # Проходим по всему буферу
        for i in range(len(buffer)):
            if applied_patterns >= 3:
                print("\n🎯 НАЙДЕНЫ И ПРИМЕНЕНЫ 3 ПАТТЕРНА! Завершаем обработку.")
                break
                
            # Проверяем каждый паттерн на текущей позиции
            for pattern_info in all_patterns:
                pattern = pattern_info['pattern']
                
                # Проверяем, поместится ли паттерн
                if i + len(pattern) > len(buffer):
                    continue
                    
                # Проверяем совпадение паттерна
                match = True
                for j in range(len(pattern)):
                    if buffer[i + j] != pattern[j]:
                        match = False
                        break
                
                if match and i not in found_addresses:
                    # Нашли совпадение! Сразу применяем изменения
                    print(f"\n✓ Найден паттерн: {pattern_info['name']}")
                    print(f"  Адрес: 0x{i:04X}")
                    
                    # Показываем найденные байты
                    hex_str = " ".join([f"{buffer[i+j]:02X}" for j in range(len(pattern))])
                    print(f"  Байты: {hex_str}")
                    
                    # Применяем изменения
                    changes = pattern_info['changes']
                    for pos, new_value in changes:
                        if i + pos < len(buffer):
                            old_value = buffer[i + pos]
                            buffer[i + pos] = new_value
                            print(f"  Изменен байт в позиции {pos} (0x{i+pos:04X}): 0x{old_value:02X} -> 0x{new_value:02X}")
                    
                    found_addresses.add(i)
                    applied_patterns += 1
                    print(f"  Применено паттернов: {applied_patterns}/3")
                    
                    if applied_patterns >= 3:
                        break
        
        # Итоговая информация
        if applied_patterns == 0:
            print("\n❌ НИ ОДИН ПАТТЕРН НЕ НАЙДЕН!")
        elif applied_patterns < 3:
            print(f"\n⚠️  Найдено только {applied_patterns}/3 паттернов. Возможно, файл частично совместим.")
        else:
            print(f"\n🎯 УСПЕШНО! Найдены и применены все 3 паттерна!")
        
        print("\nПатч успешно применён к sirius_d3_d4_NI")
        print("Все этапы обработки завершены")