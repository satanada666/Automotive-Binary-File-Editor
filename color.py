from PyQt5.QtGui import QPalette, QColor # Импортируем необходимые модули из PyQt5 

# Список доступных цветов
color_list = [ # список цветов для фона 
    QColor("white"), # белый 
    QColor("#dce775"),  # светло-зеленый
    QColor("#ffccbc"),  # светло-оранжевый
    QColor("#b2ebf2"),   # светло-голубой
    #QColor("default")  # светло-розовый
]

def setup_color(win, settings): # Функция для настройки цвета фона окна
    original_palette = win.palette() # Сохраняем оригинальную палитру окна
    saved_color = settings.value("background_color") # Получаем сохраненный цвет из настроек
    color_index = -1  # -1 означает оригинальную палитру    

    if saved_color and saved_color != "default": # Если сохраненный цвет не пустой и не "default" 
        color = QColor(saved_color) # Преобразуем сохраненный цвет в объект QColor
        new_palette = win.palette() # Создаем новую палитру
        new_palette.setColor(QPalette.Window, color) # Устанавливаем цвет окна в новую палитру
        win.setAutoFillBackground(True)
        win.setPalette(new_palette)
        try:
            color_index = next(i for i, c in enumerate(color_list) if c.name() == saved_color)
        except StopIteration:
            color_index = -1
    else:
        win.setAutoFillBackground(False)
        win.setPalette(original_palette)

    def change_color():
        nonlocal color_index
        color_index += 1
        if color_index >= len(color_list):
            win.setPalette(original_palette)
            win.setAutoFillBackground(False)
            settings.setValue("background_color", "default")
            color_index = -1
        else:
            new_palette = win.palette()
            new_palette.setColor(QPalette.Window, color_list[color_index])
            win.setPalette(new_palette)
            win.setAutoFillBackground(True)
            settings.setValue("background_color", color_list[color_index].name())

    return change_color  # Возвращаем функцию изменения цвета



