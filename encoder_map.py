from file_editors import ME17_No_Immo, My2,  Encoder,  j34p, edc16u1, Opel_25040_Pin_Vin, mazda_95320_GR6B_57K30B, srs, dasch, eeprom, Vag_simos_2_1_No_Immo, Vag_simos_3_3_No_Immo 
from file_editors import Chevrolet_E84_Pin_Vin, Chevrolet_E84_Editor 
 # Исправлено
   # Импортируем необходимые классы редакторов из file_editors.py
  # Исправлено

# Словарь соответствия имен ECU с классами редакторов
ecu_encoder_map = {
    "EDC16U1(U34)_No_Immo": edc16u1(),
    "ME17_No_Immo": ME17_No_Immo(),
    "MED9.1": My2(),
    # Добавляем новые типы редакторов
    # "Opel_eeprom": eeprom(),  # Используем базовый класс EEPROM
    "j34p_No_Immo": j34p(),  # Используем шаблон для j34p
    # Можно добавить другие модели EEPROM с указанием подходящих шаблонов
    "Opel_25040_Pin_Vin": Opel_25040_Pin_Vin(),
    # Добавьте другие соответствия по мере необходимости
    "mazda_95320_GR6B_57K30B": mazda_95320_GR6B_57K30B(),
    "Vag_simos_2_1_No_Immo": Vag_simos_2_1_No_Immo(),
    "Vag_simos_3_3_No_Immo": Vag_simos_3_3_No_Immo(),  # Используем тот же класс для разных версий
    "Chevrolet_E84_Pin_Vin": Chevrolet_E84_Pin_Vin(),
    "Chevrolet_E84_Editor": Chevrolet_E84_Editor(),
}

# Функция для получения редактора по имени ECU
def get_encoder_for_ecu(ecu_name):
    return ecu_encoder_map.get(ecu_name, None)