from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtCore import Qt

def populate_tree(tree, ecu_roots):
    """Заполняет дерево ECU объектами."""
    def add_items(parent, ecu_obj):
        item = QTreeWidgetItem(parent)
        item.setText(0, ecu_obj.name)
        print(f"🌳 Добавлен узел: {ecu_obj.name}")
        # Проверяем, есть ли поле image в объекте
        if hasattr(ecu_obj, 'image') and ecu_obj.image:
            print(f"🖼️ Найдено изображение для {ecu_obj.name}: {ecu_obj.image}")
            image_item = QTreeWidgetItem(item)
            image_item.setText(0, ecu_obj.image)
            image_item.setData(0, Qt.UserRole, {'type': 'image', 'path': ecu_obj.image})
            print(f"✅ Создан узел изображения: {ecu_obj.image}")
        else:
            print(f"ℹ️ Нет изображения для {ecu_obj.name}")
        # Рекурсивно добавляем дочерние элементы
        for child in ecu_obj.children:
            add_items(item, child)

    tree.clear()
    for root in ecu_roots:
        add_items(tree, root)
    print("🌳 Дерево заполнено, все узлы готовы к отображению")

'''from PyQt5.QtWidgets import QTreeWidgetItem
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
    tree.expandAll()'''

