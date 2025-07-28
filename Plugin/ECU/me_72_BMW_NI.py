from encoder import Encoder

class me_72_BMW_NI(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 524288
        self.size_max = 524288
    
    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        
        # Ищем последовательность f6 f5 32 80 db 00
        expected_signature = bytes([0xf6, 0xf5, 0x32, 0x80, 0xdb, 0x00])
        
        # Ищем последовательность во всём буфере
        signature_found = False
        self.signature_address = None
        
        for addr in range(len(buffer) - len(expected_signature)):
            if buffer[addr:addr + len(expected_signature)] == expected_signature:
                signature_found = True
                self.signature_address = addr
                break
        
        if not signature_found:
            return False
        
        return super().check(buffer)
    
    def encode(self, buffer: bytearray):
        # Проверяем, что буфер соответствует требованиям
        if not self.check(buffer):
            print(f"Ошибка: буфер не соответствует требованиям me_72_BMW_NI")
            print(f"Размер буфера: {len(buffer)} байт (ожидается {self.size_min})")
            
            # Дополнительная проверка сигнатуры для диагностики
            expected_signature = bytes([0xf6, 0xf5, 0x32, 0x80, 0xdb, 0x00])
            
            # Ищем последовательность во всём буфере
            signature_found = False
            found_addr = None
            
            for addr in range(len(buffer) - len(expected_signature)):
                if buffer[addr:addr + len(expected_signature)] == expected_signature:
                    signature_found = True
                    found_addr = addr
                    break
            
            if not signature_found:
                print("Не найдена сигнатура BMW ME 7.2 !!!")
                print(f"Ожидается последовательность: {expected_signature.hex().upper()}")
            else:
                print(f"Сигнатура найдена по адресу 0x{found_addr:04X}")
            return
        
        # Начинаем редактирование 26 байт после найденной сигнатуры
        edit_start_address = self.signature_address + 6  # 6 - длина сигнатуры f6 f5 32 80 db 00
        edit_length = 26
        
        # Проверяем, что не выходим за границы буфера
        if edit_start_address + edit_length > len(buffer):
            print(f"Ошибка: область редактирования выходит за границы буфера")
            print(f"Начальный адрес: 0x{edit_start_address:04X}, длина: {edit_length}")
            return
        
        # Заполняем 26 байт повторяющимся паттерном cc 00
        pattern = bytes([0xcc, 0x00])
        
        for i in range(edit_length):
            buffer[edit_start_address + i] = pattern[i % 2]
        
        print("Патч успешно применён к me_72_BMW_NI")
        print(f"Сигнатура найдена по адресу 0x{self.signature_address:04X}")
        print(f"Отредактировано {edit_length} байт начиная с адреса 0x{edit_start_address:04X}")
        print(f"Применён паттерн: {pattern.hex().upper()} (повторяющийся)")