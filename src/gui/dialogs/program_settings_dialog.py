from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                               QLabel, QLineEdit, QPushButton, QFormLayout, QComboBox, QCheckBox)
from PyQt6.QtCore import QSettings

class ProgramSettingsDialog(QDialog):
    def __init__(self, settings: QSettings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle('程序设置')
        self.setFixedSize(500, 300)
        self.is_system_tray_state = False
        layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        
        # 创建表单布局
        form_layout = QFormLayout()
        
        # 从QSettings中加载设置或使用默认值
        self.config_path = QLineEdit(self.settings.value('config_path', './swan.config.toml'))
        self.log_path = QLineEdit(self.settings.value('log_path', './logs/swan.log'))
        self.chrome_executable_path = QLineEdit(self.settings.value('chrome_executable_path', ''))
        self.data_directory = QLineEdit(self.settings.value('data_directory', './data'))
        
        # 日志等级
        self.log_level = QComboBox()
        log_level_label = QLabel('日志等级')
        self.log_level.addItem("All")
        self.log_level.addItem("Info")
        self.log_level.addItem("Debug")
        self.log_level.addItem("Error")
        self.log_level.addItem("Warning")
        
        # 是否开启最小化
        self.is_system_tray = QCheckBox()
        self.is_system_tray.setChecked(self.settings.value('is_system_tray', type=bool))
        self.is_system_tray.stateChanged.connect(self._on_checkbox_changed)
        is_system_tary_label = QLabel('是否开启最小化')
        
        # 添加表单项
        form_layout.addRow('配置文件路径:', self.config_path)
        form_layout.addRow('日志文件路径:', self.log_path)
        form_layout.addRow('数据存放路径:', self.data_directory)
        form_layout.addRow('Chrome可执行文件路径', self.chrome_executable_path)
        
        h_layout.addWidget(log_level_label)
        h_layout.addWidget(self.log_level)
        
        h_layout.addWidget(is_system_tary_label)
        h_layout.addWidget(self.is_system_tray)
        
        layout.addLayout(form_layout)
        layout.addLayout(h_layout)
        
        
        # 添加按钮
        button_layout = QHBoxLayout()
        save_button = QPushButton('保存')
        cancel_button = QPushButton('取消')
        
        save_button.clicked.connect(self.save_settings)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _on_checkbox_changed(self, state):
        # self.is_system_tray_state = state
        pass
    
    def save_settings(self):
        # 保存设置到QSettings
        self.settings.setValue('config_path', self.config_path.text())
        self.settings.setValue('log_path', self.log_path.text())
        self.settings.setValue('chrome_executable_path', self.chrome_executable_path.text())
        self.settings.setValue('data_directory', self.data_directory.text())
        self.settings.setValue('is_system_tray', self.is_system_tray.isChecked())
        self.accept()