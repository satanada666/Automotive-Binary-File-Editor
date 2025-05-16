from dash_editor import DashEditor
from collections import Counter

class Chevrolet_lacetti_dash_denso_96804358_EJ_6H21_11000_932900D_93c46(DashEditor):
    """Редактор для Chevrolet Lacetti DASH Denso 93c46."""
    
    def __init__(self):
        super().__init__()
        self.size_min = 128
        self.size_max = 128
        self.data = None

    def check(self, buffer: bytearray) -> bool:
        """Проверка буфера на соответствие формату EEPROM 93c46."""
        print(f"check: Тип буфера = {type(buffer)}, Длина буфера = {len(buffer) if buffer else 'None'}")
        print(f"check: Первые 16 байт = {[hex(b) for b in buffer[:16]]}")
        if not super().check(buffer):
            print(f"Ошибка: Ожидалось {self.size_min} байт, получено {len(buffer)} байт")
            return False
        print("check: Размер буфера корректен")
        return True

    def b2ui(self, data: bytes) -> int:
        """Преобразует байты в целое число (little endian)"""
        return int.from_bytes(data, "little", signed=False)

    def ui2b(self, num: int, c=4) -> bytearray:
        """Преобразует целое число в байты (little endian)"""
        return bytearray(int.to_bytes(num, c, "little", signed=False))
        
    def odo_decode(self, data: bytes) -> str:
        """Декодирует 4 байта в строковое представление одометра."""
        if len(data) != 4:
            raise ValueError("data must be 4 bytes")
        dec = self.b2ui(data) ^ 0xFFFFFFFF
        bin = self.ui2b(dec)
        bin.reverse()
        return bin.hex()

    def odo_normalize(self, odo: str) -> str:
        """Нормализует строку одометра до 8 символов"""
        odo = "0"*(8 - len(odo)) + odo
        return odo[0:8]
        
    def odo_encode(self, odo: str) -> bytearray:
        """Кодирует строковое представление одометра в 4 байта."""
        if len(odo) != 8:
            raise ValueError("odo must be 8 characters")
        if not all(c in '0123456789' for c in odo):
            raise ValueError("odo must contain only digits 0-9")
        bin = bytearray().fromhex(odo)
        bin.reverse()
        dec = self.b2ui(bin) ^ 0xFFFFFFFF
        return self.ui2b(dec)

    def decode_mileage(self, encoded_bytes: bytearray, model: str) -> int:
        """Декодирует четырёхбайтовое значение в пробег."""
        if len(encoded_bytes) != 4:
            raise ValueError("Ожидается ровно 4 байта")
            
        print(f"decode_mileage: Закодированные байты = {[hex(b) for b in encoded_bytes]}")
        
        odo_hex = self.odo_decode(bytes(encoded_bytes))
        print(f"decode_mileage: Декодированное шестнадцатеричное значение = {odo_hex}")
        
        cleaned_hex = odo_hex.lstrip('0')
        mileage_value = int(cleaned_hex) if cleaned_hex else 0
        
        print(f"decode_mileage: Итоговый пробег (км) = {mileage_value}")
        
        if mileage_value < 0 or mileage_value > 999999:
            print("decode_mileage: Пробег вне допустимого диапазона")
            raise ValueError("Пробег вне допустимого диапазона")
        
        return mileage_value

    def get_mileage(self, buffer: bytearray, model: str = 'lacetti_2004') -> int:
        """Возвращает текущий пробег из буфера данных."""
        if not self.check(buffer):
            return 0
        self.data = bytearray(buffer)
        
        try:
            if model == 'lacetti_2004':
                locations = [
                    self.data[0x08:0x0C],  # 0x08-0x0B
                    self.data[0x0C:0x10],  # 0x0C-0x0F
                    self.data[0x10:0x14]   # 0x10-0x13
                ]
                locations_str = [bytes(loc).hex() for loc in locations]
                print(f"get_mileage: Значения пробега в трёх местах = {locations_str}")
                
                most_common = Counter(locations_str).most_common(1)
                if most_common[0][1] < 2:
                    print("get_mileage: Значения пробега не совпадают, берём последнее (0x10-0x13)")
                    encoded = locations[2]
                else:
                    print(f"get_mileage: Выбираем наиболее частое значение = {most_common[0][0]}")
                    encoded = bytearray.fromhex(most_common[0][0])
                
                return self.decode_mileage(encoded, model)
            elif model == 'lacetti_2007':
                encoded = self.data[0x0B:0x0F]
                return self.decode_mileage(encoded, model)
            else:
                raise ValueError("Неподдерживаемая модель")
        except Exception as e:
            print(f"Ошибка при чтении пробега: {str(e)}")
            return 0

    def update_mileage(self, buffer: bytearray, new_mileage: int, model: str = 'lacetti_2004'):
        """Обновляет пробег в буфере данных."""
        if not self.check(buffer):
            return
        self.data = bytearray(buffer)
        
        if new_mileage < 0 or new_mileage > 999999:
            print(f"Ошибка: Пробег {new_mileage} км вне допустимого диапазона (0–999999 км)")
            return
        
        decimal_value = format(new_mileage, '08d')
        encoded_bytes = self.odo_encode(decimal_value)
        
        if model == 'lacetti_2004':
            self.data[0x08:0x0C] = encoded_bytes
            self.data[0x0C:0x10] = encoded_bytes
            self.data[0x10:0x14] = encoded_bytes
            print(f"Пробег обновлён до {new_mileage} км в позициях 0x08-0x0B, 0x0C-0x0F, 0x10-0x13")
        elif model == 'lacetti_2007':
            self.data[0x0B:0x0F] = encoded_bytes
            print(f"Пробег обновлён до {new_mileage} км в позиции 0x0B-0x0E")
        else:
            raise ValueError("Неподдерживаемая модель")

    def encode(self, buffer: bytearray, model: str = 'lacetti_2004') -> dict:
        """Кодирует данные и возвращает информацию."""
        if not self.check(buffer):
            return {'mileage': 0, 'VIN': 'не найден', 'PIN': 'не найден'}
        self.data = bytearray(buffer)
        mileage = self.get_mileage(buffer, model)
        result = {
            'mileage': mileage,
            'VIN': 'не найден',
            'PIN': 'не найден'
        }
        print(f"encode: Результат = {result}")
        return result