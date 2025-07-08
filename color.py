from PyQt5.QtGui import QPalette, QColor, QPixmap, QBrush
from PyQt5.QtCore import Qt
import os

def setup_color(win, settings):
    """Настраивает цвет фона окна с предустановленными картинками."""
    original_palette = win.palette()
    
    # Список фонов: цвета + пути к картинкам
    background_list = [
        {"type": "color", "value": QColor("white"), "name": "Белый"},
        {"type": "color", "value": QColor("#dce775"), "name": "Светло-зеленый"},
        {"type": "color", "value": QColor("#ffccbc"), "name": "Светло-оранжевый"},
        {"type": "color", "value": QColor("#b2ebf2"), "name": "Светло-голубой"},
        {"type": "image", "value": "images/background1.jpg", "name": "Картинка 1"},
        {"type": "image", "value": "images/background2.png", "name": "Картинка 2"},
        {"type": "image", "value": "images/background3.jpg", "name": "Картинка 3"},
        {"type": "image", "value": "images/background4.png", "name": "Картинка 4"},
    ]
    
    current_index = -1  # Начинаем с оригинального фона
    
    # Восстановление сохраненного фона
    saved_bg_type = settings.value("background_type", "default")
    if saved_bg_type != "default":
        try:
            saved_index = int(settings.value("background_index", 0))
            if 0 <= saved_index < len(background_list):
                current_index = saved_index
                apply_background(win, background_list[current_index])
                print(f"Восстановлен фон: {background_list[current_index]['name']}")
        except Exception as e:
            print(f"Ошибка восстановления фона: {e}")

    def apply_background(window, bg_item):
        """Применяет фон (цвет или картинку)."""
        try:
            if bg_item["type"] == "color":
                # Применяем цветной фон
                palette = QPalette()
                palette.setColor(QPalette.Window, bg_item["value"])
                window.setAutoFillBackground(True)
                window.setPalette(palette)
                print(f"Установлен цветной фон: {bg_item['name']}")
                
            elif bg_item["type"] == "image":
                # Проверяем существование файла
                if not os.path.exists(bg_item["value"]):
                    print(f"Файл изображения не найден: {bg_item['value']}")
                    return False
                
                # Загружаем и применяем картинку
                pixmap = QPixmap(bg_item["value"])
                if not pixmap.isNull():
                    # Масштабируем картинку под размер окна
                    window_size = window.size()
                    scaled_pixmap = pixmap.scaled(
                        window_size, 
                        Qt.KeepAspectRatioByExpanding, 
                        Qt.SmoothTransformation
                    )
                    
                    palette = QPalette()
                    palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
                    window.setAutoFillBackground(True)
                    window.setPalette(palette)
                    print(f"Установлен фон-картинка: {bg_item['name']}")
                    return True
                else:
                    print(f"Не удалось загрузить изображение: {bg_item['value']}")
                    return False
        except Exception as e:
            print(f"Ошибка применения фона: {e}")
            return False
        return True

    def change_color():
        """Переключает фоны по кругу: оригинальный -> цвета -> картинки -> оригинальный."""
        nonlocal current_index
        
        current_index = (current_index + 1) % (len(background_list) + 1)
        
        if current_index == len(background_list):
            # Сброс к оригинальному фону
            win.setAutoFillBackground(False)
            win.setPalette(original_palette)
            settings.setValue("background_type", "default")
            settings.remove("background_index")
            print("Восстановлен оригинальный фон")
        else:
            # Применение выбранного фона
            bg_success = apply_background(win, background_list[current_index])
            if bg_success:
                settings.setValue("background_type", "custom")
                settings.setValue("background_index", current_index)
            else:
                # Если не удалось применить фон, переходим к следующему
                change_color()

    def get_current_background_name():
        """Возвращает название текущего фона."""
        if current_index == -1 or current_index >= len(background_list):
            return "Оригинальный"
        return background_list[current_index]["name"]

    def set_specific_background(index):
        """Устанавливает конкретный фон по индексу."""
        nonlocal current_index
        if 0 <= index < len(background_list):
            current_index = index
            bg_success = apply_background(win, background_list[current_index])
            if bg_success:
                settings.setValue("background_type", "custom")
                settings.setValue("background_index", current_index)
                return True
        return False

    def reset_to_original():
        """Сбрасывает к оригинальному фону."""
        nonlocal current_index
        current_index = -1
        win.setAutoFillBackground(False)
        win.setPalette(original_palette)
        settings.setValue("background_type", "default")
        settings.remove("background_index")
        print("Сброшен к оригинальному фону")

    def get_available_backgrounds():
        """Возвращает список доступных фонов."""
        available = []
        for i, bg in enumerate(background_list):
            if bg["type"] == "color":
                available.append({"index": i, "name": bg["name"], "type": "color"})
            elif bg["type"] == "image":
                if os.path.exists(bg["value"]):
                    available.append({"index": i, "name": bg["name"], "type": "image"})
                else:
                    print(f"Изображение недоступно: {bg['value']}")
        return available

    # Создаем папку для изображений, если её нет
    if not os.path.exists("images"):
        os.makedirs("images")
        print("Создана папка 'images' для фоновых изображений")
        print("Поместите ваши картинки в эту папку с именами:")
        print("- background1.jpg")
        print("- background2.png")
        print("- background3.jpg")
        print("- background4.png")

    # Возвращаем главную функцию для совместимости со старым кодом
    # Также возвращаем словарь дополнительных функций как атрибут
    change_color.get_current_name = get_current_background_name
    change_color.set_background = set_specific_background
    change_color.reset = reset_to_original
    change_color.get_available = get_available_backgrounds
    
    return change_color

# Пример использования:
"""
# В вашем главном коде:
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import QSettings
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тест фоновых изображений")
        self.setGeometry(100, 100, 800, 600)
        
        # Инициализация настроек
        self.settings = QSettings("MyApp", "BackgroundSettings")
        
        # Настройка UI
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Метка для отображения текущего фона
        self.status_label = QLabel("Текущий фон: Оригинальный")
        layout.addWidget(self.status_label)
        
        # Кнопка смены фона
        change_btn = QPushButton("Сменить фон")
        change_btn.clicked.connect(self.change_background)
        layout.addWidget(change_btn)
        
        # Кнопка сброса
        reset_btn = QPushButton("Сброс к оригинальному")
        reset_btn.clicked.connect(self.reset_background)
        layout.addWidget(reset_btn)
        
        # Настройка фона
        self.bg_functions = setup_color(self, self.settings)
        self.update_status()
    
    def change_background(self):
        self.bg_functions['change_color']()
        self.update_status()
    
    def reset_background(self):
        self.bg_functions['reset']()
        self.update_status()
    
    def update_status(self):
        current_name = self.bg_functions['get_current_name']()
        self.status_label.setText(f"Текущий фон: {current_name}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
"""