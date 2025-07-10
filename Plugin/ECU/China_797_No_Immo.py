from encoder import Encoder

class China_797_No_Immo(Encoder):
    def __init__(self):
        super().__init__()
        self.size_832kb = 832 * 1024  # 851968 байт
        self.size_1024kb = 1024 * 1024  # 1048576 байт
        self.size_min = self.size_832kb
        self.size_max = self.size_1024kb

    def check(self, buffer: bytearray) -> bool:
        if len(buffer) not in [self.size_832kb, self.size_1024kb]:
            print(f"Ошибка: неподдерживаемый размер файла {len(buffer)} байт")
            print(f"Поддерживаемые размеры: {self.size_832kb} байт (832кб) или {self.size_1024kb} байт (1024кб)")
            return False

        if len(buffer) == self.size_832kb:
            if len(buffer) > 0x254DF:
                byte1 = buffer[0x254DE]
                byte2 = buffer[0x254DF]

                if byte1 == 0x3D and byte2 == 0x0B:
                    print(f"[Проверка 832кб] Найдена сигнатура иммобилайзера по адресам 0x254DE-0x254DF: 0x{byte1:02X} 0x{byte2:02X}")
                    print("[Результат] Иммобилайзер НЕ отключен - требуется патчинг")
                    return True
                else:
                    print(f"[Проверка 832кб] Сигнатура иммобилайзера не найдена по адресам 0x254DE-0x254DF: 0x{byte1:02X} 0x{byte2:02X}")
                    print("[Результат] Иммобилайзер уже отключен или файл не подходит")
                    return False
            else:
                print("Ошибка: файл слишком мал для проверки адресов")
                return False

        elif len(buffer) == self.size_1024kb:
            if len(buffer) > 0x2454B:
                byte1_a = buffer[0x24546]
                byte2_a = buffer[0x24547]
                byte1_b = buffer[0x2454A]
                byte2_b = buffer[0x2454B]

                if byte1_a == 0x3D and byte2_a == 0x0B:
                    print(f"[Проверка 1024кб] Найдена сигнатура по 0x24546-0x24547: 0x{byte1_a:02X} 0x{byte2_a:02X}")
                    print("[Результат] Иммобилайзер НЕ отключен - требуется патчинг")
                    return True

                if byte1_b == 0x3D and byte2_b == 0x0B:
                    print(f"[Проверка 1024кб] Найдена сигнатура по 0x2454A-0x2454B: 0x{byte1_b:02X} 0x{byte2_b:02X}")
                    print("[Результат] Иммобилайзер НЕ отключен - требуется патчинг")
                    return True

                print(f"[Проверка 1024кб] Сигнатура не найдена ни по 0x24546-0x24547 (0x{byte1_a:02X} 0x{byte2_a:02X}), ни по 0x2454A-0x2454B (0x{byte1_b:02X} 0x{byte2_b:02X})")
                print("[Результат] Иммобилайзер уже отключен или файл не подходит")
                return False
            else:
                print("Ошибка: файл слишком мал для проверки адресов")
                return False

        return super().check(buffer)

    def encode(self, buffer: bytearray):
        if len(buffer) == self.size_832kb:
            if len(buffer) > 0x254DF:
                old_byte1 = buffer[0x254DE]
                old_byte2 = buffer[0x254DF]

                buffer[0x254DE] = 0x0D
                buffer[0x254DF] = 0x0A

                print(f"[Патч 832кб] Адрес 0x254DE: было 0x{old_byte1:02X} → стало 0x0D")
                print(f"[Патч 832кб] Адрес 0x254DF: было 0x{old_byte2:02X} → стало 0x0A")
                print("Патч успешно применён к China_797 (файл 832кб)")
            else:
                print("Ошибка: файл слишком мал для применения патча")

        elif len(buffer) == self.size_1024kb:
            if len(buffer) > 0x2454B:
                patched = False

                if buffer[0x24546] == 0x3D and buffer[0x24547] == 0x0B:
                    old_byte1 = buffer[0x24546]
                    old_byte2 = buffer[0x24547]
                    buffer[0x24546] = 0x0D
                    buffer[0x24547] = 0x0A
                    print(f"[Патч 1024кб] Адрес 0x24546: было 0x{old_byte1:02X} → стало 0x0D")
                    print(f"[Патч 1024кб] Адрес 0x24547: было 0x{old_byte2:02X} → стало 0x0A")
                    patched = True

                if buffer[0x2454A] == 0x3D and buffer[0x2454B] == 0x0B:
                    old_byte1 = buffer[0x2454A]
                    old_byte2 = buffer[0x2454B]
                    buffer[0x2454A] = 0x0D
                    buffer[0x2454B] = 0x0A
                    print(f"[Патч 1024кб] Адрес 0x2454A: было 0x{old_byte1:02X} → стало 0x0D")
                    print(f"[Патч 1024кб] Адрес 0x2454B: было 0x{old_byte2:02X} → стало 0x0A")
                    patched = True

                if patched:
                    print("Патч успешно применён к China_797 (файл 1024кб)")
                else:
                    print("Сигнатура не найдена — патч не применён")
            else:
                print("Ошибка: файл слишком мал для применения патча")
        else:
            print(f"Ошибка: неподдерживаемый размер файла {len(buffer)} байт")
