# Исправленный encoders.py с поддержкой паролей в exe

import os
import sys
import json
from pathlib import Path
from PyQt5.QtWidgets import QDialog, QInputDialog, QMessageBox, QLineEdit
from PyQt5.QtCore import Qt

# Функция для получения правильного пути к ресурсам в exe
def resource_path(relative_path):
    """Получение пути к ресурсам в exe или обычном запуске"""
    try:
        # PyInstaller создает временную папку и сохраняет путь в _MEIPASS
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        full_path = os.path.join(base_path, relative_path)
        print(f"Resource path for {relative_path}: {full_path}")
        return full_path
    except Exception as e:
        print(f"Error in resource_path: {e}")
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

# Добавляем корневую директорию проекта в sys.path для корректных импортов
project_root = resource_path(".")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from encoder import Encoder

# Импортируем только существующие модули
try:
    from Plugin.ECU.Ems3120_No_Immo import Ems3120_No_Immo
    from Plugin.ECU.ME17_No_Immo import ME17_No_Immo
    from Plugin.ECU.Ems3130_NI import Ems3130_NI
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
    from Plugin.ECU.ME17_9_11_12_activate_cruise_control_NO_CS_CS_Winols import ME17_9_11_12_activate_cruise_control_NO_CS_CS_Winols
    from Plugin.ECU.delphi_MT_38_NI import delphi_MT_38_NI
    from Plugin.ECU.Me_17_kia_Hyundai import Me_17_kia_Hyundai
    from Plugin.ECU.simk43_NI import simk43_NI
    from Plugin.ECU.simk41_NI import simk41_NI
    from Plugin.ECU.sirius_d3_d4_NI import sirius_d3_d4_NI
    from Plugin.ECU.M78_NI import M78_NI
    from Plugin.ECU.Me17_China_NI import Me17_China_NI
    from Plugin.ECU.Ducato_edc16c39_NI import Ducato_edc16c39_NI
    from Plugin.ECU.Sid802_804_NI import Sid802_804_NI
    from Plugin.ECU.ms42_NI import ms42_NI
    from Plugin.ECU.M798_MG798_NI import M798_MG798_NI
    from Plugin.ECU.M_E_797_NI import M_E_797_NI
    from Plugin.ECU.kefico_MH72_MH832_MH83 import kefico_MH72_MH832_MH83
    from Plugin.ECU.nissan_hitachi_sh705507n_NI import nissan_hitachi_sh705507n_NI
    from Plugin.ECU.me_72_BMW_NI import me_72_BMW_NI
    
    from Plugin.EEPROM.j34p import j34p
    from Plugin.EEPROM.Geely_Emgrand_93c56_PIN import Geely_Emgrand_93c56_PIN
    from Plugin.EEPROM.me745_NI import me745_NI
    from Plugin.EEPROM.edc16u1 import edc16u1
    from Plugin.EEPROM.med_9_1_NI_95160 import med_9_1_NI_95160
    from Plugin.EEPROM.opel_25040_pin_vin import Opel_25040_Pin_Vin
    from Plugin.EEPROM.VW_Simos_4S_93C56_NI import VW_Simos_4S_93C56_NI
    from Plugin.EEPROM.Vag_simos_2_1_No_Immo import Vag_simos_2_1_No_Immo
    from Plugin.EEPROM.Vag_simos_3_3_No_Immo import Vag_simos_3_3_No_Immo
    from Plugin.EEPROM.VAG_EDC15_NI_24c02 import VAG_EDC15_NI_24c02
    from Plugin.EEPROM.VAG_M3_8_3_24C02_NI import VAG_M3_8_3_24C02_NI
    from Plugin.EEPROM.Chevrolet_E84_Pin_Vin import Chevrolet_E84_Pin_Vin
    from Plugin.EEPROM.Chevrolet_E84_Editor import Chevrolet_E84_Editor
    from Plugin.EEPROM.me7_5_No_Immo_Pin_Cs import me7_5_No_Immo_Pin_Cs
    from Plugin.EEPROM.kyron_95160_NI_CS import kyron_95160_NI_CS
    from Plugin.EEPROM.me7_1_NI_CS import me7_1_NI_CS
    
    from Plugin.SRS.mazda_95320_GR6B_57K30B import mazda_95320_GR6B_57K30B
    from Plugin.SRS.Continental_Reault_8201_385_569 import Continental_Reault_8201_385_569
    from Plugin.SRS.Hyundi_santa_fe_95910_2b180_epp95640 import Hyundi_santa_fe_95910_2b180_epp95640
    from Plugin.SRS.srs_kia_95910_3u100_95320 import srs_kia_95910_3u100_95320
    from Plugin.SRS._619771500_9674290880_2012MCU95320 import _619771500_9674290880_2012MCU95320
    from Plugin.SRS._0285001639_Bosch_98820_BU900_HC12B32 import _0285001639_Bosch_98820_BU900_HC12B32
    from Plugin.SRS.TRW_51822436_D219391215 import TRW_51822436_D219391215
    
    from Plugin.DASH.Chevrolet_lacetti_dash_denso_96804358_EJ_6H21_11000_932900D_93c46 import Chevrolet_lacetti_dash_denso_96804358_EJ_6H21_11000_932900D_93c46
    from Plugin.DASH.Daewoo_Gentra_dash_denso_93c56 import Daewoo_Gentra_dash_denso_93c56
    from Plugin.DASH.Chevrolet_lacetti_2007_2013_dash_denso_93c46 import Chevrolet_lacetti_2007_2013_dash_denso_93c46
    from Plugin.DASH.aveo_93c56 import aveo_93c56
    from Plugin.DASH._94003_G9000_J5060_94013_G9920_Genesis_g80_94013_J5740_94019_2P191_94043_B1010_94043_B1870_ahls_off import _94003_G9000_J5060_94013_G9920_Genesis_g80_94013_J5740_94019_2P191_94043_B1010_94043_B1870_ahls_off
    from Plugin.DASH.gelly_atlas_2020_24c02 import gelly_atlas_2020_24c02
    from Plugin.DASH.haval_m6_2023_dash_93c56 import haval_m6_2023_dash_93c56
    from Plugin.DASH.Prado_93c86_until_2015 import Prado_93c86_until_2015
    from Plugin.DASH.cg100x_ahl import cg100x_ahl
    
    from Plugin.BCM.Cruze_BCM_24c16_after_2009 import Cruze_BCM_24c16_after_2009

