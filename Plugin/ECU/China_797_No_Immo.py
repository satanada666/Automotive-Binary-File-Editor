from encoder import Encoder

class China_797_No_Immo(Encoder):
    def __init__(self):
        super().__init__()
        # Поддерживаем два размера файлов: 832кб и 1024кб
        self.size_832kb = 832 * 1024  # 851968 байт
        self.size_1024kb = 1024 * 1024  # 1048576 байт
        
        # Устанавливаем минимальный и максимальный размеры
        self.size_min = self.size_832kb
        self.size_max = self.size_1024kb

    def check(self, buffer: bytearray) -> bool:
        # Проверяем, что размер файла соответствует одному из поддерживаемых
        if len(buffer) not in [self.size_832kb, self.size_1024kb]:
            print(f"Ошибка: неподдерживаемый размер файла {len(buffer)} байт")
            print(f"Поддерживаемые размеры: {self.size_832kb} байт (832кб) или {self.size_1024kb} байт (1024кб)")
            return False
        
        # Проверяем наличие сигнатуры иммобилайзера в зависимости от размера файла
        if len(buffer) == self.size_832kb:
            # Для файла 832кб проверяем адреса 0x254DE и 0x254DF
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
            # Для файла 1024кб проверяем адреса 0x24546 и 0x24547
            if len(buffer) > 0x24547:
                byte1 = buffer[0x24546]
                byte2 = buffer[0x24547]
                
                if byte1 == 0x3D and byte2 == 0x0B:
                    print(f"[Проверка 1024кб] Найдена сигнатура иммобилайзера по адресам 0x24546-0x24547: 0x{byte1:02X} 0x{byte2:02X}")
                    print("[Результат] Иммобилайзер НЕ отключен - требуется патчинг")
                    return True
                else:
                    print(f"[Проверка 1024кб] Сигнатура иммобилайзера не найдена по адресам 0x24546-0x24547: 0x{byte1:02X} 0x{byte2:02X}")
                    print("[Результат] Иммобилайзер уже отключен или файл не подходит")
                    return False
            else:
                print("Ошибка: файл слишком мал для проверки адресов")
                return False
        
        return super().check(buffer)

    def encode(self, buffer: bytearray):
        # Определяем размер файла и применяем соответствующий патч
        if len(buffer) == self.size_832kb:
            # Патч для файла 832кб
            if len(buffer) > 0x254DF:
                # Сохраняем старые значения для логирования
                old_byte1 = buffer[0x254DE]
                old_byte2 = buffer[0x254DF]
                
                # Устанавливаем новые значения
                buffer[0x254DE] = 0x0D
                buffer[0x254DF] = 0x0A
                
                print(f"[Патч 832кб] Адрес 0x254DE: было 0x{old_byte1:02X} → стало 0x0D")
                print(f"[Патч 832кб] Адрес 0x254DF: было 0x{old_byte2:02X} → стало 0x0A")
                print("Патч успешно применён к China_797 (файл 832кб)")
            else:
                print("Ошибка: файл слишком мал для применения патча")
                
        elif len(buffer) == self.size_1024kb:
            # Патч для файла 1024кб
            if len(buffer) > 0x24547:
                # Сохраняем старые значения для логирования
                old_byte1 = buffer[0x24546]
                old_byte2 = buffer[0x24547]
                
                # Устанавливаем новые значения
                buffer[0x24546] = 0x0D
                buffer[0x24547] = 0x0A
                
                print(f"[Патч 1024кб] Адрес 0x24546: было 0x{old_byte1:02X} → стало 0x0D")
                print(f"[Патч 1024кб] Адрес 0x24547: было 0x{old_byte2:02X} → стало 0x0A")
                print("Патч успешно применён к China_797 (файл 1024кб)")
            else:
                print("Ошибка: файл слишком мал для применения патча")
        else:
            print(f"Ошибка: неподдерживаемый размер файла {len(buffer)} байт")