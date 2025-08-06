from encoder import Encoder

class nissan_classic_SH705524N_NI(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 524288
        self.size_max = 524288
        # Последовательность байт для поиска
        self.search_pattern = bytes([0x07, 0xC8, 0x7A, 0x3E, 0x5E, 0x03, 0xF8, 0x37, 0x85, 0xC1, 0xA1, 0xFC])
        
        # Ожидаемое значение (искомая последовательность)
        self.expected_value = bytes([0x07, 0xC8, 0x7A, 0x3E, 0x5E, 0x03, 0xF8, 0x37, 0x85, 0xC1, 0xA1, 0xFC])
        
        # Новое значение
        self.new_value = bytes([0xA2, 0x62, 0x77, 0xE1, 0xA1, 0x5F, 0x5D, 0x9D, 0x88, 0x1E, 0x5E, 0xA0])
    
    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        
        # Сначала ищем последовательность SH705524N в диапазоне 0x1bd0-0x1be4
        search_start = 0x1bd0
        search_end = 0x1be4
        expected_signature = bytes([0x53, 0x48, 0x37, 0x30, 0x35, 0x35, 0x32, 0x34])  # SH705524
        
        # Проверяем что диапазон поиска не выходит за границы буфера
        if search_end >= len(buffer):
            return False
        
        # Ищем сигнатуру SH705524 в указанном диапазоне
        signature_found = False
        for addr in range(search_start, search_end - len(expected_signature) + 2):
            if addr + len(expected_signature) <= len(buffer):
                if buffer[addr:addr + len(expected_signature)] == expected_signature:
                    signature_found = True
                    break
        
        if not signature_found:
            return False

        # Если сигнатура найдена, ищем паттерн для патча
        pattern_addresses = self.find_pattern_addresses(buffer)
        if not pattern_addresses:
            return False

        # Проверяем, что хотя бы один адрес содержит искомую последовательность
        for addr in pattern_addresses:
            if self.check_pattern_match(buffer, addr):
                return super().check(buffer)
        
        return False
    
    def find_pattern_addresses(self, buffer: bytearray) -> list:
        """Находит все адреса, где встречается искомая последовательность байт"""
        pattern_addresses = []
        pattern_len = len(self.search_pattern)
        
        for i in range(len(buffer) - pattern_len + 1):
            if buffer[i:i + pattern_len] == self.search_pattern:
                pattern_addresses.append(i)
                print(f"  Найдена последовательность по адресу 0x{i:06X}")
        
        return pattern_addresses

    def check_pattern_match(self, buffer: bytearray, addr) -> bool:
        """Проверяет, что по адресу находится искомая последовательность"""
        if addr + len(self.expected_value) > len(buffer):
            return False
        return buffer[addr:addr + len(self.expected_value)] == self.expected_value
    
    def encode(self, buffer: bytearray):
        if len(buffer) != self.size_min:
            print(f"Ошибка: неверный размер буфера {len(buffer)} байт (ожидается {self.size_min})")
            return

        # Сначала проверяем наличие сигнатуры SH705524
        search_start = 0x1bd0
        search_end = 0x1be4
        expected_signature = bytes([0x53, 0x48, 0x37, 0x30, 0x35, 0x35, 0x32, 0x34])  # SH705524
        
        signature_found = False
        signature_addr = None
        
        if search_end < len(buffer):
            for addr in range(search_start, search_end - len(expected_signature) + 2):
                if addr + len(expected_signature) <= len(buffer):
                    if buffer[addr:addr + len(expected_signature)] == expected_signature:
                        signature_found = True
                        signature_addr = addr
                        break
        
        if not signature_found:
            print("Ошибка: не найдена сигнатура SH705524!")
            print(f"Поиск в диапазоне 0x{search_start:04X}-0x{search_end:04X}")
            print(f"Ожидается последовательность: {expected_signature.hex().upper()}")
            return
        
        print(f"Сигнатура SH705524 найдена по адресу 0x{signature_addr:04X}")
        print("Поиск последовательности для патча...")
        
        pattern_addresses = self.find_pattern_addresses(buffer)

        if not pattern_addresses:
            print("Ошибка: последовательность для патча не найдена!")
            print(f"Ищется последовательность: {self.search_pattern.hex().upper()}")
            return

        print(f"Найдено {len(pattern_addresses)} вхождений последовательности")
        print("Применение патча по найденным адресам...")

        patched_count = 0

        for addr in pattern_addresses:
            if self.check_pattern_match(buffer, addr):
                old_bytes = buffer[addr:addr + len(self.new_value)]
                # Заменяем всю последовательность
                for i in range(len(self.new_value)):
                    buffer[addr + i] = self.new_value[i]
                print(f"  Адрес 0x{addr:06X}: {old_bytes.hex().upper()} -> {self.new_value.hex().upper()}")
                patched_count += 1
            else:
                current = buffer[addr:addr + len(self.expected_value)]
                print(f"  Адрес 0x{addr:06X}: пропущен (найдено {current.hex().upper()}, ожидалось {self.expected_value.hex().upper()})")

        if patched_count == 0:
            print("Ошибка: не найдено ни одного валидного адреса для патча!")
        else:
            print(f"\nПатч успешно применён! Изменено участков: {patched_count}")
            print("Патч успешно применён к nissan_classic_SH705524N_NI")


##############

class ME17_9_11_12_activate_cruise_control_NO_CS_CS_Winols(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 1540096
        self.size_max = 1540096

        # Последовательность байт для поиска
        self.search_pattern = bytes([0x07, 0xC8, 0x7A, 0x3E, 0x5E, 0x03, 0xF8, 0x37, 0x85, 0xC1, 0xA1, 0xFC])
        
        # Ожидаемое значение на позиции после найденной последовательности (должно быть 2 байта)
        self.expected_value = bytes([0xFF, 0xFF])

        # Новое значение (2 байта)
        self.new_value = bytes([0xA2, 0x62])

    def find_pattern_addresses(self, buffer: bytearray) -> list:
        """Находит все адреса, где встречается искомая последовательность байт"""
        pattern_addresses = []
        pattern_len = len(self.search_pattern)
        
        for i in range(len(buffer) - pattern_len + 1):
            if buffer[i:i + pattern_len] == self.search_pattern:
                # Сохраняем адрес следующих 2 байт после найденной последовательности
                target_addr = i + pattern_len
                pattern_addresses.append(target_addr)
                print(f"  Найдена последовательность по адресу 0x{i:06X}, целевой адрес 0x{target_addr:06X}")
        
        return pattern_addresses

    def check_target_bytes(self, buffer: bytearray, addr) -> bool:
        """Проверяет, что по адресу находятся два ожидаемых байта (FF FF)"""
        if addr + 1 >= len(buffer):
            return False
        return buffer[addr:addr + 2] == self.expected_value

    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False

        pattern_addresses = self.find_pattern_addresses(buffer)
        if not pattern_addresses:
            return False

        # Проверяем, что хотя бы один адрес содержит ожидаемые байты
        for addr in pattern_addresses:
            if self.check_target_bytes(buffer, addr):
                return super().check(buffer)
        
        return False

    def encode(self, buffer: bytearray):
        if len(buffer) != self.size_min:
            print(f"Ошибка: неверный размер буфера {len(buffer)} байт (ожидается {self.size_min})")
            return

        print(f"Поиск последовательности байт {self.search_pattern.hex().upper()}...")
        pattern_addresses = self.find_pattern_addresses(buffer)

        if not pattern_addresses:
            print("Ошибка: последовательность байт не найдена!")
            print("Файл не подходит для данного патча.")
            return

        print(f"Найдено {len(pattern_addresses)} вхождений последовательности")
        print("Применение патча по найденным адресам...")

        patched_count = 0

        for addr in pattern_addresses:
            if self.check_target_bytes(buffer, addr):
                old_bytes = buffer[addr:addr + 2]
                buffer[addr] = self.new_value[0]
                buffer[addr + 1] = self.new_value[1]
                print(f"  Адрес 0x{addr:06X}: {old_bytes.hex().upper()} -> {self.new_value.hex().upper()}")
                patched_count += 1
            else:
                current = buffer[addr:addr + 2] if addr + 1 < len(buffer) else buffer[addr:addr + 1]
                print(f"  Адрес 0x{addr:06X}: пропущен (найдено {current.hex().upper()}, ожидалось {self.expected_value.hex().upper()})")

        if patched_count == 0:
            print("Ошибка: не найдено ни одного валидного адреса для патча!")
        else:
            print(f"\nПатч успешно применён! Изменено участков: {patched_count}")
            print("Cruise Control активирован.")