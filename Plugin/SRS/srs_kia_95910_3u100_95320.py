from subclass import srs  # <-- Импорт базового класса srs

class srs_kia_95910_3u100_95320(srs):
    def __init__(self):
        super().__init__()
        self.size_min = 4096
        self.size_max = 4096

    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        return super().check(buffer)

    def encode(self, buffer: bytearray):
        # Проверка размера буфера перед операциями
        if len(buffer) < self.size_min:
            print(f"Ошибка: размер буфера ({len(buffer)}) меньше необходимого ({self.size_min})")
            return

        modified = False

        # Диапазон 0x006F - 0x019C: установить 0x00
        for addr in range(0x006F, 0x019D):
            if buffer[addr] != 0x00:
                print(f"[Изменение] 0x{addr:04X}: {buffer[addr]:02X} → 00")
                buffer[addr] = 0x00
                modified = True

        # Диапазон 0x01D0 - 0x07BF: установить 0xFF
        for addr in range(0x01D0, 0x07C0):
            if buffer[addr] != 0xFF:
                print(f"[Изменение] 0x{addr:04X}: {buffer[addr]:02X} → FF")
                buffer[addr] = 0xFF
                modified = True

        # Диапазон 0x0EB0 - 0x0F27: установить 0x00
        for addr in range(0x0EB0, 0x0F28):
            if buffer[addr] != 0x00:
                print(f"[Изменение] 0x{addr:04X}: {buffer[addr]:02X} → 00")
                buffer[addr] = 0x00
                modified = True

        if not modified:
            print("Никаких изменений не потребовалось – все данные уже в нужном виде")

        # Вызов метода encode родительского класса
        super().encode(buffer)

        print("Патч успешно применён к srs_kia_95910_3u100_95320")
