from subclass import eeprom

class Opel_25040_Pin_Vin(eeprom):
    def __init__(self):
        super().__init__()
        self.size_min = 512
        self.size_max = 512

    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            print(f"Недопустимый размер файла: {len(buffer)} байт. Ожидается: {self.size_min}")
            return False
        if len(buffer) < 0x008B + 1:
            print("Файл слишком короткий для извлечения данных")
            return False
        return super().check(buffer)

    def encode(self, buffer: bytearray):
        # Извлечение VIN (17 байтов с адреса 0x0050)
        vin_bytes = buffer[0x0050:0x0050 + 17]
        try:
            vin = vin_bytes.decode('ascii')
            print(f"VIN: {vin}")
        except UnicodeDecodeError:
            print("Ошибка: VIN не удалось декодировать как ASCII")
            vin = "Ошибка декодирования"

        # Извлечение байтов для расчета PIN
        p1 = buffer[0x0088]
        p2 = buffer[0x0089]
        p3 = buffer[0x008A]
        p4 = buffer[0x008B]
        
        # Расшифровка первой цифры PIN
        pin1_map = {
            0x70: 2, 0x71: 3, 0x72: 0, 0x73: 1,
            0x74: 6, 0x75: 7, 0x76: 4, 0x77: 5,
            0x78: 10, 0x79: 11, 0x7A: 8, 0x7B: 9,
            0x7C: 14, 0x7D: 15, 0x7E: 12, 0x7F: 13
        }
        pin1 = pin1_map.get(p1, 0)
        
        # Расшифровка второй цифры PIN
        pin2_map = {
            0x70: 5, 0x71: 4, 0x72: 7, 0x73: 6,
            0x74: 1, 0x75: 0, 0x76: 3, 0x77: 2,
            0x78: 13, 0x79: 12, 0x7A: 15, 0x7B: 14,
            0x7C: 9, 0x7D: 8, 0x7E: 11, 0x7F: 10
        }
        pin2 = pin2_map.get(p2, 0)
        
        # Расшифровка третьей цифры PIN
        pin3_map = {
            0x70: 3, 0x71: 2, 0x72: 1, 0x73: 0,
            0x74: 7, 0x75: 6, 0x76: 5, 0x77: 4,
            0x78: 11, 0x79: 10, 0x7A: 9, 0x7B: 8,
            0x7C: 15, 0x7D: 14, 0x7E: 13, 0x7F: 12
        }
        pin3 = pin3_map.get(p3, 0)
        
        # Расшифровка четвертой цифры PIN
        pin4_map = {
            0x60: 3, 0x61: 2, 0x62: 1, 0x63: 0,
            0x64: 7, 0x65: 6, 0x66: 5, 0x67: 4,
            0x68: 11, 0x69: 10, 0x6A: 9, 0x6B: 8,
            0x6C: 15, 0x6D: 14, 0x6E: 13, 0x6F: 12
        }
        pin4 = pin4_map.get(p4, 0)
        
        # Формирование полного PIN-кода
        pin = f"{pin1}{pin2}{pin3}{pin4}"
        print(f"PIN: {pin}")
        
        # Возвращаем словарь с данными для использования в интерфейсе
        return {"VIN": vin, "PIN": pin}