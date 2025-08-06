import json
from ECU import ECU, EEPROMNode, DASHNode, BCMNode

def load_ecu_json(path: str = "ecu_data.json") -> dict:
    """Загружает JSON-файл с данными ECU."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"🔍 JSON загружен, ключи верхнего уровня: {list(data.keys())}")
    return data

def build_ecu_objects(data: dict) -> list:
    """Создаёт иерархию объектов ECU из словаря."""
    def create_recursive(name: str, children_dict: dict):
        cls = {
            "ECU": ECU,
            "EEPROM": EEPROMNode,
            "DASH": DASHNode,
            "BCM": BCMNode
        }.get(name, ECU)
        instance = cls(name)
        instance.password_protected = children_dict.get("password_protected", False)
        instance.image = children_dict.get("image")
        print(f"🔍 Обработка узла '{name}': password_protected={instance.password_protected}, image={instance.image}")
        instance.children = [
            create_recursive(child_name, grandkids)
            for child_name, grandkids in children_dict.items()
            if child_name not in ("password_protected", "image")
        ]
        return instance

    return [create_recursive(name, children) for name, children in data.items()]

def create_ecu_hierarchy_from_file(json_path: str = "ecu_data.json") -> list:
    """Создаёт иерархию ECU из JSON-файла."""
    data = load_ecu_json(json_path)
    return build_ecu_objects(data)

'''import json
from ECU import ECU, EEPROMNode, DASHNode, BCMNode

def load_ecu_json(path: str = "ecu_data.json") -> dict:
    """Загружает JSON-файл с данными ECU."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_ecu_objects(data: dict) -> list:
    """Создаёт иерархию объектов ECU из словаря."""
    def create_recursive(name: str, children_dict: dict):
        cls = {
            "ECU": ECU,
            "EEPROM": EEPROMNode,
            "DASH": DASHNode,
            "BCM": BCMNode
        }.get(name, ECU)
        instance = cls(name)
        instance.children = [
            create_recursive(child_name, grandkids)
            for child_name, grandkids in children_dict.items()
        ]
        return instance

    return [create_recursive(name, children) for name, children in data.items()]

def create_ecu_hierarchy_from_file(json_path: str = "ecu_data.json") -> list:
    """Создаёт иерархию ECU из JSON-файла."""
    data = load_ecu_json(json_path)
    return build_ecu_objects(data)'''

###work
'''import json
from ECU import ECU, EEPROMNode, DASHNode, BCMNode

def load_ecu_json(path: str = "ecu_data.json") -> dict:
    """Загружает JSON-файл с данными ECU."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_ecu_objects(data: dict) -> list:
    """Создаёт иерархию объектов ECU из словаря."""
    def create_recursive(name: str, children_dict: dict):
        cls = {
            "ECU": ECU,
            "EEPROM": EEPROMNode,
            "DASH": DASHNode,
            "BCM": BCMNode
        }.get(name, ECU)
        instance = cls(name)
        instance.password_protected = children_dict.get("password_protected", False)
        instance.children = [
            create_recursive(child_name, grandkids)
            for child_name, grandkids in children_dict.items()
            if child_name != "password_protected"
        ]
        return instance

    return [create_recursive(name, children) for name, children in data.items()]

def create_ecu_hierarchy_from_file(json_path: str = "ecu_data.json") -> list:
    """Создаёт иерархию ECU из JSON-файла."""
    data = load_ecu_json(json_path)
    return build_ecu_objects(data)'''