from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QProgressDialog, QApplication
from PyQt5.QtGui import QTextCursor, QColor, QTextCharFormat, QBrush
from PyQt5.QtWidgets import QDialog

class HexCompareWorker(QThread):
    progressUpdated = pyqtSignal(int)
    comparisonFinished = pyqtSignal(list, bytearray, bytearray)
    blockProcessed = pyqtSignal(int, int, list)

    def __init__(self, original_data: bytearray, modified_data: bytearray):
        super().__init__()
        self.original_data = original_data
        self.modified_data = modified_data
        self.running = True

    def run(self):
        differences = []
        total_bytes = min(len(self.original_data), len(self.modified_data))
        block_size = 32768 if total_bytes < 1024*1024 else 131072
        num_blocks = (total_bytes + block_size - 1) // block_size

        for block in range(num_blocks):
            if not self.running:
                return
            self.progressUpdated.emit(int(block * 100 / num_blocks))
            start = block * block_size
            end = min(start + block_size, total_bytes)
            block_differences = [i for i in range(start, end)
                               if self.original_data[i] != self.modified_data[i]]
            self.blockProcessed.emit(start, end, block_differences)
            differences.extend(block_differences)
            QApplication.processEvents()

        self.progressUpdated.emit(100)
        self.comparisonFinished.emit(differences, self.original_data, self.modified_data)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()

def format_hex_byte(byte_value: int) -> str:
    """Форматирует байт в HEX."""
    return f"{byte_value:02X}"

def format_hex_line(data: bytearray, offset: int, line_length: int = 16) -> str:
    """Форматирует строку из байтов в HEX и ASCII."""
    hex_line = f"{offset:08X}: "
    for i in range(line_length):
        if offset + i < len(data):
            hex_line += format_hex_byte(data[offset + i]) + " "
        else:
            hex_line += "   "
        if i == 7:
            hex_line += " "
    hex_line += " |"
    for i in range(line_length):
        if offset + i < len(data):
            char = data[offset + i]
            hex_line += chr(char) if 32 <= char <= 126 else "."
        else:
            hex_line += " "
    hex_line += "|"
    return hex_line

def highlight_differences(text_edit, line_text: str, line_offset: int, diff_offsets: list, is_original: bool = True):
    """Подсвечивает различия в строке."""
    text_edit.append(line_text)
    cursor = text_edit.textCursor()
    cursor.movePosition(QTextCursor.End)
    cursor.movePosition(QTextCursor.StartOfLine)
    format_diff = QTextCharFormat()
    format_diff.setBackground(QBrush(QColor(255, 200, 200) if is_original else QColor(200, 255, 200)))

    for abs_offset in diff_offsets:
        if (abs_offset // 16) * 16 != line_offset:
            continue
        rel_pos = abs_offset % 16
        hex_start_pos = 10 + (rel_pos * 3) + (1 if rel_pos > 7 else 0)
        cursor.setPosition(cursor.position() - cursor.positionInBlock() + hex_start_pos)
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 2)
        cursor.setCharFormat(format_diff)
        ascii_start_pos = 10 + 48 + 3 + rel_pos
        cursor.setPosition(cursor.position() - cursor.positionInBlock() + ascii_start_pos)
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 1)
        cursor.setCharFormat(format_diff)
    return cursor

def display_hex_comparison(original_data: bytearray, modified_data: bytearray, win):
    """Отображает HEX-сравнение двух файлов."""
    win.originalHexEdit.clear()
    win.modifiedHexEdit.clear()
    win.progressBar.setValue(0)
    win.progressBar.setVisible(True)
    win.comparison_worker = HexCompareWorker(original_data, modified_data)
    win.comparison_worker.progressUpdated.connect(win.update_progress)
    win.comparison_worker.blockProcessed.connect(
        lambda start, end, diffs: process_block(start, end, diffs, original_data, modified_data, win)
    )
    win.comparison_worker.comparisonFinished.connect(
        lambda diffs, orig, mod: win.show_comparison_results(diffs)
    )
    win.comparison_worker.start()

def process_block(start_offset: int, end_offset: int, differences: list, original_data: bytearray, modified_data: bytearray, win):
    """Обрабатывает блок данных и отображает различия."""
    if not differences:
        return
    unique_lines = set()
    for diff_offset in differences:
        line_start = (diff_offset // 16) * 16
        for context in range(-1, 2):
            context_line = line_start + (context * 16)
            if context_line >= 0 and context_line < min(len(original_data), len(modified_data)):
                unique_lines.add(context_line)
    line_offsets = sorted(unique_lines)
    if start_offset > 0:
        win.originalHexEdit.append("...")
        win.modifiedHexEdit.append("...")
    for line_offset in line_offsets:
        orig_line = format_hex_line(original_data, line_offset)
        mod_line = format_hex_line(modified_data, line_offset)
        line_diffs = [diff for diff in differences if line_offset <= diff < line_offset + 16]
        if line_diffs:
            highlight_differences(win.originalHexEdit, orig_line, line_offset, line_diffs, is_original=True)
            highlight_differences(win.modifiedHexEdit, mod_line, line_offset, line_diffs, is_original=False)
        else:
            win.originalHexEdit.append(orig_line)
            win.modifiedHexEdit.append(mod_line)
    win.originalHexEdit.append("")
    win.modifiedHexEdit.append("")
    cursor = win.originalHexEdit.textCursor()
    cursor.movePosition(QTextCursor.End)
    win.originalHexEdit.setTextCursor(cursor)
    cursor = win.modifiedHexEdit.textCursor()
    cursor.movePosition(QTextCursor.End)
    win.modifiedHexEdit.setTextCursor(cursor)
    QApplication.processEvents()