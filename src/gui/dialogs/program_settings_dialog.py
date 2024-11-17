from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                               QLabel, QLineEdit, QPushButton, QFormLayout)
from PyQt6.QtCore import QSettings

class ProgramSettingsDialog(QDialog):
    def __init__(self, settings: QSettings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("程序设置")
        self.setFixedSize(500, 300)
        
        layout = QVBoxLayout()
        
        # 创建表单布局
        form_layout = QFormLayout()
        
        # 从QSettings中加载设置或使用默认值
        self.config_path = QLineEdit(self.settings.value("config_path", "./swan.config.toml"))
        self.log_path = QLineEdit(self.settings.value("log_path", "./logs/swan.log"))
        self.chrome_executable_path = QLineEdit(self.settings.value("chrome_executable_path", ""))
        
        # 添加表单项
        form_layout.addRow("配置文件路径:", self.config_path)
        form_layout.addRow("日志文件路径:", self.log_path)
        form_layout.addRow("Chrome可执行文件路径", self.chrome_executable_path)
        
        layout.addLayout(form_layout)
        
        # 添加按钮
        button_layout = QHBoxLayout()
        save_button = QPushButton("保存")
        cancel_button = QPushButton("取消")
        
        save_button.clicked.connect(self.save_settings)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def save_settings(self):
        # 保存设置到QSettings
        self.settings.setValue("config_path", self.config_path.text())
        self.settings.setValue("log_path", self.log_path.text())
        self.accept()