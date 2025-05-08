from encoder import Encoder
from Plugin.ECU.me17 import ME17_No_Immo
from my2 import My2

###EEPROM####
from subclass import eeprom
from Plugin.EEPROM.j34p import j34p
from Plugin.EEPROM.edc16u1 import edc16u1
from Plugin.EEPROM.opel_25040_pin_vin import Opel_25040_Pin_Vin
from Plugin.SRS.mazda_95320_GR6B_57K30B import mazda_95320_GR6B_57K30B
from Plugin.EEPROM.Vag_simos_2_1_No_Immo import Vag_simos_2_1_No_Immo
from Plugin.EEPROM.Vag_simos_3_3_No_Immo import Vag_simos_3_3_No_Immo
from Plugin.EEPROM.Chevrolet_E84_Pin_Vin import Chevrolet_E84_Pin_Vin
from Plugin.EEPROM.Chevrolet_E84_Editor import Chevrolet_E84_Editor
from Plugin.EEPROM.me7_5_No_Immo_Pin_Cs  import me7_5_No_Immo_Pin_Cs
###DASCH####  
from Plugin.DASCH.Chevrolet_lacetti_dash_denso_96804358_EJ_6H21_11000_932900D_93c46 import Chevrolet_lacetti_dash_denso_96804358_EJ_6H21_11000_932900D_93c46
from Plugin.DASCH.Daewoo_Gentra_dash_denso_93c56 import Daewoo_Gentra_dash_denso_93c56
from Plugin.DASCH.Chevrolet_lacetti_2007_2013_dash_denso_93c46 import Chevrolet_lacetti_2007_2013_dash_denso_93c46
from dash_vdo import dash_vdo
###BCM#####
from bcm_valeo import bcm_valeo

# Здесь можно создать словарь или функцию для выбора нужного кодировщика
encoders = {
    "ME17": ME17_No_Immo,
    "My2": My2,
    ###EEPROM####
    "j34p": j34p,
    "edc16u1": edc16u1,
    "Opel_25040_Pin_Vin": Opel_25040_Pin_Vin,
    "Chevrolet_E84_Pin_Vin": Chevrolet_E84_Pin_Vin,
    "Chevrolet_E84_Editor": Chevrolet_E84_Editor,
    "Vag_simos_21_No_Immo": Vag_simos_2_1_No_Immo,
    "Vag_simos_33_No_Immo": Vag_simos_3_3_No_Immo,
    "me7_5_No_Immo_Pin_Cs": me7_5_No_Immo_Pin_Cs,
    ###DASCH####
    "dash_vdo": dash_vdo,
    "Chevrolet_lacetti_dash_denso_96804358_EJ_6H21_11000_932900D_93c46" : Chevrolet_lacetti_dash_denso_96804358_EJ_6H21_11000_932900D_93c46,
    "Daewoo Gentra_dash_denso_93c56": Daewoo_Gentra_dash_denso_93c56,
    ###SRS#####
    "mazda_95320_GR6B_57K30B": mazda_95320_GR6B_57K30B,
    ###BCM##### 
    "bcm_valeo": bcm_valeo
}

def get_encoder(name):
    """Возвращает экземпляр кодировщика по его имени."""
    if name in encoders:
        return encoders[name]()
    else:
        print(f"Кодировщик {name} не найден")
        return None