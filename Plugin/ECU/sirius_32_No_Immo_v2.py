from encoder import Encoder

class sirius_32_No_Immo_v2(Encoder):
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
        
        # Заполняем диапазон 0x6000-0x77FF значениями 0xFF
        # Это область хранения информации об иммобилайзере
        start_addr = 0x6000
        end_addr = 0x77FF
        
        for address in range(start_addr, end_addr + 1):  # +1 чтобы включить конечный адрес 0x77FF
            if address < len(buffer):  # Проверяем что адрес не выходит за границы буфера
                buffer[address] = 0xFF
            else:
                print(f"Предупреждение: адрес 0x{address:04X} выходит за границы буфера")
                break
        
        bytes_filled = end_addr - start_addr + 1
        print("Патч успешно применён к sirius_32_No_Immo_v2 - иммобилайзер отключен")
        print(f"Заполнена область 0x{start_addr:04X}-0x{end_addr:04X} ({bytes_filled} байт)")