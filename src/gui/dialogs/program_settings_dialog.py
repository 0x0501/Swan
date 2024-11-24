from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFormLayout, QComboBox,
                             QCheckBox)
from PySide6.QtCore import QSettings, Qt
from src.core.encryption import Encryption
from pyqttoast import Toast, ToastPreset
from PySide6.QtGui import QIntValidator


class ProgramSettingsDialog(QDialog):

    def __init__(self, settings: QSettings, parent=None):
        super().__init__(parent)
        self.settings = settings

        # 从QSettings中加载设置或使用默认值
        self.config_path = QLineEdit(
            self.settings.value('config_path', './swan.config.toml'))
        self.log_path = QLineEdit(
            self.settings.value('log_path', './logs/swan.log'))
        self.chrome_executable_path = QLineEdit(
            self.settings.value('chrome_executable_path', ''))
        self.data_directory = QLineEdit(
            self.settings.value('data_directory', './data'))
        self.encryption_dir_path = QLineEdit(
            self.settings.value('encryption_dir_path', './bin'))
        self.page_maximum = QLineEdit(
            str(self.settings.value('page_maximum', 600, type=int)))
        self.page_maximum.setValidator(QIntValidator())
        self.page_maximum.setPlaceholderText('请输入最大抓取的页数（数字）')

        self.setWindowTitle('程序设置')
        self.setFixedWidth(500)
        self.is_system_tray_state = False
        # 配置需要加密的qsettings
        self.encryption = Encryption(
            self.settings.value('encryption_dir_path', './bin'), self.settings,
            None)
        self.is_encryption_exist = \
            self.encryption.check_encryption_key_status()
        # layout
        layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        encryption_layout = QHBoxLayout()

        # 创建表单布局
        form_layout = QFormLayout()

        # 日志等级
        self.log_level = QComboBox()
        log_level_label = QLabel('日志等级')
        log_level_label.setStyleSheet("QLabel { margin-right: 72px; }")
        self.log_level.addItem("All")
        self.log_level.addItem("Info")
        self.log_level.addItem("Debug")
        self.log_level.addItem("Error")
        self.log_level.addItem("Warning")

        # 是否开启最小化
        self.is_system_tray = QCheckBox()
        self.is_system_tray.setChecked(
            self.settings.value('is_system_tray', type=bool))
        self.is_system_tray.stateChanged.connect(self._on_checkbox_changed)
        is_system_tary_label = QLabel('是否开启最小化')
        # 密钥状态以及刷新密钥
        # self.crypto_status = QText
        encryption_status_label = QLabel(
            f'当前密钥状态:' + ('存在' if self.is_encryption_exist else '密钥文件不存在或已损毁'))
        generate_encryption_key_btn = QPushButton(
            '刷新密钥文件' if self.is_encryption_exist else '生成密钥文件')
        generate_encryption_key_btn.clicked.connect(
            self._refresh_encryption_key)

        # 添加表单项
        form_layout.setVerticalSpacing(10)
        form_layout.addRow('配置文件路径:', self.config_path)
        form_layout.addRow('日志文件路径:', self.log_path)
        form_layout.addRow('最大抓取页数:', self.page_maximum)
        form_layout.addRow('数据存放路径:', self.data_directory)
        form_layout.addRow('加密密钥存放路径:', self.encryption_dir_path)
        form_layout.addRow('Chrome可执行文件路径', self.chrome_executable_path)

        h_layout.addWidget(log_level_label)
        h_layout.addWidget(self.log_level)

        h_layout.addWidget(is_system_tary_label)
        h_layout.addWidget(self.is_system_tray)

        encryption_layout.addWidget(encryption_status_label)
        encryption_layout.addWidget(generate_encryption_key_btn)

        layout.addLayout(form_layout)
        layout.addSpacing(10)
        layout.addLayout(h_layout)
        layout.addSpacing(10)
        layout.addLayout(encryption_layout)

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

    def _refresh_encryption_key(self):
        # initialize Toast
        toast = Toast(self)
        toast.setDuration(2000)
        toast.setPositionRelativeToWidget(self.parent())
        if self.encryption.regenerate_key() != -1:
            toast.setTitle('密钥刷新成功！')
            toast.setText(f'密钥存放位置: {str(self.encryption.key_file)}')
            toast.applyPreset(ToastPreset.SUCCESS)
        else:
            toast.setTitle('密钥刷新失败 :(')
            toast.setText('检查日志看看怎么回事 T_T ~')
            toast.applyPreset(ToastPreset.ERROR)
        # 显示弹窗
        toast.show()

    def save_settings(self):
        # 保存设置到QSettings
        self.settings.setValue('config_path', self.config_path.text())
        self.settings.setValue('log_path', self.log_path.text())
        self.settings.setValue('chrome_executable_path',
                               self.chrome_executable_path.text())
        self.settings.setValue('data_directory', self.data_directory.text())
        self.settings.setValue('is_system_tray',
                               self.is_system_tray.isChecked())
        self.settings.setValue('encryption_dir_path',
                               self.encryption_dir_path.text())
        self.settings.setValue('page_maximum', self.page_maximum.text())
        self.accept()
