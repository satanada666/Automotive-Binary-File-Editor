from dash_editor import DashEditor

class Chevrolet_lacetti_2007_2013_dash_denso_93c46(DashEditor):
    """Редактор одометра для Chevrolet Lacetti DASH Denso 93c46 (2007-2013)"""

    def __init__(self):
        super().__init__()
        self.size_min = 128
        self.size_max = 128
        self.data = None

    def check(self, buffer: bytearray) -> bool:
        """Проверка корректности размера буфера."""
        return super().check(buffer)

    def decode_mileage(self, encoded: bytes) -> int:
        """Декодирует пробег из 4 байт, исключая 0xFF, с XOR и перестановкой."""
        if len(encoded) != 4:
            print(f"decode_mileage: Ошибка: ожидается 4 байта, получено {len(encoded)}")
            return 0

        print(f"decode_mileage: Исходные байты = {[hex(b) for b in encoded]}")

        # Исключаем байты с 0xFF
        filtered_bytes = [b for b in encoded if b != 0xFF]
        print(f"decode_mileage: После исключения 0xFF = {[hex(b) for b in filtered_bytes]}")

        # Убедимся, что у нас ровно 3 байта
        if len(filtered_bytes) != 3:
            print(f"decode_mileage: Ошибка: после фильтрации ожидается 3 байта, получено {len(filtered_bytes)}")
            return 0

        # Переставляем байты в порядке [2, 0, 1]
        reordered_bytes = [filtered_bytes[2], filtered_bytes[0], filtered_bytes[1]]
        print(f"decode_mileage: После перестановки = {[hex(b) for b in reordered_bytes]}")

        # XOR каждого байта с 0xFF
        decoded = bytes([b ^ 0xFF for b in reordered_bytes])
        print(f"decode_mileage: После XOR = {[hex(b) for b in decoded]}")

        # Интерпретируем как BCD: каждый байт содержит две десятичные цифры
        mileage = 0
        for b in decoded:
            high_digit = (b >> 4) & 0x0F  # Старшая цифра
            low_digit = b & 0x0F          # Младшая цифра
            
            # Проверяем, что цифры действительно десятичные (0-9)
            if high_digit > 9 or low_digit > 9:
                print(f"decode_mileage: Ошибка: недопустимое значение BCD {high_digit}{low_digit}")
                return 0
                
            mileage = mileage * 10 + high_digit
            mileage = mileage * 10 + low_digit

        print(f"decode_mileage: Значение в BCD формате = {mileage}")

        if 0 <= mileage <= 999999:
            return mileage
        print(f"decode_mileage: Ошибка: пробег {mileage} вне диапазона 0–999999")
        return 0

    def encode_mileage(self, km: int) -> bytearray:
        """Кодирует пробег в 4 байта (3 значащих + 0xFF) с XOR и перестановкой."""
        if not 0 <= km <= 999999:
            print(f"encode_mileage: Ошибка: пробег {km} вне диапазона 0–999999")
            raise ValueError("Допустимый диапазон пробега: 0–999999 км")

        # Преобразуем пробег в строку с ведущими нулями (6 цифр)
        km_str = f"{km:06d}"
        print(f"encode_mileage: Пробег в строковом виде = {km_str}")

        # Преобразуем в BCD: каждая пара цифр в байт
        bcd_bytes = bytearray()
        for i in range(0, 6, 2):
            high_digit = int(km_str[i])
            low_digit = int(km_str[i + 1])
            byte_value = (high_digit << 4) | low_digit
            bcd_bytes.append(byte_value)
        print(f"encode_mileage: BCD байты = {[hex(b) for b in bcd_bytes]}")

        # XOR с 0xFF
        xored_bytes = bytearray([b ^ 0xFF for b in bcd_bytes])
        print(f"encode_mileage: После XOR = {[hex(b) for b in xored_bytes]}")

        # Переставляем байты в порядке [1, 2, 0] - обратный порядок от декодирования
        reordered_bytes = bytearray([xored_bytes[1], xored_bytes[2], xored_bytes[0]])
        print(f"encode_mileage: После перестановки = {[hex(b) for b in reordered_bytes]}")

        # Проверяем наличие байтов 0xFF в результате
        if 0xFF in reordered_bytes:
            print(f"encode_mileage: Предупреждение: В данных содержится 0xFF, это может вызвать проблемы")
            # Заменяем 0xFF на ближайшее значение 0xFE
            for i in range(len(reordered_bytes)):
                if reordered_bytes[i] == 0xFF:
                    reordered_bytes[i] = 0xFE
                    print(f"encode_mileage: Заменили 0xFF на 0xFE в позиции {i}")
        
        # Формируем итоговые 4 байта, добавляя 0xFF в конец
        result = bytearray(4)
        result[0] = reordered_bytes[0]
        result[1] = reordered_bytes[1]
        result[2] = reordered_bytes[2]
        result[3] = 0xFF  # Всегда добавляем 0xFF в конец
        print(f"encode_mileage: Итоговые 4 байта = {[hex(b) for b in result]}")

        return result

    def get_mileage(self, buffer: bytearray, model: str = None) -> int:
        """Извлекает пробег из буфера."""
        if not self.check(buffer):
            print("get_mileage: Ошибка: некорректный буфер")
            return 0
        self.data = bytearray(buffer)

        # Проверяем все три блока, где хранится пробег
        blocks = [(0x08, 0x0C), (0x0B, 0x0F), (0x10, 0x14)]
        mileage_values = []

        # Получаем значения пробега из всех трех блоков
        for start, end in blocks:
            odo_bytes = bytes(self.data[start:end])
            print(f"get_mileage: Проверяем блок (0x{start:02X}–0x{end-1:02X}) = {[hex(b) for b in odo_bytes]}")
            mileage = self.decode_mileage(odo_bytes)
            if mileage > 0:
                mileage_values.append(mileage)
                print(f"get_mileage: Блок (0x{start:02X}–0x{end-1:02X}) содержит пробег {mileage} км")

        # Если нет валидных значений, возвращаем 0
        if not mileage_values:
            print("get_mileage: Не найдено валидных значений пробега")
            return 0

        # Проверяем, совпадают ли значения из разных блоков
        if len(set(mileage_values)) > 1:
            print(f"get_mileage: Предупреждение: разные значения пробега: {mileage_values}")
            # Возвращаем наиболее часто встречающееся значение, или максимальное
            most_common = max(set(mileage_values), key=mileage_values.count)
            print(f"get_mileage: Выбрано значение {most_common} км как наиболее достоверное")
            return most_common
        
        print(f"get_mileage: Итоговый пробег = {mileage_values[0]}")
        return mileage_values[0]

    def update_mileage(self, buffer: bytearray, new_mileage: int, model: str = None):
        """Обновляет пробег в буфере."""
        if not self.check(buffer):
            print("update_mileage: Ошибка: некорректный буфер")
            return None
        if new_mileage is None:
            print("update_mileage: Пробег не указан, пропускаем обновление")
            return buffer
        self.data = bytearray(buffer)

        # Кодируем новый пробег
        try:
            encoded = self.encode_mileage(new_mileage)
        except ValueError as e:
            print(f"update_mileage: Ошибка кодирования: {e}")
            return None
        print(f"update_mileage: Закодированные байты = {[hex(b) for b in encoded]}")

        # Обновляем байты во всех трех блоках
        blocks = [(0x08, 0x0C), (0x0B, 0x0F), (0x10, 0x14)]
        
        for start, end in blocks:
            print(f"update_mileage: Исходные байты (0x{start:02X}–0x{end-1:02X}): {[hex(b) for b in self.data[start:end]]}")
            self.data[start:end] = encoded
            print(f"update_mileage: Обновленные байты (0x{start:02X}–0x{end-1:02X}): {[hex(b) for b in self.data[start:end]]}")

        # Проверяем результат
        test_mileage = self.get_mileage(self.data)
        print(f"update_mileage: Проверка после записи: {test_mileage} км")
        if test_mileage != new_mileage:
            print(f"update_mileage: Ошибка: записано {test_mileage}, ожидалось {new_mileage}")
            return None

        print(f"update_mileage: Успешно записан пробег {new_mileage} км в EEPROM")
        return self.data

    def encode(self, buffer: bytearray, model: str = None) -> dict:
        """Извлекает пробег и формирует результат."""
        if not self.check(buffer):
            print("encode: Ошибка: некорректный буфер")
            return {'mileage': 0, 'VIN': 'не найден', 'PIN': 'не найден'}

        mileage = self.get_mileage(buffer)
        return {
            'mileage': mileage,
            'VIN': 'не найден',
            'PIN': 'не найден'
        }