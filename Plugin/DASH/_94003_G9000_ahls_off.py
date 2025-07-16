from dash_editor import DashEditor

class _94003_G9000_ahls_off(DashEditor):
    def __init__(self):
        super().__init__()
        self.size_min = 2048
        self.size_max = 2048
        self.data = None

    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        return super().check(buffer)

    def encode(self, buffer: bytearray, model: str = None) -> dict:
        if not self.check(buffer):
            return {'mileage': 0, 'VIN': 'не найден', 'PIN': 'не найден'}

        # ✅ Вызов патча
        self.patch_ahls_off(buffer)

        # ✅ Чтение VIN
        vin = self.get_vin(buffer)

        return {'mileage': 0, 'VIN': vin, 'PIN': 'не найден'}

    def get_mileage(self, buffer: bytearray, model: str = None) -> int:
        """Пустая реализация, чтобы не было ошибки абстрактного класса."""
        return 0

    def update_mileage(self, buffer: bytearray, new_mileage: int, model: str = None):
        """Пустая реализация, чтобы не было ошибки абстрактного класса."""
        return buffer

    def get_vin(self, buffer: bytearray) -> str:
        """Считывание VIN по адресам 0x481–0x48A (10 байт)"""
        if len(buffer) < 0x48B:
            print("get_vin: Ошибка: буфер слишком короткий для VIN")
            return 'не найден'

        vin_bytes = buffer[0x481:0x48B]
        vin = ''.join(chr(b) for b in vin_bytes if 32 <= b <= 126)
        print(f"get_vin: VIN-байты: {[hex(b) for b in vin_bytes]}")
        print(f"get_vin: Извлечённый VIN = '{vin}'")
        return vin if len(vin) >= 6 else 'не найден'

    def patch_ahls_off(self, buffer: bytearray):
        """Патч по адресу 0x478: устанавливаем значение 0x2F"""
        if len(buffer) > 0x479:
            print(f"До патча: buffer[0x478] = {buffer[0x478]:02X}")
            buffer[0x478] = 0x2F
            print(f"После патча: buffer[0x478] = {buffer[0x478]:02X}")
            print("Патч успешно применён к _94003_G9000_ahls_off (AHLS_OFF)")
