import os
from dash_editor import DashEditor

class cg100x_ahl(DashEditor):
    def __init__(self):
        super().__init__()
        # Абсолютный путь к .bin-файлу, который лежит в корне проекта
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        self.firmware_file = os.path.join(base_dir, "CG100X_1_8_9_0_20250723_135144_BMW_SME_Battery_Management_Module(clear).bin")

    def load_firmware(self) -> bytearray:
        """Загрузка готового файла прошивки"""
        print(f"DEBUG: Текущая рабочая директория: {os.getcwd()}")
        print(f"DEBUG: Абсолютный путь к файлу: {self.firmware_file}")
        print(f"DEBUG: Файл существует: {os.path.exists(self.firmware_file)}")
        
        try:
            with open(self.firmware_file, 'rb') as f:
                data = bytearray(f.read())
            print(f"SUCCESS: Файл загружен, размер: {len(data)} байт")
            return data
        except Exception as e:
            print(f"ERROR: Ошибка загрузки файла: {e}")
            return bytearray()

    def check(self, buffer: bytearray) -> bool:
        """Проверка что буфер не пустой"""
        return len(buffer) > 0

    def encode(self, buffer: bytearray = None, model: str = None) -> dict:
        """Загрузка прошивки и возврат VIN"""
        print("DEBUG: encode() вызван — загружаем готовую прошивку")
        
        buffer = self.load_firmware()

        if not self.check(buffer):
            print("ERROR: Файл пуст или не найден")
            return {'mileage': 0, 'VIN': 'файл не найден', 'PIN': 'не найден'}

        vin = self.get_vin(buffer)
        print(f"SUCCESS: VIN: {vin}")
        return buffer  # Возвращаем байты прошивки

    def get_mileage(self, buffer: bytearray, model: str = None) -> int:
        return 0

    def update_mileage(self, buffer: bytearray, new_mileage: int, model: str = None):
        return buffer

    def get_vin(self, buffer: bytearray) -> str:
        if len(buffer) < 0x48B:
            return 'не найден'

        vin_bytes = buffer[0x481:0x48B]
        vin = ''.join(chr(b) for b in vin_bytes if 32 <= b <= 126)
        return vin if len(vin) >= 6 else 'не найден'
