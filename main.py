from PyQt5 import QtWidgets, uic 
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QProgressDialog
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QGroupBox, QInputDialog, QDialog, QGridLayout, QPushButton, QSpinBox
import sys
import os
import requests
import webbrowser
from packaging import version

from color import setup_color 
from file import save_file
from tree_setup import populate_tree
from ecu_data import create_ecu_hierarchy_from_file
from encoder_map import get_encoder_for_ecu
from text_highlighting import display_hex_comparison
from file_compare_worker import compare_two_files
from dash_editor import DashEditor

# Локальная версия программы
LOCAL_VERSION = "1.1.3"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/satanada666/Automotive-Binary-File-Editor/main/version.txt"
DOWNLOAD_URL = "https://github.com/satanada666/Automotive-Binary-File-Editor/releases"

class MileageEditDialog(QDialog):
    def __init__(self, parent=None, current_mileage=0):
        super().__init__(parent)
        self.setWindowTitle("Редактирование пробега")
        self.setMinimumWidth(300)
        
        layout = QGridLayout()
        
        layout.addWidget(QLabel("Текущий пробег (км):"), 0, 0)
        self.current_mileage_label = QLabel(str(current_mileage))
        layout.addWidget(self.current_mileage_label, 0, 1)
        
        layout.addWidget(QLabel("Новый пробег (км):"), 1, 0)
        self.new_mileage_spin = QSpinBox()
        self.new_mileage_spin.setRange(0, 999999)
        self.new_mileage_spin.setValue(current_mileage)
        self.new_mileage_spin.setSingleStep(1000)
        layout.addWidget(self.new_mileage_spin, 1, 1)
        
        button_box = QGridLayout()
        self.apply_button = QPushButton("Применить")
        self.apply_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        
        button_box.addWidget(self.apply_button, 0, 0)
        button_box.addWidget(self.cancel_button, 0, 1)
        
        layout.addLayout(button_box, 2, 0, 1, 2)
        
        self.setLayout(layout)
    
    def get_new_mileage(self):
        return self.new_mileage_spin.value()

def resource_path(relative_path):
    try:
        base_path = getattr(sys, '_MEIPASS', None)
        if base_path is None:
            base_path = os.path.abspath(os.path.dirname(__file__))
        full_path = os.path.join(base_path, relative_path)
        print(f"Resolved path for {relative_path}: {full_path}")
        return full_path
    except Exception as e:
        print(f"Error resolving resource path for {relative_path}: {str(e)}")
        sys.exit(1)

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
            process_file_in_chunks(file_name, encoder, win, settings)
        except Exception as e:
            QMessageBox.critical(win, "Ошибка", f"Не удалось открыть файл: {str(e)}")
            print(f"Error opening file: {str(e)}")

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
        if current_mileage == "N/A":
            current_mileage = 0
        try:
            current_mileage = int(current_mileage)
        except:
            current_mileage = 0
        
        dialog = MileageEditDialog(win, current_mileage)
        if dialog.exec_() == QDialog.Accepted:
            new_mileage = dialog.get_new_mileage()
            
            model = 'lacetti_2004' if 'Chevrolet_lacetti_dash_denso' in type(encoder).__name__ else 'Daewoo_Gentra'
            encoder.update_mileage(file_data, new_mileage, model=model)
            
            updated_data = encoder.data
            file_path = settings.value("last_file")
            with open(file_path, 'wb') as f:
                f.write(updated_data)
            print(f"edit_mileage: Файл сохранён по пути {file_path}")
            
            settings.setValue("file_data", updated_data)
            updated_result = encoder.encode(updated_data, model=model)
            settings.setValue("last_mileage", updated_result['mileage'])
            
            original_data = None
            with open(file_path, 'rb') as f:
                original_data = bytearray(f.read())
            
            if original_data:
                display_hex_comparison(original_data, updated_data, win)
            
            show_vin_pin_info(win, 
                             settings.value("last_vin", "N/A"), 
                             settings.value("last_pin", "N/A"), 
                             settings.value("last_mileage", "N/A"))
            
            QMessageBox.information(win, "Успешно", 
                                  f"Пробег изменен с {current_mileage} км на {new_mileage} км")
    except Exception as e:
        QMessageBox.critical(win, "Ошибка", f"Не удалось изменить пробег: {str(e)}")
        print(f"Error editing mileage: {str(e)}")

