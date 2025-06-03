from encoder import Encoder

class MT86_No_Immo(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = self.size_max = 1540096  # 1.5 МБ для MT86

    def check(self, buffer: bytearray) -> bool:
        return len(buffer) == self.size_min and super().check(buffer)

    def encode(self, buffer: bytearray):
        # Адреса для отключения иммобилайзера MT86
        immo_addresses = {
            0x20020: 0x18,  # байт 18 в формате hex
            0x20021: 0x3E,  # байт 3E в формате hex
            0x30350: 0x00,  # байт 00 в формате hex
            0x30351: 0x00   # байт 00 в формате hex
        }
        
        # Проверка размера буфера
        max_address = max(immo_addresses.keys())
        if len(buffer) <= max_address:
            raise ValueError(f"Буфер слишком мал для патча MT86: требуется минимум {max_address + 1} байт")

        # Вывод значений байтов с адреса 20000 по 20019 (по аналогии)
        print("Текущие значения байтов с 20000 по 20019:")
        for i in range(0x20000, 0x20014):  # 0x20000 до 0x20013 включительно (20 байт)
            print(f"Адрес {hex(i).upper()}: {hex(buffer[i]).upper().replace('0X', '0x')}")
        
        print("\nПрименение патча для отключения иммобилайзера MT86...")
        
        # Применяем изменения для отключения иммобилайзера
        for address, value in immo_addresses.items():
            old_value = buffer[address]
            buffer[address] = value
            print(f"Адрес {hex(address).upper()}: {hex(old_value).upper().replace('0X', '0x')} -> {hex(value).upper().replace('0X', '0x')}")

        print(f"\nПатч успешно применён к MT86 (изменены байты по адресам: "
              f"{', '.join([hex(addr).upper() for addr in immo_addresses.keys()])})")
        
        # Вывод значений после изменений для проверки
        print("\nЗначения байтов после применения патча:")
        for address in immo_addresses.keys():
            print(f"Адрес {hex(address).upper()}: {hex(buffer[address]).upper().replace('0X', '0x')}")


# Пример использования
if __name__ == "__main__":
    # Создаем экземпляр класса
    mt86_patcher = MT86_No_Immo()
    
    # Пример загрузки и обработки файла
    try:
        # Загружаем файл ЭБУ
        with open("mt86_original.bin", "rb") as f:
            buffer = bytearray(f.read())
        
        # Проверяем совместимость
        if mt86_patcher.check(buffer):
            print("Файл MT86 успешно проверен")
            
            # Применяем патч
            mt86_patcher.encode(buffer)
            
            # Сохраняем модифицированный файл
            with open("mt86_no_immo.bin", "wb") as f:
                f.write(buffer)
            print("\nМодифицированный файл сохранён как 'mt86_no_immo.bin'")
            
        else:
            print("Ошибка: Файл не соответствует формату MT86")
            
    except FileNotFoundError:
        print("Ошибка: Файл 'mt86_original.bin' не найден")
    except Exception as e:
        print(f"Ошибка: {e}")