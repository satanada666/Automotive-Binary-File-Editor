from subclass import eeprom

class VW_Simos_4S_93C56_NI(eeprom): 
    def __init__(self):
        super().__init__()
        self.size_min = 256  # 93C56 EEPROM размер 256 байт
        self.size_max = 256

    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        return super().check(buffer)

    def encode(self, buffer: bytearray):
        if len(buffer) >= 0x0E:  # Проверяем что буфер достаточно большой
            # Данные для записи с адреса 0x6 по 0xD (8 байт)
            patch_data = bytearray([0x31, 0x31, 0x31, 0x31, 0x00, 0x00, 0x00, 0x00])
            
            # Применяем патч к буферу
            buffer[0x06:0x0E] = patch_data
            
            print("Патч успешно применён к VW Simos 4S 93C56")
            print(f"Адреса 0x06-0x0D заменены на: {' '.join(f'{b:02X}' for b in patch_data)}")
            
    def get_info(self):
        return {
            "ECU": "VW Simos 4S",
            "EEPROM": "93C56 (256 байт)",
            "Patch_Address": "0x06-0x0D",
            "Patch_Data": "31 31 31 31 00 00 00 00",
            "Description": "Замена данных с адреса 0x6 по 0xD"
        }