from encoder import Encoder

class nissan_hitachi_sh705507n_NI(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 524288
        self.size_max = 524288
        
        # Последовательность байт для точного поиска
        self.search_pattern = bytes([0x06, 0x0E, 0x00, 0x0E, 0x03, 0x1B, 0x18, 0x18, 0x05, 0x01])
        
        # Ожидаемое значение для проверки
        self.expected_value = 0x01
        
        # Новое значение для отключения иммобилайзера
        self.new_value = 0x00
    
    def find_pattern_addresses(self, buffer: bytearray) -> list:
        """Находит все адреса, где встречается искомая последовательность байт"""
        pattern_addresses = []
        pattern_len = len(self.search_pattern)
        
        for i in range(len(buffer) - pattern_len + 1):
            if buffer[i:i + pattern_len] == self.search_pattern:
                # Адрес байта 0x01 в найденной последовательности (позиция 9)
                target_addr = i + 9
                pattern_addresses.append(target_addr)
                print(f"  Найдена последовательность по адресу 0x{i:10X}, байт 0x01 по адресу 0x{target_addr:10X}")
        
        return pattern_addresses
    
    def check_immobilizer_address(self, buffer: bytearray, addr) -> bool:
        """Проверяет один адрес на наличие значения 0x01"""
        if addr >= len(buffer):
            return False
        if buffer[addr] != self.expected_value:
            return False
        return True
    
    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        
        # Ищем по последовательности байт
        pattern_addresses = self.find_pattern_addresses(buffer)
        if len(pattern_addresses) > 0:
            # Проверяем, что найденные адреса содержат правильное значение
            valid_pattern_addresses = 0
            for addr in pattern_addresses:
                if self.check_immobilizer_address(buffer, addr):
                    valid_pattern_addresses += 1
            
            if valid_pattern_addresses > 0:
                return super().check(buffer)
        
        return False
    
    def encode(self, buffer: bytearray):
        # Проверяем размер буфера
        if not self.check(buffer):
            print(f"Ошибка: размер буфера {len(buffer)} не соответствует {self.size_min} байтам")
            return
        
        print("Поиск последовательности байт 06 0E 00 0E 03 1B 18 18 05 (01)...")
        
        # Ищем последовательность байт
        pattern_addresses = self.find_pattern_addresses(buffer)
        
        if len(pattern_addresses) == 0:
            print("Ошибка: последовательность байт не найдена!")
            print("Файл не подходит для данного патча.")
            return
        
        print(f"Найдено {len(pattern_addresses)} вхождений последовательности")
        print("Применение точного патча по найденным адресам...")
        
        patched_count = 0
        
        for addr in pattern_addresses:
            if self.check_immobilizer_address(buffer, addr):
                old_value = buffer[addr]
                new_value = self.new_value
                buffer[addr] = new_value
                patched_count += 1
                print(f"  Адрес 0x{addr:06X}: 0x{old_value:02X} -> 0x{new_value:02X}")
            else:
                current_value = buffer[addr] if addr < len(buffer) else 0xFF
                print(f"  Адрес 0x{addr:06X}: пропущен (текущее значение 0x{current_value:02X}, ожидается 0x{self.expected_value:02X})")
        
        if patched_count == 0:
            print("Ошибка: не найдено ни одного валидного адреса для патча!")
            return
        
        # Заполнение диапазона 0x4506-0x4520 значениями 0x00, пропуская 0x450C, 0x450D, 0x4518, 0x4519
        start_addr = 0x4506
        end_addr = 0x4520
        bytes_filled = 0
        excluded_addresses = {0x450C, 0x450D, 0x4518, 0x4519}
        
        for address in range(start_addr, end_addr + 1):
            if address not in excluded_addresses and address < len(buffer):
                buffer[address] = 0x00
                bytes_filled += 1
            elif address in excluded_addresses and address < len(buffer):
                print(f"  Адрес 0x{address:04X} пропущен по требованию")
            else:
                print(f"Предупреждение: адрес 0x{address:04X} выходит за границы буфера")
                break
        
        print(f"\nТочный патч успешно применён!")
        print(f"Всего изменено байт (поиск последовательности): {patched_count}")
        print(f"Заполнена область 0x{start_addr:04X}-0x{end_addr:04X} ({bytes_filled} байт, исключая 0x450C, 0x450D, 0x4518, 0x4519)")
        print("Иммобилайзер отключен.")