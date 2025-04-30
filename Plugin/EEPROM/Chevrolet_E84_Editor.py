from subclass import eeprom
from PyQt5.QtWidgets import QInputDialog
import re

class Chevrolet_E84_Editor(eeprom):
    def __init__(self, win=None):
        super().__init__()
        self.size_min = 512
        self.size_max = 131072
        self.vin_addresses = []
        self.win = win  # Главное окно для отображения диалога

    def check(self, buffer: bytearray) -> bool:
        if not (self.size_min <= len(buffer) <= self.size_max):
            print(f"❌ Неверный размер файла: {len(buffer)} байт")
            return False
        return super().check(buffer)

    def find_vin_candidates(self, buffer: bytearray):
        candidates = []
        for i in range(len(buffer) - 17):
            segment = buffer[i:i+17]
            try:
                vin = segment.decode('ascii')
                if re.fullmatch(r'[A-HJ-NPR-Z0-9]{17}', vin):
                    candidates.append((vin, i))
            except UnicodeDecodeError:
                continue
        return candidates

    def find_duplicate_vin(self, buffer: bytearray, vin: str):
        addresses = []
        vin_bytes = vin.encode('ascii')
        for i in range(len(buffer) - 17):
            if buffer[i:i+17] == vin_bytes:
                addresses.append(i)
                if len(addresses) == 2:
                    break
        return addresses

    def encode(self, buffer: bytearray):
        candidates = self.find_vin_candidates(buffer)

        if not candidates:
            print("❌ Не найден ни один VIN-кандидат.")
            return {"VIN": "не найден"}

        for vin, addr in candidates:
            duplicate_addrs = self.find_duplicate_vin(buffer, vin)
            if len(duplicate_addrs) == 2:
                self.vin_addresses = duplicate_addrs
                print(f"✅ Найден VIN: {vin}")
                print(f"🧭 Адреса VIN в файле: {[f'0x{a:06X}' for a in self.vin_addresses]}")
                break
        else:
            print("❌ Не найден VIN, встречающийся дважды.")
            return {"VIN": "не найден"}

        if self.win:
            vin_input, ok = QInputDialog.getText(self.win, "Введите VIN", "Новый VIN (17 символов):")
            if not ok or len(vin_input.strip()) != 17:
                print("❌ Ввод VIN отменён или некорректен.")
                return {"VIN": "не изменён"}
            new_vin = vin_input.strip().upper()
        else:
            new_vin = input("Введите новый VIN (17 символов): ").strip().upper()

        if not re.fullmatch(r'[A-HJ-NPR-Z0-9]{17}', new_vin):
            print("❌ Неверный формат VIN.")
            return {"VIN": "не изменён"}

        for addr in self.vin_addresses:
            buffer[addr:addr+17] = new_vin.encode('ascii')

        print(f"✅ VIN заменён на: {new_vin}")
        return {"VIN": new_vin}
