from encoder import Encoder

class sim2k_240_241_242_245(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 2097152
        self.size_max = 2097152
        
        # Адреса для проверки иммобилайзера
        self.immobilizer_addresses = [
            0x134CD7,
            0x139F6B,
            0x10B2CB,
            0x12942F,
            0x130957,
            0x131D77
        ]
        
        # Ожидаемое значение для проверки
        self.expected_value = 0x01
        
        # Новое значение для отключения иммобилайзера
        self.new_value = 0x00
    
    def check_immobilizer_address(self, buffer: bytearray, addr) -> bool:
        """Проверяет один адрес на наличие значения 01"""
        if addr >= len(buffer):
            return False
        if buffer[addr] != self.expected_value:
            return False
        return True
    
    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        
        # Проверяем, что хотя бы один адрес содержит правильное значение
        valid_addresses = 0
        for addr in self.immobilizer_addresses:
            if self.check_immobilizer_address(buffer, addr):
                valid_addresses += 1
        
        if valid_addresses == 0:
            return False
        
        return super().check(buffer)
    
    def encode(self, buffer: bytearray):
        # Проверяем, что буфер соответствует требованиям
        if not self.check(buffer):
            print(f"Ошибка: буфер не соответствует требованиям sim2k_240_241_242_245")
            print(f"Размер буфера: {len(buffer)} байт (ожидается {self.size_min})")
            
            # Проверка адресов для диагностики
            print("\nПроверка адресов иммобилайзера:")
            valid_addresses = 0
            
            for addr_idx, addr in enumerate(self.immobilizer_addresses):
                if addr < len(buffer):
                    current_value = buffer[addr]
                    expected_value = self.expected_value
                    status = "✓" if current_value == expected_value else "✗"
                    if current_value == expected_value:
                        valid_addresses += 1
                    print(f"  Адрес 0x{addr:06X}: {status} текущее=0x{current_value:02X}, ожидается=0x{expected_value:02X}")
                else:
                    print(f"  Адрес 0x{addr:06X}: ✗ выходит за границы буфера")
            
            print(f"\nВсего валидных адресов: {valid_addresses}")
            print("Для работы требуется хотя бы один валидный адрес")
            
            return
        
        # Применяем патч для отключения иммобилайзера
        print("Применение патча для отключения иммобилайзера sim2k_240_241_242_245...")
        patched_count = 0
        valid_addresses = 0
        
        for addr_idx, addr in enumerate(self.immobilizer_addresses):
            if self.check_immobilizer_address(buffer, addr):
                valid_addresses += 1
                old_value = buffer[addr]
                new_value = self.new_value
                buffer[addr] = new_value
                patched_count += 1
                print(f"  Адрес 0x{addr:06X}: 0x{old_value:02X} -> 0x{new_value:02X}")
            else:
                if addr < len(buffer):
                    current_value = buffer[addr]
                    print(f"  Адрес 0x{addr:06X}: пропущен (текущее значение 0x{current_value:02X}, ожидается 0x{self.expected_value:02X})")
                else:
                    print(f"  Адрес 0x{addr:06X}: пропущен (выходит за границы буфера)")
        
        print(f"\nПатч успешно применён!")
        print(f"Обработано валидных адресов: {valid_addresses}")
        print(f"Всего изменено байт: {patched_count}")
        print("Иммобилайзер отключен.")