import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QProgressDialog
from PyQt5.QtCore import Qt
from dash_editor import DashEditor
from text_highlighting import display_hex_comparison
from dialogs import MileageVinPinEditDialog  # Импорт из dialogs.py

def open_file(win, settings, current_encoder):
    options = QFileDialog.Options()
    file_name, _ = QFileDialog.getOpenFileName(
        win, "Открыть файл", "", 
        "Все файлы (*);;Бинарные файлы (*.bin);;Hex файлы (*.hex)",
        options=options
    )
    if file_name:
        try:
            win.statusBar().showMessage(f"Открытие файла: {file_name}")
            encoder = current_encoder[0]
            if encoder is None:
                QMessageBox.warning(win, "Предупреждение",
                                   "Не выбран модуль редактирования. Выберите Module->brand->model")
                return
            if isinstance(encoder, type):
                print(f"open_file: Error - Encoder is a class ({encoder.__name__}), not an instance")
                raise ValueError("Encoder must be an instance, not a class")
            print(f"open_file: Encoder = {type(encoder).__name__}")
            
            file_size = os.path.getsize(file_name)
            print(f"open_file: File size = {file_size} bytes")
            
            with open(file_name, 'rb') as f:
                data = bytearray(f.read())
            
            original_copy = data[:]
            
            print(f"open_file: Data length = {len(data)}")
            try:
                check_result = encoder.check(data)
                print(f"open_file: Check result = {check_result}")
            except Exception as e:
                print(f"open_file: Error in check method: {str(e)}")
                raise
            
            if not check_result:
                QMessageBox.warning(win, "Ошибка проверки",
                                   "Файл не прошел проверку для выбранного ECU")
                return
            
            if isinstance(encoder, DashEditor):
                # Определяем модель и проверяем, нужно ли игнорировать VIN/PIN
                encoder_name = type(encoder).__name__
                ignore_vin_pin = (
                    'dash' in encoder_name.lower() or
                    'ecu' in encoder_name.lower() or
                    'eeprom' in encoder_name.lower()
                )
                
                if 'Cruze_BCM_24c16_after_2009' in encoder_name:
                    model = 'cruze_2009'
                elif 'Chevrolet_lacetti_2007_2013_dash_denso_93c46' in encoder_name:
                    model = 'lacetti_2007'
                elif 'Chevrolet_lacetti_dash_denso' in encoder_name:
                    model = 'lacetti_2004'
                elif 'Daewoo_Gentra' in encoder_name:
                    model = 'Daewoo_Gentra'
                else:
                    model = 'default'
                
                temp_result = encoder.encode(data, model=model)
                print(f"open_file: Initial encode result = {temp_result}")
                current_mileage = temp_result.get('mileage', 0)
                current_vin = temp_result.get('VIN', 'не найден')
                current_pin = temp_result.get('PIN', 'не найден')
                
                dialog = MileageVinPinEditDialog(win, current_mileage, current_vin, current_pin)
                if dialog.exec_():
                    new_mileage = dialog.get_new_mileage()
                    new_vin = dialog.get_new_vin()
                    new_pin = dialog.get_new_pin()
                    
                    print(f"open_file: Новый пробег = {new_mileage} км, VIN = {new_vin}, PIN = {new_pin}, ignore_vin_pin={ignore_vin_pin}")
                    
                    if ignore_vin_pin:
                        encoder.update_mileage(data, new_mileage, model=model)
                        data = encoder.data
                        if data is None:
                            QMessageBox.critical(win, "Ошибка", f"Не удалось обновить пробег: данные не получены. Модуль: {encoder_name}")
                            return
                    else:
                        data = encoder.update_mileage(data, new_mileage, model=model)
                        if data is None:
                            QMessageBox.critical(win, "Ошибка", f"Не удалось обновить пробег. Модуль: {encoder_name}")
                            return
                        
                        if new_vin and new_vin != current_vin:
                            data = encoder.set_vin(data, new_vin)
                            if data is None:
                                QMessageBox.critical(win, "Ошибка", f"Не удалось обновить VIN. Модуль: {encoder_name}")
                                return
                        
                        if new_pin and new_pin != current_pin:
                            data = encoder.set_pin(data, new_pin)
                            if data is None:
                                QMessageBox.critical(win, "Ошибка", f"Не удалось обновить PIN. Модуль: {encoder_name}")
                                return
                    
                    result = encoder.encode(data, model=model)
                else:
                    print("open_file: Данные не изменены, используем текущие")
                    result = temp_result
            else:
                result = encoder.encode(data)
            
            print(f"open_file: Final encode result = {result}")
            if isinstance(result, dict):
                if 'VIN' in result and 'PIN' in result:
                    settings.setValue("last_vin", result['VIN'])
                    settings.setValue("last_pin", result['PIN'])
                    print(f"open_file: Saved VIN={result['VIN']}, PIN={result['PIN']} to settings")
                if 'mileage' in result:
                    settings.setValue("last_mileage", result['mileage'])
                    print(f"open_file: Saved mileage={result['mileage']} to settings")
            else:
                print("open_file: No VIN/PIN/mileage data to save")
            
            settings.setValue("file_data", data)
            settings.setValue("last_file", file_name)
            display_hex_comparison(original_copy, data, win)
            QMessageBox.information(win, "Успешно",
                                   f"Файл {file_name} успешно открыт и обработан")
        except Exception as e:
            QMessageBox.critical(win, "Ошибка", f"Не удалось открыть файл: {str(e)}")
            print(f"Error opening file: {str(e)}")

def save_file(win, settings, current_encoder):
    if not settings.contains("file_data") or not settings.contains("last_file"):
        QMessageBox.warning(win, "Предупреждение", "Сначала необходимо открыть файл")
        return
    
    file_data = settings.value("file_data")
    last_file = settings.value("last_file")
    
    options = QFileDialog.Options()
    file_name, _ = QFileDialog.getSaveFileName(
        win, "Сохранить файл", last_file,
        "Бинарные файлы (*.bin);;Hex файлы (*.hex);;Все файлы (*)",
        options=options
    )
    
    if file_name:
        try:
            with open(file_name, 'wb') as f:
                f.write(file_data)
            win.statusBar().showMessage(f"Файл сохранён: {file_name}")
            settings.setValue("last_file", file_name)
            print(f"save_file: File saved to {file_name}")
        except Exception as e:
            QMessageBox.critical(win, "Ошибка", f"Не удалось сохранить файл: {str(e)}")
            print(f"Error saving file: {str(e)}")