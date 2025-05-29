from encoder import Encoder

class Ems3120_No_Immo(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = self.size_max = 2 * 1024 * 1024  # 2 МБ

    def check(self, buffer: bytearray) -> bool:
        return len(buffer) == self.size_min and super().check(buffer)

    def encode(self, buffer: bytearray):
        # Исходный диапазон для обнуления
        start_address_1 = 0x29CAC
        end_address_1 = 0x29CB7  # включительно

        # Новые области для обнуления
        address_2 = 0x168AF9
        start_address_3 = 0x2A726
        end_address_3 = 0x2A72A  # включительно
        address_4 = 0x168AF0
        address_5 = 0x168AF9  #
    
        # Проверка размера буфера
        max_address = max(end_address_1, address_2, end_address_3, address_4, address_5)
        if len(buffer) <= max_address:
            raise ValueError(f"Буфер слишком мал для патча: требуется минимум {max_address + 1} байт")

        # Обнуляем байты в первом диапазоне (0x29CAC - 0x29CB7)
        for i in range(start_address_1, end_address_1 + 1):
            buffer[i] = 0x00

        # Обнуляем байты во втором адресе (0x168AF9)
        buffer[address_2] = 0x00
        buffer[address_4] = 0xFC
        buffer[address_5] = 0x10

        # Обнуляем байты в третьем диапазоне (0x2A726 - 0x2A72A)
        for i in range(start_address_3, end_address_3 + 1):
            buffer[i] = 0x00

        print(f"Патч успешно применён к EMS3120 (обнулены байты: "
              f"{hex(start_address_1)}-{hex(end_address_1)}, "
              f"{hex(address_2)}, "
              f"{hex(start_address_3)}-{hex(end_address_3)}),"
              f"{hex(address_4)},"
              f"{hex(address_5)}")
              

'''from encoder import Encoder

class Ems3120_No_Immo(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = self.size_max = 2 * 1024 * 1024  # 2 МБ

    def check(self, buffer: bytearray) -> bool:
        return len(buffer) == self.size_min and super().check(buffer)

    def encode(self, buffer: bytearray):
        start_address = 0x29CAC
        end_address = 0x29CB7  # включительно

        if len(buffer) <= end_address:
            raise ValueError(f"Buffer too small for patch: need at least {end_address+1} bytes")

        # Обнуляем байты с start_address до end_address включительно
        for i in range(start_address, end_address + 1):
            buffer[i] = 0x00

        print(f"Патч успешно применён к EMS3120 (обнулены байты с {hex(start_address)} по {hex(end_address)})")'''




