
import os
import sys
import requests
import webbrowser
import subprocess
import tempfile
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QSettings, Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QGroupBox, QVBoxLayout, QLabel, QInputDialog, QDialog

from packaging import version
from color import setup_color
from file_operations import open_file, save_file
from tree_setup import populate_tree
from ecu_data import create_ecu_hierarchy_from_file
from encoders import get_encoder
from text_highlighting import display_hex_comparison
from file_compare_worker import compare_two_files
from dash_editor import DashEditor
from dialogs import MileageVinPinEditDialog

LOCAL_VERSION = "1.1.40"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/satanada666/Automotive-Binary-File-Editor/main/version.txt"
DOWNLOAD_URL = "https://github.com/satanada666/Automotive-Binary-File-Editor/releases"
EXE_NAME = "Black_Box.exe"

def resource_path(relative_path):
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        full_path = os.path.join(base_path, relative_path)
        print(f"Resolved path for {relative_path}: {full_path}")
        return full_path
    except Exception as e:
        print(f"Error resolving resource path for {relative_path}: {str(e)}")
        sys.exit(1)

# =========================== Автообновление ===========================

class UpdaterThread(QThread):
    progress = pyqtSignal(int)
    done = pyqtSignal(str)
    error = pyqtSignal(str)

    def run(self):
        try:
            # Получение последней версии с GitHub
            r = requests.get(GITHUB_VERSION_URL)
            r.raise_for_status()
            new_version = r.text.strip()

            # Проверка необходимости обновления
            if version.parse(new_version) <= version.parse(LOCAL_VERSION):
                self.done.emit("already_latest")
                return

            # Путь к рабочему столу и целевой папке
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            target_dir = os.path.join(desktop_path, "New_version_Black_Box")
            os.makedirs(target_dir, exist_ok=True)

            # Путь к файлу
            target_exe = os.path.join(target_dir, EXE_NAME)

            # URL для скачивания
            url = f"https://github.com/satanada666/Automotive-Binary-File-Editor/releases/download/v{new_version}/{EXE_NAME}"

            # Скачивание с прогрессом
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                total = int(r.headers.get('content-length', 0))
                downloaded = 0
                with open(target_exe, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total:
                                percent = int(downloaded * 100 / total)
                                self.progress.emit(percent)

            # Готово — возвращаем путь к новому exe
            self.done.emit(target_exe)

        except Exception as e:
            self.error.emit(str(e))


def auto_update_exe(win):
    win.updater_thread = UpdaterThread()
    thread = win.updater_thread
    bar = win.progressBar
    bar.setVisible(True)
    bar.setValue(0)

    def on_done(path):
        if path == "already_latest":
            QMessageBox.information(win, "Обновление", "Установлена последняя версия.")
            bar.setVisible(False)
            return

        QMessageBox.information(win, "Обновление", "Загрузка завершена. Новая версия запускается.")

        # Открываем папку с новой версией
        try:
            folder_path = os.path.dirname(path)
            subprocess.Popen(f'explorer "{folder_path}"')
        except Exception as e:
            print(f"Не удалось открыть папку: {e}")

        # Запускаем новую версию
        try:
            subprocess.Popen([path])
        except Exception as e:
            QMessageBox.critical(win, "Ошибка", f"Не удалось запустить новую версию: {str(e)}")

        # Завершаем текущую программу
        thread.quit()
        thread.wait()
        QtWidgets.QApplication.quit()

    def on_error(msg):
        QMessageBox.critical(win, "Ошибка загрузки обновления", msg)
        bar.setVisible(False)

    thread.progress.connect(bar.setValue)
    thread.done.connect(on_done)
    thread.error.connect(on_error)
    thread.start()


# Дополнительная функция для проверки обновлений без автозагрузки
def check_for_updates(win):
    try:
        response = requests.get(GITHUB_VERSION_URL)
        response.raise_for_status()
        server_version = response.text.strip()
        print(f"Checking for updates: local={LOCAL_VERSION}, server={server_version}")

        if version.parse(server_version) > version.parse(LOCAL_VERSION):
            reply = QMessageBox.question(
                win, "Обновление",
                f"Доступна новая версия {server_version} (текущая: {LOCAL_VERSION}). Обновить?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                auto_update_exe(win)
            if hasattr(win, 'actionYes'):
                win.actionYes.setEnabled(True)
        else:
            QMessageBox.information(win, "Обновление",
                                   f"У вас установлена актуальная версия {LOCAL_VERSION}.")
            if hasattr(win, 'actionYes'):
                win.actionYes.setEnabled(False)
    except Exception as e:
        QMessageBox.critical(win, "Ошибка", f"Не удалось проверить обновления: {e}")
        if hasattr(win, 'actionYes'):
            win.actionYes.setEnabled(False)

def download_update(win):
    try:
        webbrowser.open(DOWNLOAD_URL)
    except Exception as e:
        QMessageBox.critical(win, "Ошибка", f"Не удалось открыть страницу загрузки: {str(e)}")

# =========================== Основная логика ===========================

def edit_mileage(win, settings, current_encoder):
    if not settings.contains("file_data") or not settings.contains("last_file"):
        QMessageBox.warning(win, "Предупреждение", "Сначала необходимо открыть файл")
        return
    
    encoder = current_encoder[0]
    if encoder is None:
        QMessageBox.warning(win, "Предупреждение",
                           "Не выбран модуль редактирования. Выберите Module->brand->model")
        return
    
    if not isinstance(encoder, DashEditor):
        QMessageBox.warning(win, "Предупреждение",
                           "Текущий модуль не поддерживает редактирование пробега")
        return
    
    try:
        file_data = settings.value("file_data")
        current_mileage = settings.value("last_mileage", 0)
        current_vin = settings.value("last_vin", "не найден")
        current_pin = settings.value("last_pin", "не найден")
        
        if current_mileage == "N/A":
            current_mileage = 0
        try:
            current_mileage = int(current_mileage)
        except:
            current_mileage = 0
        
        dialog = MileageVinPinEditDialog(win, current_mileage, current_vin, current_pin)
        if dialog.exec_() == QDialog.Accepted:
            new_mileage = dialog.get_new_mileage()
            new_vin = dialog.get_new_vin()
            new_pin = dialog.get_new_pin()
            
            print(f"edit_mileage: Пользователь ввел: mileage={new_mileage}, vin={new_vin}, pin={new_pin}")
            
            # Проверяем диапазон пробега
            if new_mileage > 65535:
                QMessageBox.warning(win, "Предупреждение", 
                                   f"Пробег {new_mileage} км превышает максимальное значение 65535 км для данного модуля")
                return
            
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
            elif 'gelly_atlas_2020_24c02' in encoder_name:
                model = 'gelly_atlas_2020_24c02'
            elif 'Prado_93c86_until_2015' in encoder_name:
                model = 'Prado_93c86_until_2015'
            else:
                model = 'default'
            
            print(f"edit_mileage: encoder={encoder_name}, model={model}, new_mileage={new_mileage}, ignore_vin_pin={ignore_vin_pin}")
            
            # Обновляем пробег
            if ignore_vin_pin:
                encoder.update_mileage(file_data, new_mileage, model=model)
                updated_data = encoder.data
                if updated_data is None:
                    QMessageBox.critical(win, "Ошибка", f"Не удалось обновить пробег: данные не получены. Модуль: {encoder_name}")
                    return
            else:
                updated_data = encoder.update_mileage(file_data, new_mileage, model=model)
                if updated_data is None:
                    QMessageBox.critical(win, "Ошибка", f"Не удалось обновить пробег. Модуль: {encoder_name}")
                    return
                
                if new_vin and new_vin != current_vin:
                    updated_data = encoder.set_vin(updated_data, new_vin)
                    if updated_data is None:
                        QMessageBox.critical(win, "Ошибка", f"Не удалось обновить VIN. Модуль: {encoder_name}")
                        return
                
                if new_pin and new_pin != current_pin:
                    updated_data = encoder.set_pin(updated_data, new_pin)
                    if updated_data is None:
                        QMessageBox.critical(win, "Ошибка", f"Не удалось обновить PIN. Модуль: {encoder_name}")
                        return
            
            # Сохраняем обновленные данные
            file_path = settings.value("last_file")
            with open(file_path, 'wb') as f:
                f.write(updated_data)
            print(f"edit_mileage: Файл сохранён по пути {file_path}")
            
            # Обновляем настройки
            settings.setValue("file_data", updated_data)
            updated_result = encoder.encode(updated_data, model=model)
            print(f"edit_mileage: encode result = {updated_result}")
            settings.setValue("last_mileage", updated_result['mileage'])
            settings.setValue("last_vin", updated_result['VIN'] if not ignore_vin_pin else current_vin)
            settings.setValue("last_pin", updated_result['PIN'] if not ignore_vin_pin else current_pin)
            
            # Сравниваем файлы
            original_data = bytearray(file_data)
            display_hex_comparison(original_data, updated_data, win)
            
            # Отображаем информацию
            show_vin_pin_info(win,
                             settings.value("last_vin", "N/A"),
                             settings.value("last_pin", "N/A"),
                             settings.value("last_mileage", "N/A"))
            
            QMessageBox.information(win, "Успешно",
                                   f"Пробег обновлен: {new_mileage} км" +
                                   (f"\nVIN: {new_vin}\nPIN: {new_pin}" if not ignore_vin_pin else ""))
    except Exception as e:
        QMessageBox.critical(win, "Ошибка", f"Не удалось обновить данные: {str(e)}\nМодуль: {encoder_name}")
        print(f"Error editing data: {str(e)}, Encoder: {encoder_name}, Model: {model}")

def show_vin_pin_info(win, vin, pin, mileage=None):
    try:
        if hasattr(win, 'vinPinContainer'):
            container = win.vinPinContainer
        else:
            raise AttributeError("Контейнер 'vinPinContainer' не найден в форме.")
        
        if hasattr(win, 'info_panel'):
            win.vin_label.setText(f"VIN: {vin}")
            win.pin_label.setText(f"PIN: {pin}")
            if mileage is not None and hasattr(win, 'mileage_label'):
                win.mileage_label.setText(f"Mileage: {mileage} km")
            win.info_panel.show()
        else:
            info_panel = QGroupBox(container)
            info_panel.setFixedSize(300, 150)
            layout = QVBoxLayout()
            
            win.vin_label = QLabel(f"VIN: {vin}")
            win.pin_label = QLabel(f"PIN: {pin}")
            if mileage is not None:
                win.mileage_label = QLabel(f"Mileage: {mileage} km")
                layout.addWidget(win.mileage_label)
            
            layout.addWidget(win.vin_label)
            layout.addWidget(win.pin_label)
            
            info_panel.setLayout(layout)
            info_panel.setStyleSheet("QGroupBox { border: 0px; margin-top: 0px; }")
            
            container_layout = container.layout() or QVBoxLayout(container)
            while container_layout.count():
                item = container_layout.takeAt(0)
                if widget := item.widget():
                    widget.deleteLater()
            
            container_layout.addWidget(info_panel)
            win.info_panel = info_panel
        
        win.info_panel.show()
        win.update()
    except Exception as e:
        print(f"Error in show_vin_pin_info: {str(e)}")

def show_comparison_results(differences, win, settings):
    win.statusBar().showMessage(
        f"Найдено {len(differences)} различий между файлами" if differences
        else "Файлы идентичны, различий не найдено"
    )
    show_vin_pin_info(win,
                     settings.value("last_vin", "N/A"),
                     settings.value("last_pin", "N/A"),
                     settings.value("last_mileage", "N/A"))

def main():
    app = QtWidgets.QApplication([])
    try:
        ui_file = resource_path("untitled_with_edit_mileage.ui")
        win = uic.loadUi(ui_file)
        win.progressBar.setValue(0)
        win.progressBar.setVisible(False)
    except Exception as e:
        print(f"Error loading UI: {str(e)}")
        sys.exit(1)

    tree = win.treeWidget
    settings = QSettings("666", "BLACK_BOX")
    change_color_func = setup_color(win, settings)
    current_encoder = [None]

    def on_tree_item_clicked():
        selected_items = tree.selectedItems()
        if selected_items:
            ecu_name = selected_items[0].text(0)
            encoder = get_encoder(ecu_name)
            current_encoder[0] = encoder
            win.statusBar().showMessage(
                f"Выбран ECU: {ecu_name}, редактор готов к работе" if encoder
                else f"Выбран ECU: {ecu_name}, редактор не найден"
            )
            print(f"on_tree_item_clicked: Selected ECU = {ecu_name}, Encoder = {type(encoder).__name__ if encoder else None}")
            if hasattr(win, 'info_panel'):
                win.vin_label.setText("VIN: N/A")
                win.pin_label.setText("PIN: N/A")
                if hasattr(win, 'mileage_label'):
                    win.mileage_label.setText("Mileage: N/A")
                win.info_panel.hide()
            settings.setValue("last_vin", "N/A")
            settings.setValue("last_pin", "N/A")
            settings.setValue("last_mileage", "N/A")

    win.update_progress = lambda value: (
        win.progressBar.setValue(value),
        win.progressBar.setVisible(value < 100)
    )[1]
    win.show_comparison_results = lambda differences: show_comparison_results(differences, win, settings)

    # Подключение событий
    tree.itemClicked.connect(on_tree_item_clicked)
    win.actionOpen.triggered.connect(lambda: open_file(win, settings, current_encoder))
    win.actionSave.triggered.connect(lambda: save_file(win, settings, current_encoder))
    win.actionColor.triggered.connect(change_color_func)
    win.actionCompare.triggered.connect(lambda: compare_two_files(win))
    win.actionEditMileage.triggered.connect(lambda: edit_mileage(win, settings, current_encoder))
    win.actionCheckUpdate.triggered.connect(lambda: check_for_updates(win))
    if hasattr(win, 'actionYes'):
        win.actionYes.triggered.connect(lambda: auto_update_exe(win))

    # Загрузка данных ECU
    try:
        ecu_file = resource_path("ecu_data.json")
        print(f"Loading ECU data from: {ecu_file}")
        ecu_roots = create_ecu_hierarchy_from_file(ecu_file)
        populate_tree(tree, ecu_roots)
        print(f"Tree item count: {tree.topLevelItemCount()}")
    except Exception as e:
        print(f"Error loading ECU hierarchy: {str(e)}")
        sys.exit(1)

    # Проверка обновлений при запуске
    check_for_updates(win)
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()



    








