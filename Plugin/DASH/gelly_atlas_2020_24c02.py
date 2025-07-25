from dash_editor import DashEditor

class gelly_atlas_2020_24c02(DashEditor):
    """Редактор одометра для Geely Atlas 24C02 (2020+) с 4-байтовым пробегом"""

    def __init__(self):
        super().__init__()
        self.size_min = 256
        self.size_max = 256
        self.data = None

    def check(self, buffer: bytearray) -> bool:
        """Проверка корректности размера буфера."""
        return super().check(buffer)

    def decode_mileage(self, buffer: bytearray) -> int:
        """Декодирует пробег из 4 байт по адресу 0x24-0x27."""
        if len(buffer) < 0x28:
            print(f"decode_mileage: Ошибка: размер буфера {len(buffer)} байт, требуется минимум {0x28}")
            return 0

        # Считываем 4 байта по адресу 0x24-0x27
        byte1 = buffer[0x24]
        byte2 = buffer[0x25]
        byte3 = buffer[0x26]
        byte4 = buffer[0x27]
        
        print(f"decode_mileage: Байты по адресу 0x24-0x27 = 0x{byte1:02X} 0x{byte2:02X} 0x{byte3:02X} 0x{byte4:02X}")

        # Преобразуем из 16-ричного в десятичный формат
        mileage = (byte1 << 24) | (byte2 << 16) | (byte3 << 8) | byte4
        
        print(f"decode_mileage: Пробег в десятичном формате = {mileage} км")
        return mileage

    def encode_mileage(self, km: int) -> tuple:
        """Кодирует пробег из десятичного в 16-ричный формат (4 байта)."""
        if not 0 <= km <= 4294967295:  # Максимум для 4 байт
            print(f"encode_mileage: Ошибка: пробег {km} вне диапазона 0–4294967295")
            raise ValueError("Допустимый диапазон пробега: 0–4294967295 км")

        print(f"encode_mileage: Пробег для кодирования = {km} км")

        # Преобразуем десятичное значение в 4 байта
        byte1 = (km >> 24) & 0xFF  # Старший байт
        byte2 = (km >> 16) & 0xFF
        byte3 = (km >> 8) & 0xFF
        byte4 = km & 0xFF         # Младший байт
        
        print(f"encode_mileage: Закодированные байты = 0x{byte1:02X} 0x{byte2:02X} 0x{byte3:02X} 0x{byte4:02X}")
        return byte1, byte2, byte3, byte4

    def get_mileage(self, buffer: bytearray, model: str = None) -> int:
        """Извлекает пробег из буфера."""
        if not self.check(buffer):
            print("get_mileage: Ошибка: некорректный буфер")
            return 0
        
        self.data = bytearray(buffer)
        
        print(f"get_mileage: Считывание пробега по адресу 0x24-0x27")
        mileage = self.decode_mileage(self.data)
        
        print(f"get_mileage: Итоговый пробег = {mileage} км")
        return mileage

    def update_mileage(self, buffer: bytearray, new_mileage: int, model: str = None):
        """Обновляет пробег в буфере."""
        if not self.check(buffer):
            print("update_mileage: Ошибка: некорректный буфер")
            return None
        
        if new_mileage is None:
            print("update_mileage: Пробег не указан, пропускаем обновление")
            return buffer
        
        self.data = bytearray(buffer)

        # Кодируем новый пробег в 4 байта
        try:
            byte1, byte2, byte3, byte4 = self.encode_mileage(new_mileage)
        except ValueError as e:
            print(f"update_mileage: Ошибка кодирования: {e}")
            return None

        print(f"update_mileage: Записываем пробег {new_mileage} км")

        # Основной адрес записи 0x24-0x27
        print(f"update_mileage: Запись по адресу 0x24-0x27: 0x{byte1:02X} 0x{byte2:02X} 0x{byte3:02X} 0x{byte4:02X}")
        self.data[0x24] = byte1
        self.data[0x25] = byte2
        self.data[0x26] = byte3
        self.data[0x27] = byte4

        # Список адресов для записи уменьшенных значений (по 4 байта) в обратной последовательности
        addresses = [
            (0x20, 0x21, 0x22, 0x23),  # -1
            (0x1C, 0x1D, 0x1E, 0x1F),  # -2
            (0x18, 0x19, 0x1A, 0x1B),  # -3
            (0x14, 0x15, 0x16, 0x17),  # -4
            (0x10, 0x11, 0x12, 0x13),  # -5
            (0x0C, 0x0D, 0x0E, 0x0F),  # -6
            (0x08, 0x09, 0x0A, 0x0B),  # -7
            (0x04, 0x05, 0x06, 0x07),  # -8
            (0x00, 0x01, 0x02, 0x03)   # -9
        ]

        # Записываем уменьшенные значения по всем адресам
        current_value = new_mileage
        for addr1, addr2, addr3, addr4 in addresses:
            current_value -= 1
            if current_value < 0:
                current_value = 0
            
            # Кодируем уменьшенное значение
            dec_byte1 = (current_value >> 24) & 0xFF
            dec_byte2 = (current_value >> 16) & 0xFF
            dec_byte3 = (current_value >> 8) & 0xFF
            dec_byte4 = current_value & 0xFF
            
            print(f"update_mileage: Запись по адресу 0x{addr1:02X}-0x{addr4:02X}: {current_value} км (0x{dec_byte1:02X} 0x{dec_byte2:02X} 0x{dec_byte3:02X} 0x{dec_byte4:02X})")
            
            self.data[addr1] = dec_byte1
            self.data[addr2] = dec_byte2
            self.data[addr3] = dec_byte3
            self.data[addr4] = dec_byte4

        # Проверяем результат
        test_mileage = self.get_mileage(self.data)
        print(f"update_mileage: Проверка после записи: {test_mileage} км")
        
        if test_mileage != new_mileage:
            print(f"update_mileage: Ошибка: записано {test_mileage}, ожидалось {new_mileage}")
            return None

        print(f"update_mileage: Успешно записан пробег {new_mileage} км в EEPROM")
        return self.data

    def get_vin(self, buffer: bytearray) -> str:
        """Извлекает VIN номер из буфера по адресам 0xAE-0xBE."""
        if len(buffer) < 0xBF:
            print(f"get_vin: Ошибка: размер буфера {len(buffer)} байт, требуется минимум {0xBF}")
            return 'не найден'
        
        # Считываем 17 байт VIN по адресам 0xAE-0xBE
        vin_bytes = buffer[0xAE:0xBF]
        print(f"get_vin: Байты VIN по адресам 0xAE-0xBE = {[hex(b) for b in vin_bytes]}")
        
        try:
            # Преобразуем байты в строку ASCII
            vin = ''.join(chr(b) for b in vin_bytes if 32 <= b <= 126)  # Печатаемые ASCII символы
            print(f"get_vin: Извлеченный VIN = '{vin}'")
            
            # Проверяем длину VIN (должен быть 17 символов)
            if len(vin) == 17:
                return vin
            elif len(vin) > 0:
                print(f"get_vin: Предупреждение: VIN неполный, длина {len(vin)} символов")
                return vin
            else:
                print("get_vin: VIN содержит только непечатаемые символы")
                return 'не найден'
                
        except Exception as e:
            print(f"get_vin: Ошибка при декодировании VIN: {e}")
            return 'не найден'

    def encode(self, buffer: bytearray, model: str = None) -> dict:
        """Извлекает пробег, VIN и формирует результат."""
        if not self.check(buffer):
            print("encode: Ошибка: некорректный буфер")
            return {'mileage': 0, 'VIN': 'не найден', 'PIN': 'не найден'}

        mileage = self.get_mileage(buffer)
        vin = self.get_vin(buffer)
        
        return {
            'mileage': mileage,
            'VIN': vin,
            'PIN': 'не найден'
        }

