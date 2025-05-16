
class ECUNode:
    def __init__(self, name):
        self.name = name
        self.children = []

class ECU(ECUNode): pass
class EEPROMNode(ECUNode): pass
class DASHNode(ECUNode): pass
class BCMNode(ECUNode): pass
