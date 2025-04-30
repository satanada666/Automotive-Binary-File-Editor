
from PyQt5.QtWidgets import QFileDialog, QMessageBox

def open_file(win, settings, current_encoder):
    options = QFileDialog.Options()
    file_name, _ = QFileDialog.getOpenFileName(
        win, "Открыть файл", "",
        "Все файлы (*);;Бинарные файлы (*.bin);;Hex файлы (*.hex)",
        options=options
    )
    if file_name:
        try:
            with open(file_name, 'rb') as f:
                data = bytearray(f.read())
            
            # Проверяем, выбран ли редактор
            encoder = current_encoder[0]
            if encoder is None:
                QMessageBox.warning(win, "Предупреждение", 
                                   "Не выбран ECU. Сначала выберите ECU в дереве.")
                return
            
            # Проверяем файл через выбранный редактор
            if encoder.check(data):
                # Модифицируем файл
                encoder.encode(data)
                # Сохраняем данные в настройках для последующего сохранения
                settings.setValue("file_data", data)
                settings.setValue("last_file", file_name)
                QMessageBox.information(win, "Успешно", 
                                      f"Файл {file_name} успешно открыт и отредактирован")
            else:
                QMessageBox.warning(win, "Ошибка проверки", 
                                   "Файл не прошел проверку для выбранного ECU")
        except Exception as e:
            QMessageBox.critical(win, "Ошибка", f"Не удалось открыть файл: {str(e)}")

def save_file(win, settings, current_encoder):
    data = settings.value("file_data")
    if not data:
        QMessageBox.warning(win, "Предупреждение", "Нет данных для сохранения. Сначала откройте файл.")
        return
    
    # Проверяем, выбран ли редактор
    encoder = current_encoder[0]
    if encoder is None:
        QMessageBox.warning(win, "Предупреждение", 
                           "Не выбран ECU. Сначала выберите ECU в дереве.")
        return

    options = QFileDialog.Options()
    file_name, _ = QFileDialog.getSaveFileName(
        win, "Сохранить файл", "",
        "Все файлы (*);;Бинарные файлы (*.bin);;Hex файлы (*.hex)",
        options=options
    )
    if file_name:
        try:
            with open(file_name, 'wb') as f:
                f.write(data)
            settings.setValue("last_file", file_name)
            QMessageBox.information(win, "Успешно", f"Файл сохранен как {file_name}")
        except Exception as e:
            QMessageBox.critical(win, "Ошибка", f"Не удалось сохранить файл: {str(e)}")


