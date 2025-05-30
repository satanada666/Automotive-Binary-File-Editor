import os
import sys
from pathlib import Path
from PyQt5.QtWidgets import QDialog

# Добавляем корневую директорию проекта в sys.path для корректных импортов
sys.path.append(str(Path(__file__).parent))

from encoder import Encoder
from my2 import My2
from dash_vdo import dash_vdo
from bcm_valeo import bcm_valeo
from Plugin.ECU.me17 import ME17_No_Immo
from Plugin.ECU.Ems3120_No_Immo import Ems3120_No_Immo
from Plugin.EEPROM.j34p import j34p
from Plugin.EEPROM.edc16u1 import edc16u1
from Plugin.EEPROM.opel_25040_pin_vin import Opel_25040_Pin_Vin
from Plugin.SRS.mazda_95320_GR6B_57K30B import mazda_95320_GR6B_57K30B
from Plugin.EEPROM.Vag_simos_2_1_No_Immo import Vag_simos_2_1_No_Immo
from Plugin.EEPROM.Vag_simos_3_3_No_Immo import Vag_simos_3_3_No_Immo
from Plugin.EEPROM.Chevrolet_E84_Pin_Vin import Chevrolet_E84_Pin_Vin
from Plugin.EEPROM.Chevrolet_E84_Editor import Chevrolet_E84_Editor
from Plugin.EEPROM.me7_5_No_Immo_Pin_Cs import me7_5_No_Immo_Pin_Cs
from Plugin.DASH.Chevrolet_lacetti_dash_denso_96804358_EJ_6H21_11000_932900D_93c46 import Chevrolet_lacetti_dash_denso_96804358_EJ_6H21_11000_932900D_93c46
from Plugin.DASH.Daewoo_Gentra_dash_denso_93c56 import Daewoo_Gentra_dash_denso_93c56
from Plugin.DASH.Chevrolet_lacetti_2007_2013_dash_denso_93c46 import Chevrolet_lacetti_2007_2013_dash_denso_93c46
from Plugin.DASH.aveo_93c56 import aveo_93c56
from Plugin.BCM.Cruze_BCM_24c16_after_2009 import Cruze_BCM_24c16_after_2009

# Единый реестр энкодеров
encoder_registry = {
    "ME17_No_Immo": ME17_No_Immo,
    "Ems3120_No_Immo": Ems3120_No_Immo,
    "MED9.1": My2,
    "EDC16U1(U34)_No_Immo": edc16u1,
    "j34p_No_Immo": j34p,
    "Opel_25040_Pin_Vin": Opel_25040_Pin_Vin,
    "mazda_95320_GR6B_57K30B": mazda_95320_GR6B_57K30B,
    "Vag_simos_2_1_No_Immo": Vag_simos_2_1_No_Immo,
    "Vag_simos_3_3_No_Immo": Vag_simos_3_3_No_Immo,
    "Chevrolet_E84_Pin_Vin": Chevrolet_E84_Pin_Vin,
    "Chevrolet_E84_Editor": Chevrolet_E84_Editor,
    "me7_5_No_Immo_Pin_Cs": me7_5_No_Immo_Pin_Cs,
    "dash_vdo": dash_vdo,
    "Chevrolet_lacetti_dash_denso_96804358_EJ_6H21_11000_932900D_93c46": Chevrolet_lacetti_dash_denso_96804358_EJ_6H21_11000_932900D_93c46,
    "Daewoo_Gentra_dash_denso_93c56": Daewoo_Gentra_dash_denso_93c56,
    "Chevrolet_lacetti_2007_2013_dash_denso_93c46": Chevrolet_lacetti_2007_2013_dash_denso_93c46,
    "aveo_93c56": aveo_93c56,
    "Cruze_BCM_24c16_after_2009": Cruze_BCM_24c16_after_2009,
    "bcm_valeo": bcm_valeo
}

def get_encoder(name: str) -> Encoder:
    """Возвращает экземпляр энкодера по его имени."""
    encoder_class = encoder_registry.get(name)
    if encoder_class:
        encoder = encoder_class()
        print(f"get_encoder: Name = {name}, Encoder = {type(encoder).__name__}")
        return encoder
    print(f"get_encoder: Name = {name}, Encoder = None")
    return None