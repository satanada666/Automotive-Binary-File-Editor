from subclass import eeprom

class me7_1_NI_CS(eeprom):
    """Класс для работы с иммобилайзером Immo III, EEPROM 95040"""

    def __init__(self):
        super().__init__()
        self.size_min = 512  # EEPROM 95040 = 512 байт (32 страницы по 16 байт)
        self.size_max = 512

    def check(self, buffer: bytearray) -> bool:
        """Проверка размера буфера"""
        if len(buffer) != self.size_min:
            print(f"Ошибка: размер буфера {len(buffer)} байт, ожидалось {self.size_min}")
            return False
        return super().check(buffer)

    def encode(self, buffer: bytearray) -> bytearray:
        """
        Отключение иммобилайзера:
        - Принудительная установка 0x02 по адресам 0x12 и 0x22
        - Уменьшение по адресу 0x1E и 0x2E на 1 (если > 0)
        """
        if not self.check(buffer):
            return buffer

        print(f"Исходный PIN код: {self.calculate_login_pin(buffer)}")

        # Принудительно устанавливаем 0x02 по 0x12 и 0x22
        for addr in [0x12, 0x22]:
            original = buffer[addr]
            buffer[addr] = 0x02
            print(f"Установлен байт 0x{addr:02X}: {original:02X} → 02")

        # Уменьшаем 0x1E и 0x2E
        for addr in [0x1E, 0x2E]:
            original = buffer[addr]
            if buffer[addr] > 0:
                buffer[addr] = (buffer[addr] - 1) & 0xFF
                print(f"Изменён байт 0x{addr:02X}: {original:02X} → {buffer[addr]:02X}")
            else:
                print(f"Байт 0x{addr:02X} уже равен 0x00, не изменён.")

        return buffer

    def calculate_login_pin(self, buffer: bytearray) -> str:
        """
        Заглушка для извлечения PIN-кода.
        """
        pin_bytes = buffer[0x30:0x34]
        try:
            return ''.join(chr(b) for b in pin_bytes)
        except:
            return "N/A"

    def decode(self, buffer: bytearray) -> bytearray:
        """
        Пример метода decode: восстанавливаем исходные значения:
        - 0x12 и 0x22 обратно в 0xFF (если нужно — изменить логику при известном оригинале)
        - 0x1E и 0x2E увеличиваются на 1
        """
        buffer[0x12] = 0xFF
        buffer[0x22] = 0xFF
        for addr in [0x1E, 0x2E]:
            buffer[addr] = (buffer[addr] + 1) & 0xFF
        return buffer
