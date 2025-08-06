class ECUNode:
    def __init__(self, name):
        self.name = name
        self.children = []
        self.password_protected = False
        self.image = None  # Для хранения пути к изображению

class ECU(ECUNode):
    pass

class EEPROMNode(ECUNode):
    pass

class DASHNode(ECUNode):
    pass

class BCMNode(ECUNode):
    pass
###work
'''class ECUNode:
    def __init__(self, name):
        self.name = name
        self.children = []

class ECU(ECUNode): pass
class EEPROMNode(ECUNode): pass
class DASHNode(ECUNode): pass
class BCMNode(ECUNode): pass'''
