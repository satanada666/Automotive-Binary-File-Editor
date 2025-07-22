from encoder import Encoder

class sirius_d3_d4_NI(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 524288
        self.size_max = 524288
    
    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        return super().check(buffer)
    
    def encode(self, buffer: bytearray):
        # Проверяем, что буфер соответствует размеру
        if not self.check(buffer):
            print(f"Ошибка: размер буфера {len(buffer)} не соответствует {self.size_min} байтам")
            return
        
        # Заполняем диапазон 0x4000-0x7FFF значениями 0xFF
        # Это область хранения информации об иммобилайзере
        for address in range(0x4000, 0x8001):  # До 0x8000 не включается, что правильно для 0x7FFF
            if address <= 0x8002:  # Ограничение до 0x8001
                buffer[address] = 0xFF
            else:
                break
        
        print("Патч успешно применён к EMS3132 - иммобилайзер отключен")
        print(f"Обнулена область 0x4000-0x7FFF ({0x7FFF - 0x4000 + 1} байт)")