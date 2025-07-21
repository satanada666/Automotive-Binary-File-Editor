from encoder import Encoder

class ME17_9_11_12_activate_cruise_control_NO_CS_CS_Winols(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 1540096
        self.size_max = 1540096

        # Последовательность байт для поиска
        self.search_pattern = bytes([0xA0, 0x00, 0x02, 0x00, 0xFF, 0xFF])
        
        # Ожидаемое значение двух последних байт
        self.expected_value = bytes([0xFF, 0xFF])

        # Новое значение
        self.new_value = bytes([0x00, 0x14])

    def find_pattern_addresses(self, buffer: bytearray) -> list:
        """Находит все адреса, где встречается искомая последовательность байт"""
        pattern_addresses = []
        pattern_len = len(self.search_pattern)
        
        for i in range(len(buffer) - pattern_len + 1):
            if buffer[i:i + pattern_len] == self.search_pattern:
                # Сохраняем адрес первых FF (4-й байт в последовательности)
                target_addr = i + 4
                pattern_addresses.append(target_addr)
                print(f"  Найдена последовательность по адресу 0x{i:05X}, байты FF FF по адресу 0x{target_addr:06X}")
        
        return pattern_addresses

    def check_immobilizer_address(self, buffer: bytearray, addr) -> bool:
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

        for addr in pattern_addresses:
            if self.check_immobilizer_address(buffer, addr):
                return super().check(buffer)
        
        return False

    def encode(self, buffer: bytearray):
        if len(buffer) != self.size_min:
            print(f"Ошибка: неверный размер буфера {len(buffer)} байт (ожидается {self.size_min})")
            return

        print("Поиск последовательности байт A0 00 02 00 FF FF...")
        pattern_addresses = self.find_pattern_addresses(buffer)

        if not pattern_addresses:
            print("Ошибка: последовательность байт не найдена!")
            print("Файл не подходит для данного патча.")
            return

        print(f"Найдено {len(pattern_addresses)} вхождений последовательности")
        print("Применение патча по найденным адресам...")

        patched_count = 0

        for addr in pattern_addresses:
            if self.check_immobilizer_address(buffer, addr):
                old_bytes = buffer[addr:addr + 2]
                buffer[addr] = self.new_value[0]
                buffer[addr + 1] = self.new_value[1]
                print(f"  Адрес 0x{addr:06X}: {old_bytes.hex().upper()} -> {self.new_value.hex().upper()}")
                patched_count += 1
            else:
                current = buffer[addr:addr + 2]
                print(f"  Адрес 0x{addr:06X}: пропущен (найдено {current.hex().upper()}, ожидалось FF FF)")

        if patched_count == 0:
            print("Ошибка: не найдено ни одного валидного адреса для патча!")
        else:
            print(f"\nПатч успешно применён! Изменено участков: {patched_count}")
            print("Cruise Control активирован.")