def process_file_in_chunks(file_name, encoder, win, settings):
    progress = None
    try:
        file_size = os.path.getsize(file_name)
        print(f"process_file_in_chunks: File size = {file_size} bytes")
        if file_size < 2 * 1024 * 1024:
            process_small_file(file_name, encoder, win, settings)
            return

        progress = QProgressDialog("Обработка файла...", "Отмена", 0, 100, win)
        progress.setWindowTitle("Обработка")
        progress.setWindowModality(Qt.WindowModal)
        progress.show()

        with open(file_name, 'rb') as f_in:
            original_data = bytearray(f_in.read())

        modified_data = bytearray(original_data)

        print(f"process_file_in_chunks: Encoder = {type(encoder).__name__}, Data length = {len(modified_data)}")
        try:
            check_result = encoder.check(modified_data)
            print(f"process_file_in_chunks: Check result = {check_result}")
        except Exception as e:
            print(f"process_file_in_chunks: Error in check method: {str(e)}")
            raise
        if not check_result:
            if progress is not None:
                progress.close()
            QMessageBox.warning(win, "Ошибка проверки",
                              "Файл не прошел проверку для выбранного ECU")
            return

        if isinstance(encoder, DashEditor):
            model = 'lacetti_2004' if 'Chevrolet_lacetti_dash_denso' in type(encoder).__name__ else 'Daewoo_Gentra'
            result = encoder.encode(modified_data, model=model)
            current_mileage = result.get('mileage', 0)
            
            new_mileage, ok = QInputDialog.getInt(win, "Введите новый пробег", 
                                                 f"Текущий пробег: {current_mileage} км\nВведите новый пробег (в километрах):", 
                                                 value=current_mileage, min=0, max=999999, step=1000)
            if ok:
                print(f"process_file_in_chunks: Новый пробег = {new_mileage} км")
                encoder.update_mileage(modified_data, new_mileage, model=model)
                result = encoder.encode(modified_data, model=model)
            else:
                print("process_file_in_chunks: Пробег не изменен, используем текущий")
        else:
            result = encoder.encode(modified_data)

        print(f"process_file_in_chunks: Encode result = {result}")
        if isinstance(result, dict):
            if 'VIN' in result and 'PIN' in result:
                settings.setValue("last_vin", result['VIN'])
                settings.setValue("last_pin", result['PIN'])
                print(f"process_file_in_chunks: Saved VIN={result['VIN']}, PIN={result['PIN']} to settings")
            if 'mileage' in result:
                settings.setValue("last_mileage", result['mileage'])
                print(f"process_file_in_chunks: Saved mileage={result['mileage']} to settings")
        else:
            print("process_file_in_chunks: No VIN/PIN/mileage data to save")

        settings.setValue("file_data", modified_data)
        settings.setValue("last_file", file_name)

        if progress is not None:
            progress.close()

        display_hex_comparison(original_data, modified_data, win)

        QMessageBox.information(win, "Успешно",
                              f"Файл {file_name} успешно открыт и отредактирован")
    except Exception as e:
        if progress is not None:
            progress.close()
        QMessageBox.critical(win, "Ошибка", f"Не удалось обработать файл: {str(e)}")
        print(f"Error processing file: {str(e)}")

