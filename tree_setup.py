'''функция populate_tree предназначена для добавления элементов в виджет дерева
 (QTreeWidget) в PyQt5, используя объекты ECU. Она рекурсивно обрабатывает
 родительские и дочерние объекты, добавляя их в дерево, и затем разворачивает
   все элементы дерева с помощью expandAll().'''

from PyQt5 import QtWidgets # импортируем необходимые модули

def populate_tree(tree, ecu_roots): ## функция для добавления элементов в дерево
    def add_items(parent_widget, ecu_obj): # рекурсивная функция для добавления элементов
        item = QtWidgets.QTreeWidgetItem(parent_widget) # создание нового элемента
        item.setText(0, ecu_obj.name) # установка текста элемента
        for child in getattr(ecu_obj, "children", []): # обработка дочерних объектов
            add_items(item, child) # рекурсивный вызов для дочерних объектов
            '''Проходит по всем корневым объектам ECU в списке ecu_roots 
и вызывает add_items для каждого из них, добавляя все элементы в дерево.'''

    for root in ecu_roots:
        add_items(tree, root)

    tree.expandAll()
    '''После того как все элементы добавлены, дерево 
    разворачивается, чтобы показать все вложенные элементы.'''
