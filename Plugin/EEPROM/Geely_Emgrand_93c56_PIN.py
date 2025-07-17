from subclass import eeprom

class Geely_Emgrand_93c56_PIN(eeprom):
    """Класс для извлечения PIN кода из EEPROM 93c56 (иммобилайзер 95040)"""

    def __init__(self):
        super().__init__()
        self.size_min = 256  # EEPROM 93c56 — 256 байт
        self.size_max = 256

    def check(self, buffer: bytearray) -> bool:
        """Проверка размера буфера"""
        if len(buffer) != self.size_min:
            return False
        return super().check(buffer)

    def encode(self, buffer: bytearray):
        """Извлечение PIN кода без изменений и вычислений контрольных сумм"""
        if len(buffer) != self.size_min:
            print(f"Ошибка: ожидалось {self.size_min} байтов, получено {len(buffer)} байтов")
            return buffer

        pin = self.calculate_login_pin(buffer)
        print(f"Извлечённый PIN код (HEX): {pin}")

        return {
            "PIN": pin if pin else "не найден",
            "VIN": "не найден"
        }

    def calculate_login_pin(self, buffer: bytearray) -> str:
        """
        Чтение PIN-кода из EEPROM по адресам 0x2C и 0x2D.
        В памяти байты идут как [low, high], но PIN нужно считать как [high, low].
        Возвращает строку HEX, например 'D5E4'.
        """
        if len(buffer) < 0x2D + 1:
            print("Ошибка чтения PIN: указанные байты вне диапазона")
            return ""

        b_low = buffer[0xDC]
        b_high = buffer[0xDD]

        pin_value = (b_high << 8) | b_low

        return f"{pin_value:04X}"  # Возвращаем HEX в верхнем регистре, 4 символа
