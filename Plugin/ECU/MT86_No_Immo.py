from encoder import Encoder

class MT86_No_Immo(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = self.size_max = 1540096  # 1.5 МБ для MT86

    def check(self, buffer: bytearray) -> bool:
        return len(buffer) == self.size_min and super().check(buffer)

    def find_byte_sequence(self, buffer: bytearray, sequence: bytes) -> int:
        """
        Поиск ПЕРВОГО вхождения последовательности байтов в буфере
        Возвращает адрес первого найденного вхождения или -1 если не найдено
        """
        sequence_len = len(sequence)
        
        for i in range(len(buffer) - sequence_len + 1):
            if buffer[i:i + sequence_len] == sequence:
                return i  # Возвращаем сразу при первом найденном совпадении
                
        return -1  # Не найдено

    def encode(self, buffer: bytearray):
        # Ищем последовательность 01 00 55
        target_sequence = bytes([0x01, 0x00, 0x55])
        
        print(f"Поиск последовательности байтов: {' '.join([hex(b).upper().replace('0X', '0x') for b in target_sequence])}")
        
        # Находим ПЕРВОЕ вхождение последовательности
        found_address = self.find_byte_sequence(buffer, target_sequence)
        
        if found_address == -1:
            print("Последовательность 01 00 55 не найдена в файле")
            return
            
        print(f"Последовательность найдена по адресу: {hex(found_address).upper()}")
        
        # Показываем контекст (несколько байтов до и после)
        context_start = max(0, found_address - 5)
        context_end = min(len(buffer), found_address + 8)
        print(f"Контекст [{hex(context_start).upper()} - {hex(context_end-1).upper()}]: ", end="")
        for i in range(context_start, context_end):
            if i == found_address:
                print(f"[{hex(buffer[i]).upper().replace('0X', '0x')}]", end=" ")
            else:
                print(f"{hex(buffer[i]).upper().replace('0X', '0x')}", end=" ")
        print()
        
        # Проверяем, что первый байт действительно 0x01 перед изменением
        if buffer[found_address] == 0x01:
            old_value = buffer[found_address]
            buffer[found_address] = 0x00  # Заменяем 01 на 00
            print(f"Адрес {hex(found_address).upper()}: {hex(old_value).upper().replace('0X', '0x')} -> {hex(buffer[found_address]).upper().replace('0X', '0x')}")
            
            print(f"\nПатч успешно применён!")
            
            # Показываем результат после патчинга
            print("Результат:")
            print(f"Адрес {hex(found_address).upper()}: Последовательность теперь: ", end="")
            for i in range(3):  # Показываем 3 байта последовательности
                print(f"{hex(buffer[found_address + i]).upper().replace('0X', '0x')}", end=" ")
            print()
        else:
            print(f"Ошибка: Первый байт по адресу {hex(found_address).upper()} не равен 0x01")

    def search_and_replace_all_sequences(self, buffer: bytearray):
        """
        Альтернативный метод: поиск и замена всех последовательностей 01 00 55 на 00 00 55
        """
        original_sequence = bytes([0x01, 0x00, 0x55])
        replacement_sequence = bytes([0x00, 0x00, 0x55])
        
        print(f"Поиск и замена всех последовательностей:")
        print(f"Исходная: {' '.join([hex(b).upper().replace('0X', '0x') for b in original_sequence])}")
        print(f"Замена на: {' '.join([hex(b).upper().replace('0X', '0x') for b in replacement_sequence])}")
        
        replacements = 0
        i = 0
        
        while i <= len(buffer) - len(original_sequence):
            if buffer[i:i + len(original_sequence)] == original_sequence:
                print(f"Замена по адресу {hex(i).upper()}")
                buffer[i:i + len(replacement_sequence)] = replacement_sequence
                replacements += 1
                i += len(replacement_sequence)  # Пропускаем замененную последовательность
            else:
                i += 1
                
        print(f"Выполнено {replacements} замен")


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
            print(f"Размер файла: {len(buffer)} байт\n")
            
            # Применяем патч с поиском последовательности
            mt86_patcher.encode(buffer)
            
            # Сохраняем модифицированный файл
            with open("mt86_no_immo.bin", "wb") as f:
                f.write(buffer)
            print(f"\nМодифицированный файл сохранён как 'mt86_no_immo.bin'")
            
        else:
            print("Ошибка: Файл не соответствует формату MT86")
            
    except FileNotFoundError:
        print("Ошибка: Файл 'mt86_original.bin' не найден")
    except Exception as e:
        print(f"Ошибка: {e}")