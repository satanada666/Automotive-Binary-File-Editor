from PyQt5.QtWidgets import QTreeWidgetItem
import os
from PyQt5.QtWidgets import QDialog

def populate_tree(tree, ecu_roots):
    """Заполняет дерево ECU объектами."""
    def add_items(parent, ecu_obj):
        item = QTreeWidgetItem(parent)
        item.setText(0, ecu_obj.name)
        for child in ecu_obj.children:
            add_items(item, child)

    for root in ecu_roots:
        add_items(tree, root)
    tree.expandAll()