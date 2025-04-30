#Chevrolet_E84_Pin_Vin
from subclass import eeprom
import re

class Chevrolet_E84_Pin_Vin(eeprom):
    def __init__(self):
        super().__init__()
        self.size_min = 512
        self.size_max = 131072  # в зависимости от dump-а, EEPROM может быть больше

    def check(self, buffer: bytearray) -> bool:
        if not (self.size_min <= len(buffer) <= self.size_max):
            print(f"Неверный размер: {len(buffer)} байт. Ожидается от {self.size_min} до {self.size_max}")
            return False
        return super().check(buffer)

    def encode(self, buffer: bytearray):
        # Преобразуем в ASCII для анализа
        ascii_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in buffer)

        # Поиск 4-значных PIN-кодов
        pin_matches = [(m.group(), m.start()) for m in re.finditer(r'\b\d{4}\b', ascii_str)]

        # Поиск VIN'ов (стандартный формат: 17 символов, без I/O/Q)
        vin_matches = [(m.group(), m.start()) for m in re.finditer(r'\b[A-HJ-NPR-Z0-9]{17}\b', ascii_str)]

        # Вывод PIN-кодов
        if pin_matches:
            print("\n🔐 PIN-коды:")
            for pin, offset in pin_matches:
                print(f"  PIN: {pin} — смещение: 0x{offset:04X}")
        else:
            print("\nPIN не найден.")

        # Вывод VIN-номеров
        vins = []
        if vin_matches:
            print("\n🚗 VIN-номера:")
            for vin, offset in vin_matches:
                print(f"  VIN: {vin} — смещение: 0x{offset:04X}")
                vins.append(vin)
        else:
            print("\nVIN не найден.")

        # Вернём самый вероятный PIN и VIN (первый из найденных)
        return {
            "PIN": pin_matches[0][0] if pin_matches else "не найден",
            "VIN": vins[0] if vins else "не найден"
        }
