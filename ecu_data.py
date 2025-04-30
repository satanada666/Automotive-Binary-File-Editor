import json #импортируем библиотеку json для работы с JSON файлами
from ECU import ECU, EEPROMNode, DASHNode, BCMNode #импортируем классы ECU, EEPROMNode, DASHNode, BCMNode из файла ECU.py
# Импортируем необходимые классы из ECU.py

class_map = { #словарь, содержащий классы для каждого типа узла
    "ECU": ECU, # базовый класс ECU
    "ECU1": ECU, # наследуемый класс ECU1 (можно добавить в будущем) 
    "EEPROM": EEPROMNode, # класс для EEPROM узлов
    "DASH": DASHNode, # класс для DASH узлов
    "BCM": BCMNode # класс для BCM узлов
}

def load_ecu_json(path="ecu_data.json"): #функция для загрузки JSON файла
    with open(path, "r", encoding="utf-8") as f: #открываем файл в режиме чтения с кодировкой utf-8 и сохраняем его в переменную f
        return json.load(f) #загружаем содержимое файла в виде словаря json.loads(f.read()) и возвращаем его вызовом функции json.load() 

def build_ecu_objects(data: dict):
    def create_recursive(name, children_dict):
        cls = class_map.get(name, ECU)
        instance = cls(name)
        instance.children = [
            create_recursive(child_name, grandkids)
            for child_name, grandkids in children_dict.items()
        ]
        return instance

    return [create_recursive(name, children) for name, children in data.items()]

def create_ecu_hierarchy_from_file(json_path="ecu_data.json"):
    data = load_ecu_json(json_path)
    return build_ecu_objects(data)