except ImportError as e:
    print(f"WARNING: Import error in encoders.py: {e}")

# Реестр энкодеров - только существующие классы
encoder_registry = {
    "Ems3120_No_Immo": Ems3120_No_Immo,
    "ME17_No_Immo": ME17_No_Immo,
    "Ems3130_NI": Ems3130_NI,
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
    "simk43_NI": simk43_NI,
    "simk41_NI": simk41_NI,
    "M798_MG798_NI": M798_MG798_NI,
    "M78_NI": M78_NI,
    "M_E_797_NI": M_E_797_NI,
    "ms42_NI": ms42_NI,
    "nissan_hitachi_sh705507n_NI": nissan_hitachi_sh705507n_NI,
    "Sid802_804_NI": Sid802_804_NI,
    "Ducato_edc16c39_NI": Ducato_edc16c39_NI,
    "sirius_d3_d4_NI": sirius_d3_d4_NI,
    "ME17_9_11_12_activate_cruise_control_NO_CS_CS_Winols": ME17_9_11_12_activate_cruise_control_NO_CS_CS_Winols,
    "Me17_China_NI": Me17_China_NI,
    "Me_17_kia_Hyundai": Me_17_kia_Hyundai,
    "delphi_MT_38_NI": delphi_MT_38_NI,
    "Melco_MH7203_NI": Melco_MH7203_NI,
    "Geely_Emgrand_93c56_PIN": Geely_Emgrand_93c56_PIN,
    "med_9_1_NI_95160": med_9_1_NI_95160,
    "EDC16U1(U34)_No_Immo": edc16u1,
    "j34p_No_Immo": j34p,
    "me745_NI": me745_NI,
    "me_72_BMW_NI": me_72_BMW_NI,
    "kefico_MH72_MH832_MH83": kefico_MH72_MH832_MH83,
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
    "_0285001639_Bosch_98820_BU900_HC12B32": _0285001639_Bosch_98820_BU900_HC12B32,
    "me7_5_No_Immo_Pin_Cs": me7_5_No_Immo_Pin_Cs,
    "kyron_95160_NI_CS": kyron_95160_NI_CS,
    "Prado_93c86_until_2015": Prado_93c86_until_2015,
    "_94003_G9000_J5060_94013_G9920_Genesis_g80_94013_J5740_94019_2P191_94043_B1010_94043_B1870_ahls_off": _94003_G9000_J5060_94013_G9920_Genesis_g80_94013_J5740_94019_2P191_94043_B1010_94043_B1870_ahls_off,
    "haval_m6_2023_dash_93c56": haval_m6_2023_dash_93c56,
    "gelly_atlas_2020_24c02": gelly_atlas_2020_24c02,
    "srs_kia_95910_3u100_95320": srs_kia_95910_3u100_95320,
    "Chevrolet_lacetti_dash_denso_96804358_EJ_6H21_11000_932900D_93c46": Chevrolet_lacetti_dash_denso_96804358_EJ_6H21_11000_932900D_93c46,
    "Daewoo_Gentra_dash_denso_93c56": Daewoo_Gentra_dash_denso_93c56,
    "Chevrolet_lacetti_2007_2013_dash_denso_93c46": Chevrolet_lacetti_2007_2013_dash_denso_93c46,
    "aveo_93c56": aveo_93c56,
    "Cruze_BCM_24c16_after_2009": Cruze_BCM_24c16_after_2009,
    "_619771500_9674290880_2012MCU95320": _619771500_9674290880_2012MCU95320,
    "TRW_51822436_D219391215": TRW_51822436_D219391215,
    "cg100x_ahl":cg100x_ahl,
    "me7_1_NI_CS": me7_1_NI_CS,
}

