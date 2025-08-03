from dash_editor import DashEditor

class cg100x_ahl(DashEditor):
    def __init__(self):
        super().__init__()
        self.size_min = 0x05C200  # Покрывает максимальный адрес 0x05C1C7
        self.size_max = 0x05C200
        self.data = None
        self.patches = self.load_patches()

    def load_patches(self):
        """Чтение патчей из файла differences_cg100x.txt"""
        patches = []
        try:
            with open('differences_cg100x.txt', 'r') as file:
                # Пропускаем заголовок
                next(file)
                for line in file:
                    # Разделяем строку на адрес, File1_Byte, File2_Byte
                    parts = line.strip().split()
                    if len(parts) == 3:
                        try:
                            address = int(parts[0], 16)  # Адрес в шестнадцатеричном формате
                            file2_byte = int(parts[2], 16)  # Значение File2_Byte
                            patches.append((address, file2_byte))
                        except ValueError:
                            print(f"Ошибка парсинга строки: {line.strip()}")
                            continue
        except FileNotFoundError:
            print("Ошибка: Файл differences_cg100x.txt не найден")
        except Exception as e:
            print(f"Ошибка при чтении файла: {e}")
        
        if not patches:
            print("Патчи не загружены: файл пуст или содержит ошибки")
        else:
            print(f"Загружено {len(patches)} патчей из differences_cg100x.txt")
        return patches

    def check(self, buffer: bytearray) -> bool:
        """Проверка размера буфера"""
        return len(buffer) >= self.size_min

    def encode(self, buffer: bytearray, model: str = None) -> dict:
        """Основной метод обработки буфера"""
        if not self.check(buffer):
            return {'mileage': 0, 'VIN': 'не найден', 'PIN': 'не найден'}

        self.patch_ahls_off(buffer)

        vin = self.get_vin(buffer)
        return {'mileage': 0, 'VIN': vin, 'PIN': 'не найден'}

    def get_mileage(self, buffer: bytearray, model: str = None) -> int:
        """Метод обязателен по абстрактному классу, но отключён"""
        return 0

    def update_mileage(self, buffer: bytearray, new_mileage: int, model: str = None):
        """Метод обязателен по абстрактному классу, но отключён"""
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
        """Применение патчей из differences_cg100x.txt"""
        if not self.patches:
            print("Патчи не применены: список патчей пуст")
            return

        for address, new_value in self.patches:
            if address < len(buffer):
                old_value = buffer[address]
                buffer[address] = new_value
                print(f"Патч: адрес 0x{address:06X}, старое значение 0x{old_value:02X}, новое значение 0x{new_value:02X}")
            else:
                print(f"Патч не применён: адрес 0x{address:06X} выходит за пределы буфера")
        
        print("Все патчи из differences_cg100x.txt применены")