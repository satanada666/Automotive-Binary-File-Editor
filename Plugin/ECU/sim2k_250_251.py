from encoder import Encoder

class sim2k_250_251(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 2621440
        self.size_max = 2621440

        # Первая сигнатура (10 байт)
        self.sequence_1 = [0xFF, 0x0F, 0x09, 0xCF, 0xCE, 0x18, 0x3E, 0x04, 0xDA, 0x01]

        # Вторая сигнатура (список из двух возможных вариантов)
        self.sequence_2_variants = [
            [0x14, 0xF0, 0xDF, 0x00, 0x73, 0x80],
            [0x14, 0xF0, 0xDF, 0x00, 0x73, 0x00]
        ]

        # Часть для замены внутри второй сигнатуры (байты 3–6)
        self.sig2_replace_offset = 2
        self.expected_sig2_patch_variants = [
            [0xDF, 0x00, 0x73, 0x80],
            [0xDF, 0x00, 0x73, 0x00]
        ]
        self.new_sig2_patch = [0x3C, 0x73, 0x00, 0x00]

    def find_all_sequences(self, buffer: bytearray, sequence: list) -> list:
        """Найти все вхождения сигнатуры (включая перекрывающиеся)"""
        positions = []
        seq_len = len(sequence)
        print(f"Поиск последовательности {sequence} длиной {seq_len} байт...")
        for i in range(len(buffer) - seq_len + 1):
            if buffer[i:i + seq_len] == bytearray(sequence):
                print(f"Найдено совпадение на адресе 0x{i:06X}: {list(buffer[i:i + seq_len])}")
                positions.append(i)
        if not positions:
            print(f"Сигнатура {sequence} не найдена.")
        return positions

    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        has_seq1 = bool(self.find_all_sequences(buffer, self.sequence_1))
        has_seq2 = any(bool(self.find_all_sequences(buffer, seq)) for seq in self.sequence_2_variants)
        return has_seq1 and has_seq2 and super().check(buffer)

    def encode(self, buffer: bytearray):
        if not self.check(buffer):
            print("Ошибка: буфер не соответствует требованиям sim2k_250_251")
            print(f"Размер: {len(buffer)} байт (ожидалось: {self.size_min})")
            print("Требуется наличие обеих сигнатур.")
            return False

        patched_count = 0
        print("Применение патча sim2k_250_251...\n")

        # === Шаг 1: Первая сигнатура ===
        seq1_positions = self.find_all_sequences(buffer, self.sequence_1)
        print(f"Найдено {len(seq1_positions)} вхождений первой сигнатуры:")
        for pos in seq1_positions:
            patch_pos = pos + 9
            if buffer[patch_pos] == 0x01:
                buffer[patch_pos] = 0x00
                print(f"  Адрес 0x{patch_pos:06X}: 0x01 → 0x00")
                patched_count += 1
            else:
                print(f"  Адрес 0x{patch_pos:06X}: пропущен (0x{buffer[patch_pos]:02X} != 0x01)")

        # === Шаг 2: Вторая сигнатура (с заменой DF 00 73 80 или DF 00 73 00) ===
        total_seq2_positions = []
        for seq_idx, seq in enumerate(self.sequence_2_variants):
            seq2_positions = self.find_all_sequences(buffer, seq)
            total_seq2_positions.extend(seq2_positions)
            print(f"Найдено {len(seq2_positions)} вхождений варианта сигнатуры {seq_idx + 1}: {seq}")

        print(f"\nОбщее количество вхождений второй сигнатуры: {len(total_seq2_positions)}")
        for pos in total_seq2_positions:
            patch_start = pos + self.sig2_replace_offset
            old_bytes = list(buffer[patch_start:patch_start + 4])
            print(f"Проверка адреса 0x{patch_start:06X}: найдено {old_bytes}")
            if old_bytes in self.expected_sig2_patch_variants:
                buffer[patch_start:patch_start + 4] = bytearray(self.new_sig2_patch)
                for i in range(4):
                    print(f"  Адрес 0x{patch_start + i:06X}: 0x{old_bytes[i]:02X} → 0x{self.new_sig2_patch[i]:02X}")
                patched_count += 4
            else:
                print(f"  Пропущено: в сигнатуре по адресу 0x{patch_start:06X} байты {old_bytes} не совпадают с {self.expected_sig2_patch_variants}")

        # Проверка содержимого буфера после патча
        print("\nСодержимое буфера после патча:")
        for pos in total_seq2_positions:
            patch_start = pos + self.sig2_replace_offset
            print(f"Адрес 0x{patch_start:06X}: {list(buffer[patch_start:patch_start + 4])}")

        if patched_count == 0:
            print("\nОшибка: ни один патч не был применён. Проверьте сигнатуры в буфере.")
            return False

        print(f"\nПатч успешно применён.")
        print(f"Всего изменено байт: {patched_count}")
        print("Иммобилайзер отключен.")
        return True