from PyQt5 import QtWidgets, uic 
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QProgressDialog
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QGroupBox
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

# Локальная версия программы
LOCAL_VERSION = "1.1.2"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/satanada666/Automotive-Binary-File-Editor/main/version.txt"
DOWNLOAD_URL =   "https://github.com/satanada666/Automotive-Binary-File-Editor/releases" #"https://1024terabox.com/s/1MUcQEV6sEICcsC73kdFjZw"

def resource_path(relative_path):
    """Получает абсолютный путь к ресурсу, работает для dev и для PyInstaller"""
    try:
        base_path = getattr(sys, '_MEIPASS', None)
        if base_path is None:
            base_path = os.path.abspath(os.path.dirname(__file__))
        full_path = os.path.join(base_path, relative_path)
        print(f"Resolved path for {relative_path}: {full_path}")  # Отладка
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
            process_file_in_chunks(file_name, encoder, win, settings)
        except Exception as e:
            QMessageBox.critical(win, "Ошибка", f"Не удалось открыть файл: {str(e)}")
            print(f"Error opening file: {str(e)}")

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

        check_result = encoder.check(modified_data)
        print(f"process_file_in_chunks: Check result = {check_result}")
        if not check_result:
            if progress is not None:
                progress.close()
            QMessageBox.warning(win, "Ошибка проверки",
                              "Файл не прошел проверку для выбранного ECU")
            return

        result = encoder.encode(modified_data)
        print(f"process_file_in_chunks: Encode result = {result}")
        if isinstance(result, dict) and 'VIN' in result and 'PIN' in result:
            settings.setValue("last_vin", result['VIN'])
            settings.setValue("last_pin", result['PIN'])
            print(f"process_file_in_chunks: Saved VIN={result['VIN']}, PIN={result['PIN']} to settings")
            
        else:
            print("process_file_in_chunks: No VIN/PIN data to save")

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

    check_result = encoder.check(data)
    print(f"process_small_file: Check result = {check_result}")
    if check_result:
        result = encoder.encode(data)
        print(f"process_small_file: Encode result = {result}")
        if isinstance(result, dict) and 'VIN' in result and 'PIN' in result:
            settings.setValue("last_vin", result['VIN'])
            settings.setValue("last_pin", result['PIN'])
            print(f"process_small_file: Saved VIN={result['VIN']}, PIN={result['PIN']} to settings")
            

        else:
            print("process_small_file: No VIN/PIN data to save")
        settings.setValue("file_data", data)
        settings.setValue("last_file", file_name)
        display_hex_comparison(original_copy, data, win)
        QMessageBox.information(win, "Успешно",
                              f"Файл {file_name} успешно открыт и отредактирован")
    else:
        QMessageBox.warning(win, "Ошибка проверки",
                          "Файл не прошел проверку для выбранного ECU")

def show_vin_pin_info(win, vin, pin):
    try:
        if hasattr(win, 'vinPinContainer'):
            container = win.vinPinContainer
        else:
            raise AttributeError("Контейнер 'vinPinContainer' не найден в форме. Добавьте его в Qt Designer.")

        if hasattr(win, 'info_panel'):
            win.vin_label.setText(f"VIN: {vin}")
            win.pin_label.setText(f"PIN: {pin}")
            win.info_panel.show()
        else:
            info_panel = QGroupBox(container)
            info_panel.setFixedSize(300, 100)
            layout = QVBoxLayout()
            
            win.vin_label = QLabel(f"VIN: {vin}")
            win.pin_label = QLabel(f"PIN: {pin}")
            
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
            if encoder:
                win.statusBar().showMessage(f"Выбран ECU: {ecu_name}, редактор готов к работе")
            else:
                win.statusBar().showMessage(f"Выбран ECU: {ecu_name}, редактор не найден")

            # Очищаем info_panel при смене модуля
            if hasattr(win, 'info_panel'):
                win.vin_label.setText("VIN: N/A")
                win.pin_label.setText("PIN: N/A")
                win.info_panel.hide()
            settings.setValue("last_vin", "N/A")
            settings.setValue("last_pin", "N/A")

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
        print(f"show_comparison_results: Retrieved VIN={vin}, PIN={pin} from settings")
        show_vin_pin_info(win, vin, pin)

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

    # Connect the Check_update action to the check_for_updates function
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

    # Initial check for updates when the application starts
    check_for_updates(win)

    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()