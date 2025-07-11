from encoder import Encoder

class nissan_classic_SH705529N_NI(Encoder):
    def __init__(self):
        super().__init__()
        self.size_min = 524288
        self.size_max = 524288
    
    def check(self, buffer: bytearray) -> bool:
        if len(buffer) != self.size_min:
            return False
        
        # Ищем последовательность 53 48 37 30 35 35 32 39 4E в диапазоне 0x1bd0-0x1be4
        search_start = 0x420E
        search_end = 0x4216
        expected_signature = bytes([0x53, 0x48, 0x37, 0x30, 0x35, 0x35, 0x32, 0x39, 0x4E])  # SH705529N
        
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
            print(f"Ошибка: буфер не соответствует требованиям nissan_classic_SH705529N_NI")
            print(f"Размер буфера: {len(buffer)} байт (ожидается {self.size_min})")
            
            # Дополнительная проверка сигнатуры для диагностики
            search_start = 0x420E
            search_end = 0x4216
            expected_signature = bytes([0x53, 0x48, 0x37, 0x30, 0x35, 0x35, 0x32, 0x39, 0x4E])  # SH705529N
            
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
                    print("Не процессор SH705529N !!!")
                    print(f"Поиск в диапазоне 0x{search_start:04X}-0x{search_end:04X}")
                    print(f"Ожидается последовательность: {expected_signature.hex().upper()}")
                else:
                    print(f"Сигнатура найдена по адресу 0x{found_addr:04X}")
            else:
                print(f"Невозможно проверить сигнатуру - диапазон выходит за границы буфера")
            return
        
        # Применяем патчи по указанным адресам
        patches = {
            0x719C: 0x55,
            0x7275: 0x02,
            0xB826: 0x00,
            0xBCFC: 0x00,
            0xBCFD: 0x00,
            0xBD02: 0x00,
            0xBD03: 0x00
        }
        
        patches_applied = 0
        for patch_address, patch_value in patches.items():
            if patch_address < len(buffer):
                buffer[patch_address] = patch_value
                print(f"По адресу 0x{patch_address:04X} записано значение 0x{patch_value:02X}")
                patches_applied += 1
            else:
                print(f"Ошибка: адрес 0x{patch_address:04X} выходит за границы буфера")
        
        if patches_applied > 0:
            print(f"Патчи успешно применены к nissan_classic_SH705529N_NI !!cut pin 1 in the black connector on the dashboard!! ({patches_applied} из {len(patches)})")
        else:
            print("Не удалось применить ни одного патча")