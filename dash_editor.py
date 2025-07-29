from abc import ABC, abstractmethod
from encoder import Encoder
from PyQt5.QtWidgets import QDialog

class DashEditor(Encoder, ABC):
    """Абстрактный базовый класс для редакторов DASH."""
    
    def __init__(self):
        super().__init__()
        self.data = None

    @abstractmethod
    def get_mileage(self, buffer: bytearray, model: str = None) -> int:
        """Возвращает текущий пробег в километрах."""
        pass

    @abstractmethod
    def update_mileage(self, buffer: bytearray, new_mileage: int, model: str = None):
        """Обновляет пробег в буфере."""
        pass

    @abstractmethod
    def encode(self, buffer: bytearray, model: str = None) -> dict:
        """Кодирует данные и возвращает результат."""
        pass

    def b2ui(self, data: bytes) -> int:
        """Преобразует байты в целое число (little endian)."""
        return int.from_bytes(data, "little", signed=False)

    def ui2b(self, num: int, c: int = 4) -> bytearray:
        """Преобразует целое число в байты (little endian)."""
        return bytearray(int.to_bytes(num, c, "little", signed=False))

    def odo_decode(self, data: bytes) -> str:
        """Декодирует 4 байта в строковое представление одометра."""
        if len(data) != 4:
            raise ValueError("Data must be 4 bytes")
        dec = self.b2ui(data) ^ 0xFFFFFFFF
        bin_data = self.ui2b(dec)
        bin_data.reverse()
        return bin_data.hex()

    def odo_normalize(self, odo: str) -> str:
        """Нормализует строку одометра до 8 символов."""
        if not odo.isdigit():
            raise ValueError("Odo must contain only digits")
        return "0"*(8 - len(odo)) + odo[:8]

    def odo_encode(self, odo: str) -> bytearray:
        """Кодирует строковое представление одометра в 4 байта."""
        if len(odo) != 8 or not odo.isdigit():
            raise ValueError("Odo must be 8 digits")
        num = int(odo, 10)
        hex_str = format(num, '08x')
        bin_data = bytearray.fromhex(hex_str)
        bin_data.reverse()
        dec = self.b2ui(bin_data) ^ 0xFFFFFFFF
        return self.ui2b(dec)

    def decode_mileage(self, encoded_bytes: bytes, model: str) -> int:
        """Декодирует четырёхбайтовое значение в пробег."""
        if len(encoded_bytes) != 4:
            raise ValueError("Ожидается ровно 4 байта")
        odo_hex = self.odo_decode(encoded_bytes)
        mileage_value = int(odo_hex.lstrip('0') or '0', 16)
        if not (0 <= mileage_value <= 999999):
            raise ValueError("Пробег вне допустимого диапазона")
        return mileage_value
    
    def get_field(self, buffer, address, length, decode_fn):#############
        if address + length > len(buffer):
           return "не найден"
        raw = buffer[address:address+length]
        return decode_fn(raw)
