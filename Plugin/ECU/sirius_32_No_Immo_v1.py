from encoder import Encoder

class sirius_32_No_Immo_v1(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 262144
        self.size_max = 262144
    
    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        return super().check(buffer)
    
    def encode(self, buffer: bytearray):
        # Проверяем, что буфер соответствует размеру
        if not self.check(buffer):
            print(f"Ошибка: размер буфера {len(buffer)} не соответствует {self.size_min} байтам")
            return
        
        # Определяем адреса для заполнения значениями 0xFF
        address_ranges = [
            (0x63FC, 0x63FF),  # 000063FC - 000063FF
            (0x67FC, 0x67FF),  # 0x67FC - 0x67FF
            (0x6BFC, 0x6BFF),  # 0x6BFC - 0x6BFF
            (0x6FFC, 0x6FFF),  # 0x6FFC - 0x6FFF
            (0x73FC, 0x73FF),  # 0x73FC - 0x73FF
            (0x77FC, 0x77FF),  # 0x77FC - 0x77FF
        ]
        
        # Заполняем указанные диапазоны адресов значениями 0xFF
        total_bytes = 0
        for start_addr, end_addr in address_ranges:
            for address in range(start_addr, end_addr + 1):  # +1 чтобы включить конечный адрес
                if address < len(buffer):  # Проверяем что адрес не выходит за границы буфера
                    buffer[address] = 0xFF
                    total_bytes += 1
                else:
                    print(f"Предупреждение: адрес 0x{address:04X} выходит за границы буфера")
        
        print("Патч успешно применён к sirius_32_No_Immo_v1 - иммобилайзер отключен")
        print(f"Заполнено {total_bytes} байт в указанных диапазонах:")
        for start_addr, end_addr in address_ranges:
            print(f"  0x{start_addr:04X} - 0x{end_addr:04X}")