def process_small_file(file_name, encoder, win, settings):
    file_size = os.path.getsize(file_name)
    print(f"process_small_file: File size = {file_size} bytes")
    with open(file_name, 'rb') as f:
        data = bytearray(f.read())

    original_copy = data[:]

    print(f"process_small_file: Encoder = {type(encoder).__name__}, Data length = {len(data)}")
    try:
        check_result = encoder.check(data)
        print(f"process_small_file: Check result = {check_result}")
    except Exception as e:
        print(f"process_small_file: Error in check method: {str(e)}")
        QMessageBox.critical(win, "Ошибка", f"Ошибка проверки файла: {str(e)}")
        return
    if check_result:
        if isinstance(encoder, DashEditor):
            model = 'lacetti_2004' if 'Chevrolet_lacetti_dash_denso' in type(encoder).__name__ else 'Daewoo_Gentra'
            temp_result = encoder.encode(data, model=model)
            current_mileage = temp_result.get('mileage', 0)
            
            new_mileage, ok = QInputDialog.getInt(win, "Введите новый пробег", 
                                              f"Текущий пробег: {current_mileage} км\nВведите новый пробег (в километрах):", 
                                              value=current_mileage, min=0, max=999999, step=1000)
            if ok:
                print(f"process_small_file: Новый пробег = {new_mileage} км")
                encoder.update_mileage(data, new_mileage, model=model)
                data = encoder.data
                result = encoder.encode(data, model=model)
            else:
                print("process_small_file: Пробег не изменен, используем текущий")
                result = temp_result
        else:
            result = encoder.encode(data)
        
        print(f"process_small_file: Encode result = {result}")
        if isinstance(result, dict):
            if 'VIN' in result and 'PIN' in result:
                settings.setValue("last_vin", result['VIN'])
                settings.setValue("last_pin", result['PIN'])
                print(f"process_small_file: Saved VIN={result['VIN']}, PIN={result['PIN']} to settings")
            if 'mileage' in result:
                settings.setValue("last_mileage", result['mileage'])
                print(f"process_small_file: Saved mileage={result['mileage']} to settings")
        else:
            print("process_small_file: No VIN/PIN/mileage data to save")
        settings.setValue("file_data", data)
        settings.setValue("last_file", file_name)
        display_hex_comparison(original_copy, data, win)
        QMessageBox.information(win, "Успешно",
                              f"Файл {file_name} успешно открыт и отредактирован")
    else:
        QMessageBox.warning(win, "Ошибка проверки",
                          "Файл не прошел проверку для выбранного ECU")

def show_vin_pin_info(win, vin, pin, mileage=None):
    try:
        if hasattr(win, 'vinPinContainer'):
            container = win.vinPinContainer
        else:
            raise AttributeError("Контейнер 'vinPinContainer' не найден в форме. Добавьте его в Qt Designer.")

        if hasattr(win, 'info_panel'):
            win.vin_label.setText(f"VIN: {vin}")
            win.pin_label.setText(f"PIN: {pin}")
            if mileage is not None:
                if hasattr(win, 'mileage_label'):
                    win.mileage_label.setText(f"Mileage: {mileage} km")
                else:
                    win.mileage_label = QLabel(f"Mileage: {mileage} km")
                    win.info_panel.layout().addWidget(win.mileage_label)
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
            
            info_panel.setStyleSheet("""
                QGroupBox {
                    border: 0px;
                    margin-top: 0px;
                }
            """)
            
            container_layout = container.layout()
            if container_layout is None:
                container_layout = QVBoxLayout(container)
                container.setLayout(container_layout)
            else:
                while container_layout.count():
                    item = container_layout.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()
            
            container_layout.addWidget(info_panel)
            win.info_panel = info_panel
        
        win.info_panel.show()
        win.update()
    except Exception as e:
        print(f"Error in show_vin_pin_info: {str(e)}")

