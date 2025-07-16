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
from Plugin.ECU.Ems3132_No_Immo import Ems3132_No_Immo
from Plugin.ECU.Ems3134_No_Immo import Ems3134_No_Immo
from Plugin.ECU.sirius_32_No_Immo_v1 import sirius_32_No_Immo_v1
from Plugin.ECU.sirius_32_No_Immo_v2 import sirius_32_No_Immo_v2
from Plugin.ECU.MT86_No_Immo import MT86_No_Immo
from Plugin.ECU.BMW_MS41_No_Immo_CS import BMW_MS41_No_Immo_CS
from Plugin.ECU.China_797_No_Immo import China_797_No_Immo
from Plugin.ECU.nissan_classic_SH705524N_NI import nissan_classic_SH705524N_NI
from Plugin.ECU.nissan_classic_SH705529N_NI import nissan_classic_SH705529N_NI
from Plugin.ECU.Mitsubishi_MH8302F_NI import Mitsubishi_MH8302F_NI
from Plugin.ECU.Melco_MH7203_NI import Melco_MH7203_NI
from Plugin.ECU.sim2k_140_141_341_NI import sim2k_140_141_341_NI
from Plugin.ECU.sim2k_240_241_242_245 import sim2k_240_241_242_245
from Plugin.ECU.sim2k_250_251 import sim2k_250_251
from Plugin.EEPROM.j34p import j34p
from Plugin.EEPROM.me745_NI import me745_NI
from Plugin.EEPROM.edc16u1 import edc16u1
from Plugin.EEPROM.med_9_1_NI_95160 import med_9_1_NI_95160
from Plugin.EEPROM.opel_25040_pin_vin import Opel_25040_Pin_Vin
from Plugin.EEPROM.VW_Simos_4S_93C56_NI import VW_Simos_4S_93C56_NI
from Plugin.SRS.mazda_95320_GR6B_57K30B import mazda_95320_GR6B_57K30B
from Plugin.SRS.Continental_Reault_8201_385_569 import Continental_Reault_8201_385_569
from Plugin.SRS.Hyundi_santa_fe_95910_2b180_epp95640 import Hyundi_santa_fe_95910_2b180_epp95640
from Plugin.SRS.srs_kia_95910_3u100_95320 import srs_kia_95910_3u100_95320
from Plugin.EEPROM.Vag_simos_2_1_No_Immo import Vag_simos_2_1_No_Immo
from Plugin.EEPROM.Vag_simos_3_3_No_Immo import Vag_simos_3_3_No_Immo
from Plugin.EEPROM.VAG_EDC15_NI_24c02 import VAG_EDC15_NI_24c02
from Plugin.EEPROM.VAG_M3_8_3_24C02_NI import VAG_M3_8_3_24C02_NI
from Plugin.EEPROM.Chevrolet_E84_Pin_Vin import Chevrolet_E84_Pin_Vin
from Plugin.EEPROM.Chevrolet_E84_Editor import Chevrolet_E84_Editor
from Plugin.EEPROM.me7_5_No_Immo_Pin_Cs import me7_5_No_Immo_Pin_Cs
from Plugin.EEPROM.kyron_95160_NI_CS import kyron_95160_NI_CS
from Plugin.DASH.Chevrolet_lacetti_dash_denso_96804358_EJ_6H21_11000_932900D_93c46 import Chevrolet_lacetti_dash_denso_96804358_EJ_6H21_11000_932900D_93c46
from Plugin.DASH.Daewoo_Gentra_dash_denso_93c56 import Daewoo_Gentra_dash_denso_93c56
from Plugin.DASH.Chevrolet_lacetti_2007_2013_dash_denso_93c46 import Chevrolet_lacetti_2007_2013_dash_denso_93c46
from Plugin.DASH.aveo_93c56 import aveo_93c56
from Plugin.DASH._94003_G9000_ahls_off import _94003_G9000_ahls_off
from Plugin.DASH.gelly_atlas_2020_24c02 import gelly_atlas_2020_24c02
from Plugin.DASH.haval_m6_2023_dash_93c56 import haval_m6_2023_dash_93c56
from Plugin.DASH.Prado_93c86_until_2015 import Prado_93c86_until_2015
from Plugin.BCM.Cruze_BCM_24c16_after_2009 import Cruze_BCM_24c16_after_2009

# Единый реестр энкодеров
encoder_registry = {
    "ME17_No_Immo": ME17_No_Immo,
    "Ems3120_No_Immo": Ems3120_No_Immo,
    "Ems3132_No_Immo": Ems3132_No_Immo,
    "Ems3134_No_Immo": Ems3134_No_Immo,
    "sirius_32_No_Immo_v1": sirius_32_No_Immo_v1,
    "sirius_32_No_Immo_v2": sirius_32_No_Immo_v2,
    "MT86_No_Immo": MT86_No_Immo,
    "BMW_MS41_No_Immo_CS": BMW_MS41_No_Immo_CS,
    "China_797_No_Immo": China_797_No_Immo,
    "nissan_classic_SH705524N_NI": nissan_classic_SH705524N_NI,
    "nissan_classic_SH705529N_NI": nissan_classic_SH705529N_NI,
    "Mitsubishi_MH8302F_NI": Mitsubishi_MH8302F_NI,
    "sim2k_140_141_341_NI": sim2k_140_141_341_NI,
    "sim2k_240_241_242_245": sim2k_240_241_242_245,
    "sim2k_250_251": sim2k_250_251,
    "Melco_MH7203_NI": Melco_MH7203_NI,
    "MED9.1": My2,
    "med_9_1_NI_95160": med_9_1_NI_95160,
    "EDC16U1(U34)_No_Immo": edc16u1,
    "j34p_No_Immo": j34p,
    "me745_NI": me745_NI,
    "VW_Simos_4S_93C56_NI": VW_Simos_4S_93C56_NI,
    "Opel_25040_Pin_Vin": Opel_25040_Pin_Vin,
    "mazda_95320_GR6B_57K30B": mazda_95320_GR6B_57K30B,
    "Continental_Reault_8201_385_569": Continental_Reault_8201_385_569,
    "Hyundi_santa_fe_95910_2b180_epp95640": Hyundi_santa_fe_95910_2b180_epp95640,
    "Vag_simos_2_1_No_Immo": Vag_simos_2_1_No_Immo,
    "Vag_simos_3_3_No_Immo": Vag_simos_3_3_No_Immo,
    "VAG_EDC15_NI_24c02": VAG_EDC15_NI_24c02,
    "VAG_M3_8_3_24C02_NI": VAG_M3_8_3_24C02_NI,
    "Chevrolet_E84_Pin_Vin": Chevrolet_E84_Pin_Vin,
    "Chevrolet_E84_Editor": Chevrolet_E84_Editor,
    "me7_5_No_Immo_Pin_Cs": me7_5_No_Immo_Pin_Cs,
    "kyron_95160_NI_CS": kyron_95160_NI_CS,
    "Prado_93c86_until_2015": Prado_93c86_until_2015,
    "dash_vdo": dash_vdo,
    "_94003_G9000_ahls_off": _94003_G9000_ahls_off,
    "haval_m6_2023_dash_93c56": haval_m6_2023_dash_93c56,
    "gelly_atlas_2020_24c02": gelly_atlas_2020_24c02,
    "srs_kia_95910_3u100_95320": srs_kia_95910_3u100_95320,
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