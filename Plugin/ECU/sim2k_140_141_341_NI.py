from encoder import Encoder

class sim2k_140_141_341_NI(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 2097152
        self.size_max = 2097152
        
        # Первая последовательность для поиска (10 байт)
        self.sequence_1 = [0xFF, 0xFF, 0x41, 0x82, 0x00, 0x0C, 0x39, 0x80, 0x00, 0x01]
        
        # Вторая последовательность для поиска (10 байт)
        self.sequence_2 = [0x2C, 0x09, 0x00, 0x00, 0x40, 0x82, 0x02, 0x14, 0x89, 0x8D]

    def find_sequence(self, buffer: bytearray, sequence: list) -> int:
        """Находит первое вхождение последовательности в буфере"""
        seq_len = len(sequence)
        for i in range(len(buffer) - seq_len + 1):
            if buffer[i:i+seq_len] == bytearray(sequence):
                return i
        return -1

    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False

        # Проверяем наличие ОБЕИХ последовательностей
        seq1_pos = self.find_sequence(buffer, self.sequence_1)
        seq2_pos = self.find_sequence(buffer, self.sequence_2)

        if seq1_pos == -1 or seq2_pos == -1:
            return False

        return super().check(buffer)

    def encode(self, buffer: bytearray):
        # Проверяем, что буфер соответствует требованиям
        if not self.check(buffer):
            print(f"Ошибка: буфер не соответствует требованиям sim2k_140_141_341_NI")
            print(f"Размер буфера: {len(buffer)} байт (ожидается {self.size_min})")

            # Проверка последовательностей для диагностики
            print("\nПроверка последовательностей:")

            seq1_pos = self.find_sequence(buffer, self.sequence_1)
            seq2_pos = self.find_sequence(buffer, self.sequence_2)

            if seq1_pos == -1:
                print("Первая последовательность (FF FF 41 82 00 0C 39 80 00 01): НЕ НАЙДЕНА")
            else:
                print(f"Первая последовательность найдена на позиции 0x{seq1_pos:06X}")

            if seq2_pos == -1:
                print("Вторая последовательность (2C 09 00 00 40 82 02 14 89 8D): НЕ НАЙДЕНА")
            else:
                print(f"Вторая последовательность найдена на позиции 0x{seq2_pos:06X}")

            print("Для работы требуется наличие ОБЕИХ последовательностей")
            return False

        # Поиск последовательностей
        seq1_pos = self.find_sequence(buffer, self.sequence_1)
        seq2_pos = self.find_sequence(buffer, self.sequence_2)

        if seq1_pos == -1 or seq2_pos == -1:
            print("Ошибка: одна из последовательностей не найдена, патч не может быть применён.")
            return False

        patched_count = 0
        print("Применение нового алгоритма патча для отключения иммобилайзера sim2k_140_141_341_NI...\n")
        print(f"Первая последовательность найдена на позиции 0x{seq1_pos:06X}")
        print(f"Вторая последовательность найдена на позиции 0x{seq2_pos:06X}\n")

        print("Шаг 1: Корректировка 01 -> 00")
        last_byte_pos = seq1_pos + 9
        old_value = buffer[last_byte_pos]

        if old_value == 0x01:
            buffer[last_byte_pos] = 0x00
            patched_count += 1
            print(f"  Адрес 0x{last_byte_pos:06X}: 0x{old_value:02X} -> 0x00")
        else:
            print(f"  Адрес 0x{last_byte_pos:06X}: пропущен (значение 0x{old_value:02X} != 0x01)")

        print("Шаг 2: Корректировка 40 82 -> 48 00")
        fifth_byte_pos = seq2_pos + 4
        sixth_byte_pos = seq2_pos + 5
        old_value_1 = buffer[fifth_byte_pos]
        old_value_2 = buffer[sixth_byte_pos]

        if old_value_1 == 0x40 and old_value_2 == 0x82:
            buffer[fifth_byte_pos] = 0x48
            buffer[sixth_byte_pos] = 0x00
            patched_count += 2
            print(f"  Адрес 0x{fifth_byte_pos:06X}: 0x{old_value_1:02X} -> 0x48")
            print(f"  Адрес 0x{sixth_byte_pos:06X}: 0x{old_value_2:02X} -> 0x00")
        else:
            print(f"  Адреса 0x{fifth_byte_pos:06X}-0x{sixth_byte_pos:06X}: пропущены (значения 0x{old_value_1:02X} 0x{old_value_2:02X} != 0x40 0x82)")

        print(f"\nПатч успешно применён!")
        print(f"Первая последовательность обработана на позиции 0x{seq1_pos:06X}")
        print(f"Вторая последовательность обработана на позиции 0x{seq2_pos:06X}")
        print(f"Всего изменено байт: {patched_count}")
        print("Иммобилайзер отключен.")
        return True

