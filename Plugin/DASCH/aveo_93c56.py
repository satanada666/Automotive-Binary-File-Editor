from dash_editor import DashEditor
from collections import Counter

class aveo_93c56(DashEditor):
    """Редактор для Chevrolet Aveo EEPROM 93c56."""

    def __init__(self):
        super().__init__()
        self.size_min = 256
        self.size_max = 512  # Increased max size to accommodate higher addresses
        self.data: bytearray | None = None

        # Specific addresses where mileage data is stored
        self.mileage_addresses = [
            0x08, 0x14, 0x20, 0x2C, 0x38, 0x44, 0x50, 0x5C,
            0x68, 0x74, 0x80, 0x8C, 0x98, 0xA4, 0xB0, 0xBC,
            0xC8, 0xD4, 0xE0, 0xEC, 0xF8, 0x104, 0x110, 0x11C,
            0x128, 0x134, 0x140, 0x14C
        ]
        
        # Each mileage entry is 4 bytes
        self.mileage_offsets = [(addr, addr + 4) for addr in self.mileage_addresses]
        
        # Byte order for reading mileage
        self.mileage_byte_order = [1, 0, 3, 2]

    def check(self, buffer: bytearray) -> bool:
        if not super().check(buffer) or len(buffer) < self.size_min:
            return False

        valid_blocks = 0
        for start, end in self.mileage_offsets:
            if end <= len(buffer):
                valid_blocks += 1

        return valid_blocks >= 3

    def b2ui(self, data: bytes) -> int:
        return int.from_bytes(data, "big", signed=False)

    def ui2b(self, num: int, size: int = 4) -> bytearray:
        return bytearray(num.to_bytes(size, "big", signed=False))

    def odo_decode(self, block: bytes) -> int:
        if len(block) < 4:
            raise ValueError("block must be at least 4 bytes")

        # Reorder bytes according to mileage_byte_order
        ordered = bytearray([block[i] for i in self.mileage_byte_order])
        return int(self.b2ui(ordered) * 0.1)

    def get_mileage(self, buffer: bytearray, model: str = 'Chevrolet_Aveo') -> int:
        if not self.check(buffer):
            return 0

        self.data = bytearray(buffer)
        mileages = []

        for start, end in self.mileage_offsets:
            if end > len(buffer):
                continue
                
            try:
                block = self.data[start:end]
                mileage = self.odo_decode(block)
                if 0 <= mileage <= 600_000:
                    mileages.append(mileage)
            except Exception as e:
                print(f"Error decoding mileage at offset {start}-{end}: {e}")
                continue

        if not mileages:
            return 0

        return Counter(mileages).most_common(1)[0][0]

    def update_mileage(self, buffer: bytearray, new_mileage: int, model: str = 'Chevrolet_Aveo') -> bytearray:
        """
        Updates the mileage at specific addresses in the EEPROM.
        """
        if not self.check(buffer):
            return buffer

        self.data = bytearray(buffer)
        
        # Convert mileage to raw value (multiply by 10)
        value = int(new_mileage / 0.1)
        
        # Get bytes in big endian format
        value_bytes = self.ui2b(value, 4)
        
        # Create the 4-byte mileage pattern as it should appear in the EEPROM
        # Based on the byte order [1, 0, 3, 2], we need to rearrange
        mileage_pattern = bytearray(4)
        mileage_pattern[0] = value_bytes[1]  # First byte
        mileage_pattern[1] = value_bytes[0]  # Second byte
        mileage_pattern[2] = value_bytes[3]  # Third byte
        mileage_pattern[3] = value_bytes[2]  # Fourth byte
        
        # Update all mileage blocks with the same pattern
        for address in self.mileage_addresses:
            # Only update if the address is within buffer bounds
            if address + 4 <= len(buffer):
                for i in range(4):
                    self.data[address + i] = mileage_pattern[i]

        return self.data

    def encode(self, buffer: bytearray, model: str = 'Chevrolet_Aveo') -> dict:
        if not self.check(buffer):
            return {'mileage': 0, 'VIN': 'не найден', 'PIN': 'не найден'}

        self.data = bytearray(buffer)
        mileage = self.get_mileage(self.data, model)

        return {
            'mileage': mileage,
            'VIN': 'не найден',
            'PIN': 'не найден'
        }