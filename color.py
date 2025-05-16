from PyQt5.QtGui import QPalette, QColor

color_list = [
    QColor("white"),
    QColor("#dce775"),  # светло-зеленый
    QColor("#ffccbc"),  # светло-оранжевый
    QColor("#b2ebf2"),  # светло-голубой
]

def setup_color(win, settings):
    """Настраивает цвет фона окна."""
    original_palette = win.palette()
    saved_color = settings.value("background_color", "default")
    color_index = -1

    if saved_color != "default":
        color = QColor(saved_color)
        palette = QPalette()
        palette.setColor(QPalette.Window, color)
        win.setAutoFillBackground(True)
        win.setPalette(palette)
        color_index = next((i for i, c in enumerate(color_list) if c.name() == saved_color), -1)

    def change_color():
        nonlocal color_index
        color_index = (color_index + 1) % (len(color_list) + 1)
        if color_index == len(color_list):
            win.setAutoFillBackground(False)
            win.setPalette(original_palette)
            settings.setValue("background_color", "default")
        else:
            palette = QPalette()
            palette.setColor(QPalette.Window, color_list[color_index])
            win.setAutoFillBackground(True)
            win.setPalette(palette)
            settings.setValue("background_color", color_list[color_index].name())

    return change_color