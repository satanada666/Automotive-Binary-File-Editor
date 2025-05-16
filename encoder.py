import os
import shutil
from typing import Optional
from PyQt5.QtWidgets import QDialog

class Encoder:
    def __init__(self):
        self.size_min: int = -1
        self.size_max: int = -1

    def encode(self, buffer: bytearray) -> Optional[dict]:
        """Базовый метод кодирования. Переопределяется в наследниках."""
        pass

    def check(self, buffer: bytearray) -> bool:
        """Проверяет допустимость буфера данных."""
        return self._check_size(buffer)

    def _check_size(self, buffer: bytearray) -> bool:
        """Проверяет размер буфера данных."""
        size = len(buffer)
        if self.size_min >= 0:
            if self.size_min == self.size_max and size != self.size_min:
                print(f"Размер файла не совпадает: {size} != {self.size_min}")
                return False
            elif size < self.size_min:
                print(f"Файл слишком мал: {size} < {self.size_min}")
                return False
        if self.size_max >= 0 and size > self.size_max:
            print(f"Файл слишком большой: {size} > {self.size_max}")
            return False
        return True

    def process_large_file(self, file_path: str, output_path: Optional[str] = None, progress_callback=None) -> bool:
        """Обрабатывает большой файл по частям."""
        if not os.path.exists(file_path):
            print(f"Ошибка: Файл {file_path} не найден.")
            return False

        try:
            file_size = os.path.getsize(file_path)
            if file_size < 5 * 1024 * 1024:
                return self.transform_file(file_path, output_path)
            
            if output_path is None:
                temp_path = file_path + '.temp'
                backup_path = file_path + '.backup'
                shutil.copy2(file_path, backup_path)
                final_path = file_path
            else:
                temp_path = output_path + '.temp'
                final_path = output_path
            
            shutil.copy2(file_path, temp_path)
            
            with open(temp_path, 'r+b') as f:
                f.seek(0)
                buffer = bytearray(f.read())
                
                if not self.check(buffer):
                    os.remove(temp_path)
                    print("Файл не прошел проверку")
                    return False
                
                result = self.encode(buffer)
                
                f.seek(0)
                f.write(buffer)
                f.truncate()
            
            if os.path.exists(final_path) and final_path != file_path:
                os.remove(final_path)
            shutil.move(temp_path, final_path)
            
            print(f"Файл успешно преобразован и сохранен в {final_path}")
            return True
            
        except Exception as e:
            print(f"Ошибка при обработке большого файла: {e}")
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
            return False

    def transform_file(self, input_path: str, output_path: Optional[str] = None) -> bool:
        """Преобразует файл стандартным способом."""
        if not os.path.exists(input_path):
            print(f"Ошибка: Файл {input_path} не найден.")
            return False

        try:
            with open(input_path, 'rb') as f:
                buffer = bytearray(f.read())

            if not self.check(buffer):
                print("Файл не прошел проверку")
                return False

            if output_path is None:
                self.create_backup(input_path)
                output_path = input_path

            self.encode(buffer)

            with open(output_path, 'wb') as f:
                f.write(buffer)

            print(f"Файл успешно преобразован и сохранен в {output_path}")
            return True

        except Exception as e:
            print(f"Ошибка при обработке файла: {e}")
            return False

    def create_backup(self, file_path: str) -> str:
        """Создает резервную копию файла."""
        backup_path = file_path + '.backup'
        shutil.copy2(file_path, backup_path)
        print(f"Создана резервная копия: {backup_path}")
        return backup_path

class eeprom(Encoder):
    """Подкласс для работы с EEPROM."""
    def __init__(self):
        super().__init__()

class srs(Encoder):
    """Подкласс для работы с SRS."""
    def __init__(self):
        super().__init__()