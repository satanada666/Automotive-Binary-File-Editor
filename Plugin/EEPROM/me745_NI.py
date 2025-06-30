from subclass import eeprom

class me745_NI(eeprom): 
    def __init__(self):
        super().__init__()
        self.size_min = 4096  # 95320 EEPROM размер 4KB
        self.size_max = 4096

    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        return super().check(buffer)

    def encode(self, buffer: bytearray):
        if len(buffer) >= 0x70:
            # Заменяем данные согласно техническому заданию
            # Блок 1: 00000000-0000001F
            immo_data_1 = bytearray([
                0xFF, 0xFF, 0xFF, 0xFF, 0xBD, 0x66, 0x50, 0x3B, 0x8B, 0x0A, 0xC5, 0x78, 0x12, 0x00, 0xD5, 0x8C,
                0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x5A, 0xC4, 0xE9
            ])
            
            # Блок 2: 00000020-0000003F  
            immo_data_2 = bytearray([
                0xFF, 0xFF, 0xFF, 0xFF, 0xBD, 0x66, 0x50, 0x3B, 0x8B, 0x0A, 0xC5, 0x78, 0x12, 0x00, 0xD5, 0x8C,
                0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x5A, 0xC4, 0xE9
            ])
            
            # Блок 3: 00000040-0000006F
            immo_data_3 = bytearray([
                0x58, 0x01, 0x11, 0x11, 0x11, 0x11, 0xEE, 0xEE, 0xEE, 0xEE, 0xFF, 0x00, 0xFF, 0x00, 0xFF, 0xFF,
                0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xBB, 0xE9,
                0x58, 0x01, 0x11, 0x11, 0x11, 0x11, 0xEE, 0xEE, 0xEE, 0xEE, 0xFF, 0x00, 0xFF, 0x00, 0xFF, 0xFF
            ])
            
            # Применяем патч к буферу
            buffer[0x00:0x20] = immo_data_1
            buffer[0x20:0x40] = immo_data_2  
            buffer[0x40:0x70] = immo_data_3
            
            # Устанавливаем защиту от записи в регистре 8C
            # EEPROM write protection bit
            if len(buffer) > 0x8C:
                buffer[0x8C] |= 0x80  # Устанавливаем бит защиты записи
            
            print("Патч IMMO OFF успешно применён к Bosch ME7.4.5")
            print("ВНИМАНИЕ: Записывайте EEPROM с БЛОКИРОВКОЙ ЗАПИСИ!")
            print("EEPROM write protection установлена в регистре 0x8C")
            print("Адреса патча: 0x00-0x6F")
            
    def get_info(self):
        return {
            "ECU": "Bosch ME7.4.5",
            "EEPROM": "95320 (4KB)",
            "Function": "IMMO OFF",
            "Protection": "Write protection enabled in register 0x8C",
            "Warning": "Записывать с блокировкой записи во внешнем программаторе!"
        }