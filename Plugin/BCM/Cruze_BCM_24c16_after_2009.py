from dash_editor import DashEditor
from collections import Counter

class Cruze_BCM_24c16_after_2009(DashEditor):
    """Редактор одометра для автомобиля Chevrolet Cruze с EEPROM 24C16 выпущенного после 2009 года"""

    def __init__(self):
        super().__init__()
        self.size_min = 2048  # Размер файла 24C16
        self.size_max = 2048
        self.data = None
        # Адреса, по которым хранится значение пробега
        self.mileage_addresses = [0xF7, 0x166, 0x1C4]
        # Адреса для VIN и PIN
        self.vin_address = 0x1E8 
        self.vin_length = 17
        self.pin_address = 0xA7 
        self.pin_length = 4

    def check(self, buffer: bytearray) -> bool:
        """Проверка корректности размера буфера."""
        if len(buffer) < self.size_min or len(buffer) > self.size_max:
            print(f"check: Ошибка: размер буфера {len(buffer)} не в диапазоне {self.size_min}–{self.size_max}")
            return False
        return super().check(buffer)

    def decode_mileage(self, encoded: bytes) -> int:
        """Декодирует пробег из 4 байт, используя только байты 1 и 2 в little-endian."""
        if len(encoded) != 4:
            print(f"decode_mileage: Ошибка: ожидается 4 байта, получено {len(encoded)}")
            return 0

        print(f"decode_mileage: Исходные байты = {[hex(b) for b in encoded]}")
        
        value = int.from_bytes(encoded[1:3], byteorder='little')
        print(f"decode_mileage: Значение = {value}")
        
        mileage = value * 4
        print(f"decode_mileage: Пробег = {mileage} км")

        if 0 <= mileage <= 999999:
            return mileage
        print(f"decode_mileage: Ошибка: пробег {mileage} вне диапазона 0–999999")
        return 0

    def encode_mileage(self, km: int) -> bytearray:
        """Кодирует пробег в 4 байта, сохраняя 0x80 и 0x00."""
        if not 0 <= km <= 999999:
            print(f"encode_mileage: Ошибка: пробег {km} вне диапазона 0–999999")
            raise ValueError("Допустимый диапазон пробега: 0–999999 км")

        print(f"encode_mileage: Кодируем пробег {km} км")
        
        value = int(km / 4)
        raw_bytes = bytearray(value.to_bytes(2, byteorder='little'))
        encoded = bytearray([0x80, raw_bytes[0], raw_bytes[1], 0x00])
        print(f"encode_mileage: Закодированные байты = {[hex(b) for b in encoded]}")
        
        return encoded

    def get_vin_at_address(self, buffer: bytearray, address: int) -> tuple:
        """Извлекает VIN по указанному адресу."""
        if address + self.vin_length > len(buffer):
            print(f"get_vin_at_address: Ошибка: адрес 0x{address:X} выходит за пределы буфера")
            return "не найден", address
        
        vin_bytes = buffer[address:address + self.vin_length]
        print(f"get_vin_at_address: Байты VIN (0x{address:X}–0x{address+self.vin_length-1:X}) = {[hex(b) for b in vin_bytes]}")
        
        vin = ''.join(chr(b) for b in vin_bytes if 32 <= b <= 126)
        print(f"get_vin_at_address: Найден VIN = {vin}")
        
        if len(vin) != self.vin_length or not all(c.isalnum() for c in vin):
            print(f"get_vin_at_address: Некорректный VIN: {vin} (длина={len(vin)}, алфанумерический={all(c.isalnum() for c in vin)})")
            return "не найден", address
        
        return vin, address

    def get_pin_at_address(self, buffer: bytearray, address: int) -> tuple:
        """Извлекает PIN по указанному адресу."""
        if address + self.pin_length > len(buffer):
            print(f"get_pin_at_address: Ошибка: адрес 0x{address:X} выходит за пределы буфера")
            return "не найден", address
        
        pin_bytes = buffer[address:address + self.pin_length]
        print(f"get_pin_at_address: Байты PIN (0x{address:X}–0x{address+self.pin_length-1:X}) = {[hex(b) for b in pin_bytes]}")
        
        pin = ''.join(chr(b) for b in pin_bytes if 48 <= b <= 57)
        print(f"get_pin_at_address: Найден PIN = {pin}")
        
        if len(pin) != self.pin_length or not pin.isdigit():
            print(f"get_pin_at_address: Некорректный PIN: {pin} (длина={len(pin)}, только цифры={pin.isdigit()})")
            return "не найден", address
        
        return pin, address

    def get_vin(self, buffer: bytearray) -> str:
        """Извлекает VIN по заданному адресу."""
        if not self.check(buffer):
            print("get_vin: Ошибка: некорректный буфер")
            return "не найден"
        
        vin, addr = self.get_vin_at_address(buffer, self.vin_address)
        print(f"get_vin: VIN = {vin}")
        return vin

    def get_pin(self, buffer: bytearray) -> str:
        """Извлекает PIN по заданному адресу."""
        if not self.check(buffer):
            print("get_pin: Ошибка: некорректный буфер")
            return "не найден"
        
        pin, addr = self.get_pin_at_address(buffer, self.pin_address)
        print(f"get_pin: PIN = {pin}")
        return pin

    def get_mileage(self, buffer: bytearray, model: str = None) -> int:
        """Извлекает пробег из буфера."""
        if not self.check(buffer):
            print("get_mileage: Ошибка: некорректный буфер")
            return 0
        self.data = bytearray(buffer)

        mileage_values = []
        for addr in self.mileage_addresses:
            if addr + 4 > len(buffer):
                print(f"get_mileage: Ошибка: адрес 0x{addr:X} выходит за пределы буфера")
                continue
                
            odo_bytes = bytes(self.data[addr:addr+4])
            print(f"get_mileage: Проверяем блок (0x{addr:X}–0x{addr+3:X}) = {[hex(b) for b in odo_bytes]}")
            mileage = self.decode_mileage(odo_bytes)
            if mileage > 0:
                mileage_values.append(mileage)
                print(f"get_mileage: Блок (0x{addr:X}–0x{addr+3:X}) содержит пробег {mileage} км")

        if not mileage_values:
            print("get_mileage: Не найдено валидных значений пробега")
            return 0

        if len(set(mileage_values)) > 1:
            print(f"get_mileage: Предупреждение: разные значения пробега: {mileage_values}")
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

        try:
            encoded = self.encode_mileage(new_mileage)
        except ValueError as e:
            print(f"update_mileage: Ошибка кодирования: {e}")
            return None
        print(f"update_mileage: Закодированные байты = {[hex(b) for b in encoded]}")

        for addr in self.mileage_addresses:
            if addr + 4 > len(buffer):
                print(f"update_mileage: Ошибка: адрес 0x{addr:X} выходит за пределы буфера")
                continue
                
            print(f"update_mileage: Исходные байты (0x{addr:X}–0x{addr+3:X}): {[hex(b) for b in self.data[addr:addr+4]]}")
            self.data[addr:addr+4] = encoded
            print(f"update_mileage: Обновленные байты (0x{addr:X}–0x{addr+3:X}): {[hex(b) for b in self.data[addr:addr+4]]}")

        test_mileage = self.get_mileage(self.data)
        print(f"update_mileage: Проверка после записи: {test_mileage} км")
        if test_mileage != new_mileage:
            print(f"update_mileage: Ошибка: записано {test_mileage}, ожидалось {new_mileage}")
            return None

        print(f"update_mileage: Успешно записан пробег {new_mileage} км в EEPROM")
        return self.data

    def encode(self, buffer: bytearray, model: str = None) -> dict:
        """Извлекает пробег, VIN и PIN и формирует результат."""
        if not self.check(buffer):
            print("encode: Ошибка: некорректный буфер")
            return {'mileage': 0, 'VIN': 'не найден', 'PIN': 'не найден'}

        mileage = self.get_mileage(buffer)
        vin = self.get_vin(buffer)
        pin = self.get_pin(buffer)
        
        print(f"encode: Результат = {{'mileage': {mileage}, 'VIN': '{vin}', 'PIN': '{pin}'}}")
        return {
            'mileage': mileage,
            'VIN': vin,
            'PIN': pin
        }