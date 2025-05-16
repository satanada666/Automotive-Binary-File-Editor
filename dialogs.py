from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QSpinBox, QLineEdit, QPushButton

class MileageVinPinEditDialog(QDialog):
    def __init__(self, parent=None, current_mileage=0, current_vin="не найден", current_pin="не найден"):
        super().__init__(parent)
        self.setWindowTitle("Редактирование пробега, VIN и PIN")
        self.setMinimumWidth(400)
        
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
        
        layout.addWidget(QLabel("Текущий VIN:"), 2, 0)
        self.current_vin_label = QLabel(current_vin)
        layout.addWidget(self.current_vin_label, 2, 1)
        
        layout.addWidget(QLabel("Новый VIN (17 символов, A-Z, 1-9):"), 3, 0)
        self.new_vin_edit = QLineEdit()
        self.new_vin_edit.setText(current_vin if current_vin != "не найден" else "")
        self.new_vin_edit.setMaxLength(17)
        layout.addWidget(self.new_vin_edit, 3, 1)
        
        layout.addWidget(QLabel("Текущий PIN:"), 4, 0)
        self.current_pin_label = QLabel(current_pin)
        layout.addWidget(self.current_pin_label, 4, 1)
        
        layout.addWidget(QLabel("Новый PIN (4 цифры, 1-9):"), 5, 0)
        self.new_pin_edit = QLineEdit()
        self.new_pin_edit.setText(current_pin if current_pin != "не найден" else "")
        self.new_pin_edit.setMaxLength(4)
        layout.addWidget(self.new_pin_edit, 5, 1)
        
        button_box = QGridLayout()
        self.apply_button = QPushButton("Применить")
        self.apply_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        
        button_box.addWidget(self.apply_button, 0, 0)
        button_box.addWidget(self.cancel_button, 0, 1)
        
        layout.addLayout(button_box, 6, 0, 1, 2)
        
        self.setLayout(layout)
    
    def get_new_mileage(self):
        return self.new_mileage_spin.value()
    
    def get_new_vin(self):
        return self.new_vin_edit.text().strip()
    
    def get_new_pin(self):
        return self.new_pin_edit.text().strip()