from encoder import Encoder

class BMW_MS41_No_Immo_CS(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 262144
        self.size_max = 262144

        # Адреса контрольных сумм и патча
        self.boot_checksum_addr = 0x1404E  # 2 байта (little endian)
        self.program_space_start = 0x8000
        self.program_checksum_addr = 0x3FFFE  # 4 байта (big endian)
        self.immo_patch_addr = 0x14008
        self.immo_patch_value = 0x8F

        # CRC16 таблица для boot checksum (полином 0xA001)
        self.polynomial = 0xA001
        self.crc_table = self._generate_crc_table()

    def _generate_crc_table(self):
        table = []
        for i in range(256):
            crc = i
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ self.polynomial
                else:
                    crc >>= 1
            table.append(crc & 0xFFFF)
        return table

    def calculate_boot_checksum(self, buffer: bytearray) -> int:
        start = 0x14000
        length = 0x4E
        crc = 0x0000
        for i in range(length):
            byte = buffer[start + i]
            index = (crc ^ byte) & 0xFF
            crc = ((crc >> 8) ^ self.crc_table[index]) & 0xFFFF
        return crc

    def calculate_program_checksum(self, buffer: bytearray) -> int:
        checksum = 0
        for i in range(self.program_space_start, self.program_checksum_addr, 4):
            dword = int.from_bytes(buffer[i:i + 4], 'big')
            checksum = (checksum + dword) & 0xFFFFFFFF
        return (~checksum) & 0xFFFFFFFF

    def update_program_checksum(self, buffer: bytearray):
        checksum = self.calculate_program_checksum(buffer)
        buffer[self.program_checksum_addr:self.program_checksum_addr + 4] = checksum.to_bytes(4, 'big')

    def get_immo_status(self, buffer: bytearray) -> str:
        if len(buffer) <= self.immo_patch_addr:
            return "НЕИЗВЕСТНО"
        val = buffer[self.immo_patch_addr]
        return "ОТКЛЮЧЕН" if val == self.immo_patch_value else f"АКТИВЕН (0x{val:02X})"

    def check(self, buffer: bytearray) -> bool:
        return len(buffer) == self.size_min

    def encode(self, buffer: bytearray) -> dict:
        if len(buffer) != self.size_min:
            return {"ERROR": "Неверный размер файла"}

        # 1. Применяем патч IMMO
        buffer[self.immo_patch_addr] = self.immo_patch_value

        # 2. Обновляем BOOT CRC (little endian запись)
        boot_crc = self.calculate_boot_checksum(buffer)
        buffer[self.boot_checksum_addr] = boot_crc & 0xFF
        buffer[self.boot_checksum_addr + 1] = (boot_crc >> 8) & 0xFF

        # 3. Обновляем PROGRAM CRC
        self.update_program_checksum(buffer)
        program_crc = int.from_bytes(buffer[self.program_checksum_addr:self.program_checksum_addr + 4], 'big')

        return {
            "IMMO_STATUS": "ОТКЛЮЧЕН",
            "BOOT_CHECKSUM": f"0x{boot_crc:04X}",
            "PROGRAM_CHECKSUM": f"0x{program_crc:08X}",
            "PATCH_APPLIED": True,
            "CHECKSUM_UPDATED": True
        }

    def get_checksum_status(self, buffer: bytearray) -> dict:
        if len(buffer) < self.program_checksum_addr + 4:
            return {"ERROR": "Недостаточный размер"}

        calc_boot = self.calculate_boot_checksum(buffer)
        calc_program = self.calculate_program_checksum(buffer)

        stored_boot = buffer[self.boot_checksum_addr] | (buffer[self.boot_checksum_addr + 1] << 8)
        stored_program = int.from_bytes(buffer[self.program_checksum_addr:self.program_checksum_addr + 4], 'big')

        return {
            "immo_status": self.get_immo_status(buffer),
            "boot_sector": {
                "calculated": f"0x{calc_boot:04X}",
                "stored": f"0x{stored_boot:04X}",
                "valid": calc_boot == stored_boot
            },
            "program_space": {
                "calculated": f"0x{calc_program:08X}",
                "stored": f"0x{stored_program:08X}",
                "valid": calc_program == stored_program
            }
        }
