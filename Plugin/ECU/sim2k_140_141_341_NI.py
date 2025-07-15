from encoder import Encoder

class sim2k_140_141_341_NI(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 2097152
        self.size_max = 2097152
        
        # Группы адресов для проверки иммобилайзера (по 3 адреса в каждой группе)
        self.immobilizer_groups = [
            (0x17EFF, 0x17E8AC, 0x17E8AD),
            (0x1740CF, 0x17416C, 0x17416D),
            (0x17A30B, 0x17A3A8, 0x17A3A9),
            (0x145C4B, 0x145CE4, 0x145CE5),
            (0x15F367, 0x15F400, 0x15F401),
            (0x16E60F, 0x16E6AC, 0x16E6AD),
            (0x17A73F, 0x17A7DC, 0x17A7DD),
            (0x11A8EF, 0x11A968, 0x11A969),
            (0x144D3B, 0x144DD4, 0x144DD5),
            (0x177673, 0x177710, 0x177711),
            (0x17E80F, 0x17E8AC, 0x17E8AD) 
            (0x17E847, 0x17AE6B)
        ]
        
        # Ожидаемые значения для проверки
        self.expected_values = [0x01, 0x40, 0x82]
        
        # Новые значения для отключения иммобилайзера
        self.new_values = [0x00, 0x48, 0x00]
    
    def check_immobilizer_group(self, buffer: bytearray, group_addresses) -> bool:
        """Проверяет одну группу из 3 адресов на наличие значений 01, 40, 82"""
        for i, addr in enumerate(group_addresses):
            if addr >= len(buffer):
                return False
            if buffer[addr] != self.expected_values[i]:
                return False
        return True
    
    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        
        # Проверяем, что хотя бы одна группа адресов содержит правильные значения
        valid_groups = 0
        for group_idx, group_addresses in enumerate(self.immobilizer_groups):
            if self.check_immobilizer_group(buffer, group_addresses):
                valid_groups += 1
        
        if valid_groups == 0:
            return False
        
        return super().check(buffer)
    
    def encode(self, buffer: bytearray):
        # Проверяем, что буфер соответствует требованиям
        if not self.check(buffer):
            print(f"Ошибка: буфер не соответствует требованиям sim2k_140_141_341_NI")
            print(f"Размер буфера: {len(buffer)} байт (ожидается {self.size_min})")
            
            # Проверка групп адресов для диагностики
            print("\nПроверка групп адресов иммобилайзера:")
            valid_groups = 0
            
            for group_idx, group_addresses in enumerate(self.immobilizer_groups):
                print(f"\nГруппа {group_idx + 1}:")
                group_valid = True
                
                for i, addr in enumerate(group_addresses):
                    if addr < len(buffer):
                        current_value = buffer[addr]
                        expected_value = self.expected_values[i]
                        status = "✓" if current_value == expected_value else "✗"
                        if current_value != expected_value:
                            group_valid = False
                        print(f"  Адрес 0x{addr:06X}: {status} текущее=0x{current_value:02X}, ожидается=0x{expected_value:02X}")
                    else:
                        print(f"  Адрес 0x{addr:06X}: ✗ выходит за границы буфера")
                        group_valid = False
                
                if group_valid:
                    valid_groups += 1
                    print(f"  Группа {group_idx + 1}: ✓ ВАЛИДНА")
                else:
                    print(f"  Группа {group_idx + 1}: ✗ НЕ ВАЛИДНА")
            
            print(f"\nВсего валидных групп: {valid_groups}")
            print("Для работы требуется хотя бы одна валидная группа")
            
            return
        
        # Применяем патч для отключения иммобилайзера
        print("Применение патча для отключения иммобилайзера sim2k_140_141_341_NI...")
        patched_count = 0
        valid_groups = 0
        
        for group_idx, group_addresses in enumerate(self.immobilizer_groups):
            if self.check_immobilizer_group(buffer, group_addresses):
                valid_groups += 1
                print(f"\nОбработка валидной группы {group_idx + 1}:")
                
                for i, addr in enumerate(group_addresses):
                    old_value = buffer[addr]
                    new_value = self.new_values[i]
                    buffer[addr] = new_value
                    patched_count += 1
                    print(f"  Адрес 0x{addr:06X}: 0x{old_value:02X} -> 0x{new_value:02X}")
            else:
                print(f"Группа {group_idx + 1}: пропущена (не валидна)")
        
        print(f"\nПатч успешно применён!")
        print(f"Обработано валидных групп: {valid_groups}")
        print(f"Всего изменено байт: {patched_count}")
        print("Иммобилайзер отключен.")