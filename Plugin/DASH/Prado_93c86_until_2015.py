from dash_editor import DashEditor
from collections import Counter

class Prado_93c86_until_2015(DashEditor):
    """Редактор одометра для Toyota Prado с EEPROM 93C86"""

    def __init__(self):
        super().__init__()
        self.size_min = 2048
        self.size_max = 2048

    def check(self, buffer: bytearray) -> bool:
        return super().check(buffer)

    def decode_mileage(self, buffer: bytearray) -> int:
        if len(buffer) < 0x22:
            print("decode_mileage: Буфер слишком мал")
            return 0

        values = [(buffer[i + 1] << 8) | buffer[i] for i in range(0, 0x22, 2)]
        counter = Counter(values)
        most_common_val, count = counter.most_common(1)[0]
        mileage = most_common_val * 17

        print(f"decode_mileage: Значения = {values}")
        print(f"decode_mileage: Наиболее частое значение = 0x{most_common_val:04X} ({most_common_val}), повторов = {count}")
        print(f"decode_mileage: Пробег = {mileage} км")

        if count < len(values):
            print(f"decode_mileage: ⚠️ Предупреждение: не все копии совпадают ({count}/17)")

        return mileage

    def encode_mileage(self, km: int) -> tuple:
        """Округляет пробег и возвращает два байта (LSB, MSB)"""
        value = round(km / 17)
        lsb = value & 0xFF
        msb = (value >> 8) & 0xFF

        print(f"encode_mileage: пробег {km} -> округлённое значение {value} -> байты: {lsb:02X} {msb:02X}")
        return lsb, msb

    def get_mileage(self, buffer: bytearray, model: str = None) -> int:
        if not self.check(buffer):
            print("get_mileage: Ошибка проверки")
            return 0
        return self.decode_mileage(buffer)

    def update_mileage(self, buffer: bytearray, new_mileage: int, model: str = None):
        if not self.check(buffer):
            print("update_mileage: Ошибка проверки буфера")
            return None

        data = bytearray(buffer)
        lsb, msb = self.encode_mileage(new_mileage)

        for i in range(0, 0x22, 2):
            data[i] = lsb
            data[i + 1] = msb
            print(f"update_mileage: записано 0x{i:02X}-0x{i+1:02X} = {lsb:02X} {msb:02X}")

        test_mileage = self.get_mileage(data)
        if abs(test_mileage - new_mileage) > 8:
            print(f"update_mileage: ⚠️ Ошибка проверки: записано {test_mileage}, ожидалось {new_mileage}")
            return None

        print(f"update_mileage: ✅ Успешно обновлён пробег ≈ {test_mileage} км")
        return data

    def encode(self, buffer: bytearray, model: str = None) -> dict:
        if not self.check(buffer):
            return {'mileage': 0, 'VIN': 'не найден', 'PIN': 'не найден'}

        mileage = self.get_mileage(buffer)
        return {
            'mileage': mileage,
            'VIN': 'не найден',
            'PIN': 'не найден'
        }
