from dash_editor import DashEditor

class haval_m6_2023_dash_93c56(DashEditor):
    """Редактор одометра Haval M6 (2023) EEPROM 93C56, пробег в 4 байтах, но данные в младших байтах."""

    def __init__(self):
        super().__init__()
        self.size_min = 256
        self.size_max = 256
        self.data = None

    def check(self, buffer: bytearray) -> bool:
        return super().check(buffer)

    def decode_mileage(self, buffer: bytearray) -> int:
        if len(buffer) < 0x28:
            print(f"decode_mileage: Ошибка: размер буфера {len(buffer)} байт, требуется минимум 0x28")
            return 0

        # Пробег читается из 4 байт, но значимы только младшие два (inverted)
        b1 = buffer[0x24]  # старший
        b2 = buffer[0x25]
        b3 = buffer[0x26]
        b4 = buffer[0x27]  # младший

        print(f"decode_mileage: Байты = {b1:02X} {b2:02X} {b3:02X} {b4:02X}")

        # Для совместимости с 2-байтовым значением в младших байтах:
        value = (b4 << 8) | b3
        print(f"decode_mileage: Пробег = {value} км")
        return value

    def encode_mileage(self, km: int) -> tuple:
        if km > 0xFFFF:
            # Используем полные 4 байта
            print(f"encode_mileage: Значение больше 2 байт, используем 4 байта")
            byte1 = (km >> 24) & 0xFF
            byte2 = (km >> 16) & 0xFF
            byte3 = (km >> 8) & 0xFF
            byte4 = km & 0xFF
            print(f"encode_mileage: 4 байта = {byte1:02X} {byte2:02X} {byte3:02X} {byte4:02X}")
            return (byte1, byte2, byte3, byte4)
        else:
            # Используем формат 00 00 HI LO
            hi = (km >> 8) & 0xFF
            lo = km & 0xFF
            print(f"encode_mileage: 2 байта = {hi:02X} {lo:02X}, записываем как 00 00 {lo:02X} {hi:02X}")
            return (0x00, 0x00, lo, hi)

    def get_mileage(self, buffer: bytearray, model: str = None) -> int:
        if not self.check(buffer):
            return 0
        self.data = bytearray(buffer)
        return self.decode_mileage(self.data)

    def update_mileage(self, buffer: bytearray, new_mileage: int, model: str = None):
        if not self.check(buffer):
            print("update_mileage: Неверный буфер")
            return None

        if new_mileage is None:
            print("update_mileage: Пробег не задан")
            return buffer

        self.data = bytearray(buffer)

        # Получаем начальные 4 байта для пробега
        b1, b2, b3, b4 = self.encode_mileage(new_mileage)
        print(f"update_mileage: Начальный пробег {new_mileage} как: {b1:02X} {b2:02X} {b3:02X} {b4:02X}")

        # Записываем значения от 0x24 до 0x00, уменьшая пробег на 1 для каждого блока
        mileage = (b4 << 8) | b3  # Формируем 16-битное значение пробега из младших байт
        for i in range(0x24, -1, -4):  # Идем от 0x24 до 0x00 с шагом -4
            # Записываем текущее значение пробега
            self.data[i] = 0x00
            self.data[i + 1] = 0x00
            self.data[i + 2] = mileage & 0xFF  # Младший байт
            self.data[i + 3] = (mileage >> 8) & 0xFF  # Старший байт
            print(f" -> запись по адресу {i:02X}-{i+3:02X}: 00 00 {self.data[i+2]:02X} {self.data[i+3]:02X}")
            mileage -= 1  # Уменьшаем пробег на 1 для следующего блока

        # Проверка
        result = self.get_mileage(self.data)
        print(f"update_mileage: Проверка — считано {result} км")
        return self.data

    def get_vin(self, buffer: bytearray) -> str:
        if len(buffer) < 0xBF:
            return 'не найден'

        vin_bytes = buffer[0xAE:0xBF]
        vin = ''.join(chr(b) for b in vin_bytes if 32 <= b <= 126)
        return vin if len(vin) == 17 else 'не найден'

    def encode(self, buffer: bytearray, model: str = None) -> dict:
        if not self.check(buffer):
            return {'mileage': 0, 'VIN': 'не найден', 'PIN': 'не найден'}

        mileage = self.get_mileage(buffer)
        vin = self.get_vin(buffer)
        return {'mileage': mileage, 'VIN': vin, 'PIN': 'не найден'}