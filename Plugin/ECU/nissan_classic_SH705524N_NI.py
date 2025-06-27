from encoder import Encoder

class nissan_classic_SH705524N_NI(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 524288
        self.size_max = 524288
    
    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        
        # Ищем последовательность 53 48 37 30 35 35 32 34 4E в диапазоне 0x1bd0-0x1be4
        search_start = 0x1bd0
        search_end = 0x1be4
        expected_signature = bytes([0x53, 0x48, 0x37, 0x30, 0x35, 0x35, 0x32, 0x34, 0x4E])  # SH705524N
        
        # Проверяем что диапазон поиска не выходит за границы буфера
        if search_end >= len(buffer):
            return False
        
        # Ищем последовательность в указанном диапазоне
        signature_found = False
        for addr in range(search_start, search_end - len(expected_signature) + 2):
            if addr + len(expected_signature) <= len(buffer):
                if buffer[addr:addr + len(expected_signature)] == expected_signature:
                    signature_found = True
                    break
        
        if not signature_found:
            return False
        
        return super().check(buffer)
    
    def encode(self, buffer: bytearray):
        # Проверяем, что буфер соответствует требованиям
        if not self.check(buffer):
            print(f"Ошибка: буфер не соответствует требованиям nissan_classic_SH705524N_NI")
            print(f"Размер буфера: {len(buffer)} байт (ожидается {self.size_min})")
            
            # Дополнительная проверка сигнатуры для диагностики
            search_start = 0x1bd0
            search_end = 0x1be4
            expected_signature = bytes([0x53, 0x48, 0x37, 0x30, 0x35, 0x35, 0x32, 0x34, 0x4E])  # SH705524N
            
            if search_end < len(buffer):
                # Ищем последовательность в диапазоне
                signature_found = False
                found_addr = None
                for addr in range(search_start, search_end - len(expected_signature) + 2):
                    if addr + len(expected_signature) <= len(buffer):
                        if buffer[addr:addr + len(expected_signature)] == expected_signature:
                            signature_found = True
                            found_addr = addr
                            break
                
                if not signature_found:
                    print("Не процессор SH705524N !!!")
                    print(f"Поиск в диапазоне 0x{search_start:04X}-0x{search_end:04X}")
                    print(f"Ожидается последовательность: {expected_signature.hex().upper()}")
                else:
                    print(f"Сигнатура найдена по адресу 0x{found_addr:04X}")
            else:
                print(f"Невозможно проверить сигнатуру - диапазон выходит за границы буфера")
            return
        
        # Записываем 0x00 по адресу 0x73fd
        patch_address = 0x73fd
        
        if patch_address < len(buffer):
            buffer[patch_address] = 0x00
            print("Патч успешно применён к nissan_classic_SH705524N_NI")
            print(f"По адресу 0x{patch_address:04X} записано значение 0x00")
        else:
            print(f"Ошибка: адрес 0x{patch_address:04X} выходит за границы буфера")