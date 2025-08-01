from encoder import Encoder

class ME17_No_Immo(Encoder):
    def __init__(self):
        super().__init__()

    def check(self, buffer: bytearray) -> bool:
        signature = bytearray([0x80, 0x20])
        target_sequence = bytearray([0x8B, 0x02, 0x20, 0x22])
        patched_sequence = bytearray([0x00, 0x00, 0x82, 0x12])
        full_sequence = signature + target_sequence
        full_patched = signature + patched_sequence

        # Найти первое вхождение
        first_index = buffer.find(full_sequence)
        if first_index == -1:
            # Если первое оригинальное не найдено, возможно уже пропатчено
            first_patched = buffer.find(full_patched)
            if first_patched == -1:
                print("Последовательность не найдена в файле")
                return False

        print(f"1-е вхождение найдено по адресу: 0x{(first_index if first_index != -1 else first_patched):08X}")

        # Теперь ищем второе вхождение после первого
        start_search = (first_index if first_index != -1 else first_patched) + 1

        # Сначала проверяем, есть ли пропатченное 2-е вхождение
        second_patched = buffer.find(full_patched, start_search)
        if second_patched != -1:
            print(f"2-е вхождение уже пропатчено по адресу: 0x{second_patched:08X}")
            print("Иммобилайзер отключен")
            return True

        # Если пропатченного нет, ищем оригинальное 2-е для правки
        second_original = buffer.find(full_sequence, start_search)
        if second_original != -1:
            print(f"2-е вхождение найдено по адресу: 0x{second_original:08X} - требует правки")
            return True

        print("2-е вхождение не найдено после первого")
        return False

    def encode(self, buffer: bytearray):
        signature = bytearray([0x80, 0x20])
        target_sequence = bytearray([0x8B, 0x02, 0x20, 0x22])
        new_sequence = bytearray([0x00, 0x00, 0x82, 0x12])
        full_sequence = signature + target_sequence
        full_patched = signature + new_sequence

        # Найти первое вхождение
        first_index = buffer.find(full_sequence)
        if first_index == -1:
            first_patched = buffer.find(full_patched)
            if first_patched == -1:
                print("Не удалось найти первое вхождение")
                return

        # Ищем второе вхождение после первого
        start_search = (first_index if first_index != -1 else first_patched) + 1

        # Проверяем, не пропатчено ли уже 2-е вхождение
        second_patched = buffer.find(full_patched, start_search)
        if second_patched != -1:
            print("Иммобилайзер отключен - 2-е вхождение уже пропатчено")
            return

        # Ищем оригинальное 2-е вхождение для патча
        second_original = buffer.find(full_sequence, start_search)
        if second_original != -1:
            # Применяем патч ко второму вхождению
            buffer[second_original + len(signature): second_original + len(signature) + len(target_sequence)] = new_sequence
            print(f"Патч FLASH_OFF успешно применён ко 2-му вхождению по адресу 0x{second_original + len(signature):08X}")
            print("Иммобилайзер отключен")
        else:
            print("Не удалось найти 2-е вхождение для применения патча")