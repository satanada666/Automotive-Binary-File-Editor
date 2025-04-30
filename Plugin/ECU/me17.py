from encoder import Encoder

class ME17_No_Immo(Encoder):
    def __init__(self):
        super().__init__()
        self.expected_sizes = {1504 * 1024, 1536 * 1024, 2048 * 1024, 2560 * 1024, 4096 * 1024}

    def check(self, buffer: bytearray) -> bool:
        if len(buffer) not in self.expected_sizes:
            print(f"Недопустимый размер файла: {len(buffer)} байт. Ожидаются: {self.expected_sizes}")
            return False

        start_offset = 0
        if len(buffer) == 1504 * 1024:
            start_offset = 0x901F0
        elif len(buffer) == 1536 * 1024:
            start_offset = 0xAD720
        elif len(buffer) == 2048 * 1024:
            start_offset = 0x012FCCD
        elif len(buffer) == 2560 * 1024:
            start_offset = 0x01263E0
        elif len(buffer) == 4096 * 1024:
            start_offset = 0x6E640 + 4

        target_sequence = bytearray([0x8B, 0x02, 0x20, 0x22])
        signature = bytearray([0x80, 0x20])
        signature_length = len(signature)
        target_length = len(target_sequence)

        if len(buffer) < start_offset + signature_length + target_length:
            print(f"Файл слишком короткий для проверки: {len(buffer)} < {start_offset + signature_length + target_length}")
            return False

        for i in range(start_offset, len(buffer) - target_length - signature_length + 1):
            if (buffer[i:i + signature_length] == signature and
                buffer[i + signature_length: i + signature_length + target_length] == target_sequence):
                return True

        print("Последовательность 0x80 0x20 0x8B 0x02 0x20 0x22 не найдена в файле")
        return False

    def encode(self, buffer: bytearray):
        start_offset = 0
        if len(buffer) == 1504 * 1024:
            start_offset = 0x901F0
        elif len(buffer) == 1536 * 1024:
            start_offset = 0xAD720
        elif len(buffer) == 2048 * 1024:
            start_offset = 0x012FCCD
        elif len(buffer) == 2560 * 1024:
            start_offset = 0x01263E0
        elif len(buffer) == 4096 * 1024:
            start_offset = 0x6E640

        target_sequence = bytearray([0x8B, 0x02, 0x20, 0x22])
        new_sequence = bytearray([0x00, 0x00, 0x82, 0x12])
        signature = bytearray([0x80, 0x20])
        signature_length = len(signature)
        target_length = len(target_sequence)

        for i in range(start_offset, len(buffer) - target_length - signature_length + 1):
            if (buffer[i:i + signature_length] == signature and
                buffer[i + signature_length: i + signature_length + target_length] == target_sequence):
                buffer[i + signature_length: i + signature_length + target_length] = new_sequence
                print(f"Патч FLASH_OFF успешно применён по адресу 0x{i + signature_length:08X}")
                return

        print("Не удалось применить патч: последовательность не найдена")