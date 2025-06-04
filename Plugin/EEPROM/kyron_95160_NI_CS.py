from subclass import eeprom

class kyron_95160_NI_CS(eeprom):
    """Класс для отключения иммобилайзера Kyron 95160"""
    
    def __init__(self):
        super().__init__()
        self.size_min = 2048
        self.size_max = 2048

    def check(self, buffer: bytearray) -> bool:
        """Проверка буфера на соответствие размеру"""
        if len(buffer) != self.size_min:
            return False
        return super().check(buffer)

    def encode(self, buffer: bytearray):
        """
        Отключение иммобилайзера Kyron и обновление контрольной суммы
        """
        # Проверяем размер буфера
        if len(buffer) != self.size_min:
            print(f"Ошибка: ожидалось {self.size_min} байтов, получено {len(buffer)} байтов")
            return buffer
            
        # Сохраняем оригинальные значения иммобилайзера
        original_immo_bytes = buffer[0x480:0x488]
        print(f"Оригинальные байты иммобилайзера (0x480-0x487): {original_immo_bytes.hex().upper()}")
        
        # Сохраняем оригинальные значения с 0x488 по 0x497 (они останутся без изменений)
        original_middle_bytes = buffer[0x488:0x498]
        print(f"Байты 0x488-0x497 (останутся без изменений): {original_middle_bytes.hex().upper()}")
        
        # ШАГ 1: Отключаем иммобилайзер - устанавливаем 0x5A в позиции 0x480-0x487
        for i in range(8):
            buffer[0x480 + i] = 0x5A
            
        print("Иммобилайзер отключен: установлены байты 0x5A в 0x480-0x487")
        
        # ШАГ 2: Рассчитываем и записываем контрольную сумму
        checksum_result = self.update_checksum(buffer)
        
        print("Обновлены адреса:")
        print(f"  0x480-0x487: 5A 5A 5A 5A 5A 5A 5A 5A (иммобилайзер отключен)")
        print(f"  0x488-0x497: {buffer[0x488:0x498].hex().upper()} (без изменений)")
        print(f"  0x498-0x499: {buffer[0x498:0x49A].hex().upper()} (контрольная сумма)")
        
        return {
            "IMMO_STATUS": "ОТКЛЮЧЕН",
            "CHECKSUM_UPDATED": True,
            "CHECKSUM_VALUE": checksum_result,
            "ADDRESSES_UPDATED": ["0x480-0x487", "0x498-0x499"]
        }
    
    def calculate_checksum_16(self, buffer: bytearray, start_addr: int, end_addr: int) -> int:
        """
        Расчет 16-битной контрольной суммы для указанного диапазона адресов
        """
        checksum = 0
        for i in range(start_addr, end_addr + 1):  # включая end_addr
            if i < len(buffer):
                checksum += buffer[i]
        
        # Возвращаем младшие 16 бит
        return checksum & 0xFFFF
    
    def update_checksum(self, buffer: bytearray) -> dict:
        """
        Обновление контрольной суммы согласно алгоритму:
        1. Рассчитываем checksum-16 для диапазона 0x480-0x497
        2. Прибавляем 1 к результату  
        3. Записываем результат в 0x498-0x499 (16-битное значение, little-endian)
        """
        # Сохраняем оригинальные значения контрольной суммы
        original_0x498 = buffer[0x498]
        original_0x499 = buffer[0x499]
        
        # Временно обнуляем байты контрольной суммы для корректного расчета
        buffer[0x498] = 0x00
        buffer[0x499] = 0x00
        
        # Рассчитываем базовую контрольную сумму с 0x480 по 0x497
        base_checksum = self.calculate_checksum_16(buffer, 0x480, 0x497)
        
        # Прибавляем 1
        final_checksum = (base_checksum + 1) & 0xFFFF
        
        # Записываем результат в 0x498-0x499 (big-endian: старший байт первым)
        buffer[0x498] = (final_checksum >> 8) & 0xFF  # старший байт
        buffer[0x499] = final_checksum & 0xFF         # младший байт
        
        print(f"Базовая контрольная сумма (0x480-0x497): {hex(base_checksum).upper()}")
        print(f"Финальная контрольная сумма (+1): {hex(final_checksum).upper()}")
        print(f"Записано в 0x498 (старший байт): {hex(buffer[0x498]).upper()}")
        print(f"Записано в 0x499 (младший байт): {hex(buffer[0x499]).upper()}")
        
        return {
            "base_checksum": hex(base_checksum).upper(),
            "final_checksum": hex(final_checksum).upper(),
            "high_byte_0x498": hex(buffer[0x498]).upper(),
            "low_byte_0x499": hex(buffer[0x499]).upper()
        }
    
    def verify_checksum(self, buffer: bytearray) -> bool:
        """
        Проверка правильности контрольной суммы
        """
        # Получаем текущие значения контрольной суммы
        current_0x498 = buffer[0x498]
        current_0x499 = buffer[0x499]
        current_checksum = (current_0x498 << 8) | current_0x499  # big-endian
        
        # Временно обнуляем для расчета
        buffer[0x498] = 0x00
        buffer[0x499] = 0x00
        
        # Рассчитываем ожидаемую контрольную сумму
        calculated_base = self.calculate_checksum_16(buffer, 0x480, 0x497)
        expected_checksum = (calculated_base + 1) & 0xFFFF
        
        # Восстанавливаем оригинальные значения
        buffer[0x498] = current_0x498
        buffer[0x499] = current_0x499
        
        print(f"Текущая контрольная сумма в файле: {hex(current_checksum).upper()}")
        print(f"Ожидаемая контрольная сумма: {hex(expected_checksum).upper()}")
        
        return current_checksum == expected_checksum
    
    def get_immo_status(self, buffer: bytearray) -> str:
        """Получение статуса иммобилайзера"""
        immo_position = 0x480
        immo_bytes = buffer[immo_position:immo_position+8]
        
        if all(b == 0xA6 for b in immo_bytes):
            return "АКТИВЕН (A6)"
        elif all(b == 0x5A for b in immo_bytes):
            return "ОТКЛЮЧЕН (5A)"
        elif all(b == 0xA5 for b in immo_bytes):
            return "ОТКЛЮЧЕН (A5)"
        else:
            return f"НЕИЗВЕСТЕН ({immo_bytes.hex().upper()})"