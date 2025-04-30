from PyQt5.QtWidgets import QFileDialog, QMessageBox, QProgressDialog
from PyQt5.QtCore import Qt
from text_highlighting import display_hex_comparison
import sys
import os
import traceback


def compare_two_files(win):
    options = QFileDialog.Options()
    first_file, _ = QFileDialog.getOpenFileName(win, "Выберите первый файл для сравнения", "", "Все файлы (*)", options=options)

    if not first_file:
        return

    second_file, _ = QFileDialog.getOpenFileName(win, "Выберите второй файл для сравнения", "", "Все файлы (*)", options=options)

    if not second_file:
        return

    try:
        # Получаем размеры файлов
        size1 = os.path.getsize(first_file)
        size2 = os.path.getsize(second_file)
        
        # Проверяем размеры файлов
        if size1 != size2:
            QMessageBox.warning(win, "Ошибка сравнения", f"Размеры файлов не совпадают!\nРазмер первого файла: {size1} байт\nРазмер второго файла: {size2} байт")
            win.statusBar().showMessage(f"Сравнение отменено: разные размеры файлов")
            return
            
        # Для больших файлов (более 10 МБ) используем блочное чтение
        if size1 > 10 * 1024 * 1024:
            compare_large_files(first_file, second_file, win)
        else:
            # Для небольших файлов загружаем полностью
            with open(first_file, 'rb') as f:
                original_data = bytearray(f.read())

            with open(second_file, 'rb') as f:
                modified_data = bytearray(f.read())
                
            # Запускаем сравнение
            display_hex_comparison(original_data, modified_data, win)

    except Exception as e:
        error_message = f"Не удалось сравнить файлы: {str(e)}"
        traceback.print_exc()  # ← ВАЖНО: выводит точное место ошибки
        QMessageBox.critical(win, "Ошибка", error_message)
        print(f"Ошибка при сравнении файлов: {error_message}", file=sys.stderr)



def compare_large_files(first_file, second_file, win):
    """Сравнивает большие файлы, загружая их по частям"""
    progress = None  # Инициализация переменной progress вне блока try

    try:
        file_size = os.path.getsize(first_file)

        progress = QProgressDialog("Загрузка файлов для сравнения...", "Отмена", 0, 100, win)
        progress.setWindowTitle("Загрузка файлов")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()

        with open(first_file, 'rb') as f1, open(second_file, 'rb') as f2:
            original_data = bytearray()
            modified_data = bytearray()

            chunk_size = 1024 * 1024
            total_chunks = file_size // chunk_size + (1 if file_size % chunk_size else 0)

            for i in range(total_chunks):
                if progress.wasCanceled():
                    win.statusBar().showMessage("Сравнение отменено")
                    return

                progress.setValue(int((i / total_chunks) * 100))

                original_data.extend(f1.read(chunk_size))
                modified_data.extend(f2.read(chunk_size))

        if progress is not None:  # Проверяем перед использованием
            progress.setValue(100)
            progress.close()

        win.statusBar().showMessage("Начинаем сравнение файлов...")
        display_hex_comparison(original_data, modified_data, win)

    except Exception as e:
        if progress is not None:  # Только если progress уже определена
            progress.close()
        QMessageBox.critical(win, "Ошибка", f"Ошибка при сравнении файлов: {str(e)}")
        print(f"Ошибка при сравнении больших файлов: {str(e)}", file=sys.stderr)