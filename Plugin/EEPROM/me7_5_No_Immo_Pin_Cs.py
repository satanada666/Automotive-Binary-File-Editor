from subclass import eeprom

class me7_5_No_Immo_Pin_Cs(eeprom):
    """Класс для работы с иммобилайзером Immo III, код 95040"""
    
    def __init__(self):
        super().__init__()
        self.size_min = 512  # 512 байт разделены на 32 страницы
        self.size_max = 512

    def check(self, buffer: bytearray) -> bool:
        """Проверка буфера на соответствие формату иммобилайзера 95040"""
        if len(buffer) != self.size_min:
            return False
        return super().check(buffer)

    def encode(self, buffer: bytearray):
        """
        Отключение иммобилайзера, расчет PIN и обновление контрольных сумм
        """
        # Проверяем размер буфера
        if len(buffer) != self.size_min:
            print(f"Ошибка: ожидалось {self.size_min} байтов, получено {len(buffer)} байтов")
            return buffer
            
        # Сохраняем оригинальные значения для отчета
        original_value1 = buffer[0x12]  # Байт в позиции 0x12
        original_value2 = buffer[0x22]  # Байт в позиции 0x22
        
        # Рассчитываем исходный PIN код
        original_pin = self.calculate_login_pin(buffer)
        print(f"Исходный PIN код: {original_pin}")
        
        # Отключаем иммобилайзер, изменяя соответствующие байты согласно изображению
        # Изменение в строке 0x00000010 (байты 0x11 и 0x12)
        
        buffer[0x12] = 0x02  # Изменение с 01 на 02
        buffer[0x22] = 0x02  # Изменение с 01 на 02
        
        
        print(f"Иммобилайзер отключен: Байт 0x12 изменен с {original_value1:02X} на 02")
        print(f"Иммобилайзер отключен: Байт 0x22 изменен с {original_value2:02X} на 02")
        
        # Рассчитываем новый PIN код после модификаций
        new_pin = self.calculate_login_pin(buffer)
        print(f"Новый PIN код: {new_pin}")
        
        # Обновляем контрольные суммы для всех страниц
        for page in range(32):  # 32 страницы (00-1F)
            # Страницы 00 и 11 (0x0B) не имеют контрольной суммы
            if page in [0x00, 0x0B]:
                continue
                
            # Рассчитываем и обновляем контрольные суммы
            self.update_checksum(buffer, page)
            
        print("Контрольные суммы успешно обновлены для всех страниц")
        return {
            "PIN": new_pin if new_pin else "не найден",
            "VIN": "не найден"
}
    
    def calculate_login_pin(self, buffer: bytearray) -> str:
        """
        Расчет PIN-кода из байтов в позициях 32, 33, 42, 43
        Пример: 57 25 → 2557 → 9559 → 09559 = login pin
        """
        # Извлекаем байты
        b1 = buffer[0x32]
        b2 = buffer[0x33]
        b3 = buffer[0x42]
        b4 = buffer[0x43]
        if b1 ==b3 and b2 == b4:
        # Переворачиваем порядок: b2 сначала, потом b1
             pair1 = (b2<<8) | b1  # Первая пара в hex
             
        
        # Конвертируем из шестнадцатеричного в десятичный формат с добавлением "0" впереди
           
        
        # Добавляем ведущий ноль, если необходимо
             login_pin = f"{pair1:05d}"
        else:
              print("Пин не найден!!!")
              login_pin = ""
        return login_pin
    
    def update_checksum(self, buffer: bytearray, page: int) -> None:
        """
        Расчет и обновление контрольной суммы для указанной страницы
        Формула: (0xFFFF - (page# - 1)) - (сумма первых 14 байтов)
        """
        # Вычисляем первую часть: (0xFFFF - (page# - 1))
        first_part = 0xFFFF - (page - 1)
        
        # Рассчитываем сумму первых 14 байтов для этой страницы
        page_start = page * 16  # Каждая страница состоит из 16 байтов
        byte_sum = sum(buffer[page_start:page_start+14])
        
        # Рассчитываем контрольную сумму
        checksum = (first_part - byte_sum) & 0xFFFF  # Оставляем только нижние 16 бит
        
        # Обновляем последние два байта страницы (сначала младший, потом старший)
        low_byte = checksum & 0xFF
        high_byte = (checksum >> 8) & 0xFF
        
        # Записываем байты контрольной суммы
        buffer[page_start + 14] = low_byte
        buffer[page_start + 15] = high_byte
        print(f"Контрольная сумма: {low_byte,high_byte}")
        print("CS_OK")