def check_password_protection(name: str):
    """Проверяет, защищен ли модуль паролем, читая из JSON"""
    try:
        ecu_data_path = resource_path("ecu_data.json")
        print(f"Checking password protection for {name}, JSON path: {ecu_data_path}")
        
        if not os.path.exists(ecu_data_path):
            print(f"WARNING: ecu_data.json not found at {ecu_data_path}")
            return False
            
        with open(ecu_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Рекурсивный поиск модуля в JSON структуре
        def search_module(obj, target_name):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key == target_name and isinstance(value, dict):
                        return value.get("password_protected", False)
                    elif isinstance(value, dict):
                        result = search_module(value, target_name)
                        if result is not None:
                            return result
            return None
            
        is_protected = search_module(data, name)
        print(f"Password protection check for {name}: {is_protected}")
        return is_protected or False
        
    except Exception as e:
        print(f"Error checking password protection for {name}: {e}")
        return False

def get_encoder(name: str, parent=None) -> Encoder:
    """Возвращает экземпляр энкодера по его имени с проверкой пароля."""
    print(f"get_encoder called with name: {name}, parent: {parent is not None}")
    
    # Проверяем наличие энкодера в реестре
    encoder_class = encoder_registry.get(name)
    if not encoder_class:
        print(f"get_encoder: Name = {name}, Encoder = None (not found in registry)")
        return None

    # Проверяем, что encoder_class действительно класс
    if not isinstance(encoder_class, type):
        print(f"get_encoder: Error - {name} is not a class: {encoder_class}")
        return None

    # Проверяем защиту паролем
    protected = check_password_protection(name)
    print(f"Module {name} password protection: {protected}")

    # Проверка пароля
    if protected:
        try:
            if parent is None:
                print(f"get_encoder: Name = {name}, Encoder = None (no parent for password dialog)")
                return None
                
            password, ok = QInputDialog.getText(
                parent, "Ввод пароля", 
                f"Модуль '{name}' защищен паролем.\nВведите пароль:",
                QLineEdit.Password, ""
            )
            
            if not ok:
                print(f"get_encoder: Name = {name}, Encoder = None (password dialog cancelled)")
                return None
                
            # Проверяем пароль (можете изменить на свой)
            correct_password = "GZkuoqZcE2PmL1QC"
            if password != correct_password:
                QMessageBox.warning(parent, "Ошибка", "Неверный пароль. Доступ запрещён.")
                print(f"get_encoder: Name = {name}, Encoder = None (wrong password)")
                return None
                
            print(f"get_encoder: Name = {name}, Password accepted")
            
        except Exception as e:
            print(f"Error in password dialog for {name}: {e}")
            if parent:
                QMessageBox.critical(parent, "Ошибка", f"Ошибка при вводе пароля: {str(e)}")
            return None

    # Создаем экземпляр энкодера
    try:
        encoder = encoder_class()
        print(f"get_encoder: Name = {name}, Encoder = {type(encoder).__name__} (SUCCESS)")
        return encoder
    except Exception as e:
        print(f"Error creating encoder instance for {name}: {e}")
        if parent:
            QMessageBox.critical(parent, "Ошибка", f"Ошибка создания модуля {name}: {str(e)}")
        return None