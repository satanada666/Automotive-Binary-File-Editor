from abc import ABC, abstractmethod
from encoder import Encoder

class DashEditor(Encoder, ABC):
    """Абстрактный базовый класс для редакторов DASH."""
    
    def __init__(self):
        super().__init__()
        self.data = None

    @abstractmethod
    def get_mileage(self, buffer: bytearray, model: str = None) -> int:
        """Возвращает текущий пробег в километрах из буфера данных."""
        pass

    @abstractmethod
    def update_mileage(self, buffer: bytearray, new_mileage: int, model: str = None):
        """Обновляет пробег в буфере данных."""
        pass

    @abstractmethod
    def encode(self, buffer: bytearray, model: str = None) -> dict:
        """Кодирует данные и возвращает результат (например, VIN, PIN, mileage)."""
        pass

    def b2ui(self, data: bytes) -> int:
        """Преобразует байты в целое число (little endian)."""
        return int.from_bytes(data, "little", signed=False)

    def ui2b(self, num: int, c=4) -> bytearray:
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
        odo = "0"*(8 - len(odo)) + odo
        return odo[0:8]
        
    def odo_encode(self, odo: str) -> bytearray:
        """Кодирует десятичное строковое представление одометра в 4 байта."""
        if len(odo) != 8:
            raise ValueError("Odo must be 8 characters")
        if not all(c in '0123456789' for c in odo):
            raise ValueError("Odo must contain only digits 0-9")
        # Преобразуем десятичную строку в байты
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
        
        print(f"decode_mileage: Закодированные байты = {[hex(b) for b in encoded_bytes]}")
        
        odo_hex = self.odo_decode(encoded_bytes)
        print(f"decode_mileage: Декодированное шестнадцатеричное значение = {odo_hex}")
        
        cleaned_hex = odo_hex.lstrip('0')
        mileage_value = int(cleaned_hex, 16) if cleaned_hex else 0
        
        print(f"decode_mileage: Итоговый пробег (км) = {mileage_value}")
        
        if mileage_value < 0 or mileage_value > 999999:
            print("decode_mileage: Пробег вне допустимого диапазона")
            raise ValueError("Пробег вне допустимого диапазона")
        
        return mileage_value