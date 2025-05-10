from file_editors import ME17_No_Immo, My2, Encoder, j34p, edc16u1, Opel_25040_Pin_Vin, mazda_95320_GR6B_57K30B, srs, eeprom, Vag_simos_2_1_No_Immo, Vag_simos_3_3_No_Immo 
from file_editors import Chevrolet_E84_Pin_Vin, Chevrolet_E84_Editor, me7_5_No_Immo_Pin_Cs, Chevrolet_lacetti_dash_denso_96804358_EJ_6H21_11000_932900D_93c46, Daewoo_Gentra_dash_denso_93c56 
from file_editors import Chevrolet_lacetti_2007_2013_dash_denso_93c46, aveo_93c56
ecu_encoder_map = {
    "EDC16U1(U34)_No_Immo": edc16u1,
    "ME17_No_Immo": ME17_No_Immo,
    "MED9.1": My2,
    "j34p_No_Immo": j34p,
    "Opel_25040_Pin_Vin": Opel_25040_Pin_Vin,
    "mazda_95320_GR6B_57K30B": mazda_95320_GR6B_57K30B,
    "Vag_simos_2_1_No_Immo": Vag_simos_2_1_No_Immo,
    "Vag_simos_3_3_No_Immo": Vag_simos_3_3_No_Immo,
    "Chevrolet_E84_Pin_Vin": Chevrolet_E84_Pin_Vin,
    "Chevrolet_E84_Editor": Chevrolet_E84_Editor,
    "me7_5_No_Immo_Pin_Cs": me7_5_No_Immo_Pin_Cs,
    "Chevrolet_lacetti_dash_denso_96804358_EJ_6H21_11000_932900D_93c46": Chevrolet_lacetti_dash_denso_96804358_EJ_6H21_11000_932900D_93c46,
    "Daewoo_Gentra_dash_denso_93c56": Daewoo_Gentra_dash_denso_93c56,
    "Chevrolet_lacetti_2007_2013_dash_denso_93c46" : Chevrolet_lacetti_2007_2013_dash_denso_93c46,
    "aveo_93c56" : aveo_93c56
}

def get_encoder_for_ecu(ecu_name):
    encoder_class = ecu_encoder_map.get(ecu_name, None)
    if encoder_class:
        encoder = encoder_class()
        print(f"get_encoder_for_ecu: ECU = {ecu_name}, Encoder = {type(encoder).__name__}")
        return encoder
    print(f"get_encoder_for_ecu: ECU = {ecu_name}, Encoder = None")
    return None