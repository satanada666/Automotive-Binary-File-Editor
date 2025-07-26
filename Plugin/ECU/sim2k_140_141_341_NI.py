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

        # Третья последовательность для поиска (10 байт)
        self.sequence_3 = [0x2C, 0x09, 0x00, 0x00, 0x40, 0x82, 0x01, 0x44, 0x89, 0x8D]

        # Четвертая последовательность для поиска (10 байт)
        self.sequence_4 = [0x00, 0x00, 0x41, 0x82, 0x00, 0x0C, 0x39, 0x80, 0x00, 0x01]
        
    def find_all_sequences(self, buffer: bytearray, sequence: list) -> list:
        """Находит ВСЕ вхождения последовательности в буфере"""
        positions = []
        seq_len = len(sequence)
        for i in range(len(buffer) - seq_len + 1):
            if buffer[i:i+seq_len] == bytearray(sequence):
                positions.append(i)
        return positions

    def find_sequence(self, buffer: bytearray, sequence: list) -> int:
        """Находит первое вхождение последовательности в буфере"""
        seq_len = len(sequence)
        for i in range(len(buffer) - seq_len + 1):
            if buffer[i:i+seq_len] == bytearray(sequence):
                return i
        return -1

    def find_closest_sequences(self, buffer: bytearray):
        """Находит ближайшие друг к другу последовательности"""
        # Ищем все вхождения каждой последовательности
        seq1_positions = self.find_all_sequences(buffer, self.sequence_1)
        seq2_positions = self.find_all_sequences(buffer, self.sequence_2)
        seq3_positions = self.find_all_sequences(buffer, self.sequence_3)
        seq4_positions = self.find_all_sequences(buffer, self.sequence_4)
        
        print(f"Найдено вхождений:")
        print(f"  Последовательность 1 (FF FF 41 82...): {len(seq1_positions)} шт. на позициях: {[hex(pos) for pos in seq1_positions]}")
        print(f"  Последовательность 2 (2C 09... 02 14): {len(seq2_positions)} шт. на позициях: {[hex(pos) for pos in seq2_positions]}")
        print(f"  Последовательность 3 (2C 09... 01 44): {len(seq3_positions)} шт. на позициях: {[hex(pos) for pos in seq3_positions]}")
        print(f"  Последовательность 4 (00 00 41 82...): {len(seq4_positions)} шт. на позициях: {[hex(pos) for pos in seq4_positions]}")
        
        # Объединяем все позиции типа sequence_1 (включая sequence_4 которая похожа)
        type1_positions = seq1_positions + seq4_positions
        # Объединяем все позиции типа sequence_2 (включая sequence_3)
        type2_positions = seq2_positions + seq3_positions
        
        if not type1_positions or not type2_positions:
            return None, None
        
        # Если найдено много вхождений, ищем самые близкие пары
        min_distance = float('inf')
        best_pos1 = None
        best_pos2 = None
        
        for pos1 in type1_positions:
            for pos2 in type2_positions:
                distance = abs(pos1 - pos2)
                if distance < min_distance:
                    min_distance = distance
                    best_pos1 = pos1
                    best_pos2 = pos2
        
        print(f"\nВыбраны ближайшие последовательности:")
        print(f"  Позиция 1: 0x{best_pos1:06X}")
        print(f"  Позиция 2: 0x{best_pos2:06X}")
        print(f"  Расстояние между ними: {min_distance} байт")
        
        return best_pos1, best_pos2

    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False

        # Проверяем наличие хотя бы одной пары последовательностей
        type1_found = (self.find_sequence(buffer, self.sequence_1) != -1 or 
                      self.find_sequence(buffer, self.sequence_4) != -1)
        type2_found = (self.find_sequence(buffer, self.sequence_2) != -1 or 
                      self.find_sequence(buffer, self.sequence_3) != -1)

        if not type1_found or not type2_found:
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
            seq3_pos = self.find_sequence(buffer, self.sequence_3)
            seq4_pos = self.find_sequence(buffer, self.sequence_4)

            if seq1_pos == -1 and seq4_pos == -1:
                print("Последовательности типа 1 (41 82 00 0C 39 80 00 01): НЕ НАЙДЕНЫ")
            if seq2_pos == -1 and seq3_pos == -1:
                print("Последовательности типа 2 (40 82 XX XX 89 8D): НЕ НАЙДЕНЫ")

            print("Для работы требуется наличие хотя бы одной пары последовательностей")
            return False

        # Находим ближайшие последовательности
        seq1_pos, seq2_pos = self.find_closest_sequences(buffer)

        if seq1_pos is None or seq2_pos is None:
            print("Ошибка: не удалось найти подходящую пару последовательностей")
            return False

        patched_count = 0
        print("\nПрименение нового алгоритма патча для отключения иммобилайзера sim2k_140_141_341_NI...\n")

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