def check_for_updates(win):
    try:
        response = requests.get(GITHUB_VERSION_URL)
        response.raise_for_status()
        server_version = response.text.strip()
        print(f"Checking for updates: local={LOCAL_VERSION}, server={server_version}")

        if version.parse(server_version) <= version.parse(LOCAL_VERSION):
            print("No updates available or local version is newer.")
            QMessageBox.information(win, "Обновление",
                                 f"У вас установлена актуальная версия {LOCAL_VERSION}.")
            if hasattr(win, 'actionYes'):
                win.actionYes.setEnabled(False)
        else:
            reply = QMessageBox.question(
                win, "Обновление",
                f"Доступна новая версия {server_version} (текущая: {LOCAL_VERSION}). Обновить?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                download_update(win)
            if hasattr(win, 'actionYes'):
                win.actionYes.setEnabled(True)

    except requests.exceptions.RequestException as e:
        QMessageBox.critical(win, "Ошибка", f"Не удалось проверить обновления: {e}")
        if hasattr(win, 'actionYes'):
            win.actionYes.setEnabled(False)
    except ValueError as e:
        QMessageBox.critical(win, "Ошибка", f"Некорректный формат версии на сервере: {e}")
        if hasattr(win, 'actionYes'):
            win.actionYes.setEnabled(False)

def download_update(win):
    webbrowser.open(DOWNLOAD_URL)
    if hasattr(win, 'actionYes'):
        win.actionYes.setEnabled(False)

def main():
    app = QtWidgets.QApplication([])

    try:
        ui_file = resource_path("untitled.ui")
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
            selected_item = selected_items[0]
            ecu_name = selected_item.text(0)
            encoder = get_encoder_for_ecu(ecu_name)
            current_encoder[0] = encoder
            print(f"on_tree_item_clicked: Selected ECU = {ecu_name}, Encoder = {type(encoder).__name__ if encoder else None}")
            if encoder:
                win.statusBar().showMessage(f"Выбран ECU: {ecu_name}, редактор готов к работе")
            else:
                win.statusBar().showMessage(f"Выбран ECU: {ecu_name}, редактор не найден")

            if hasattr(win, 'info_panel'):
                win.vin_label.setText("VIN: N/A")
                win.pin_label.setText("PIN: N/A")
                if hasattr(win, 'mileage_label'):
                    win.mileage_label.setText("Mileage: N/A")
                win.info_panel.hide()
            settings.setValue("last_vin", "N/A")
            settings.setValue("last_pin", "N/A")
            settings.setValue("last_mileage", "N/A")

    def update_progress(value):
        win.progressBar.setValue(value)
        win.progressBar.setVisible(True)
        if value >= 100:
            win.progressBar.setVisible(False)

    def show_comparison_results(differences, win, settings):
        if differences:
            win.statusBar().showMessage(f"Найдено {len(differences)} различий между файлами")
        else:
            win.statusBar().showMessage("Файлы идентичны, различий не найдено")
        
        vin = settings.value("last_vin", "N/A")
        pin = settings.value("last_pin", "N/A")
        mileage = settings.value("last_mileage", "N/A")
        print(f"show_comparison_results: Retrieved VIN={vin}, PIN={pin}, Mileage={mileage}")
        show_vin_pin_info(win, vin, pin, mileage)

    win.update_progress = update_progress
    win.show_comparison_results = lambda differences: show_comparison_results(differences, win, settings)

    tree.itemClicked.connect(lambda: on_tree_item_clicked())
    win.actionOpen.triggered.connect(lambda: open_file(win, settings, current_encoder))
    win.actionSave.triggered.connect(lambda: save_file(win, settings, current_encoder))
    win.actionColor.triggered.connect(change_color_func)

    if not hasattr(win, 'actionCompare'):
        win.actionCompare = QtWidgets.QAction("Compare", win)
        win.menuFile.addAction(win.actionCompare)

    win.actionCompare.triggered.connect(lambda: compare_two_files(win))

    win.actionEditMileage = QtWidgets.QAction("Edit Mileage", win) 
    win.menuFile.addAction(win.actionEditMileage)
    win.actionEditMileage.triggered.connect(lambda: edit_mileage(win, settings, current_encoder))

    win.actionCheckUpdate.triggered.connect(lambda: check_for_updates(win))

    if hasattr(win, 'actionYes'):
        win.actionYes.triggered.connect(lambda: download_update(win))

    try:
        ecu_file = resource_path("ecu_data.json")
        print(f"Loading ECU data from: {ecu_file}")
        ecu_roots = create_ecu_hierarchy_from_file(ecu_file)
        print(f"ECU roots: {ecu_roots}")
        populate_tree(tree, ecu_roots)
        print(f"Tree item count: {tree.topLevelItemCount()}")
    except Exception as e:
        print(f"Error loading ECU hierarchy: {str(e)}")
        sys.exit(1)

    check_for_updates(win)

    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()