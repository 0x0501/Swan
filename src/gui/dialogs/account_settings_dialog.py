from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFormLayout, QFrame)
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QFont
from src.core.encryption import Encryption


class AccountSettingsDialog(QDialog):

    def __init__(self, settings: QSettings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("账号设置")
        self.setFixedSize(300, 500)

        # 账号密码项
        self.encryption = Encryption(
            self.settings.value('encryption_dir_path', './bin'), self.settings,
            None)

        layout = QVBoxLayout()

        # 字体加粗
        font = QFont()
        font.setBold(True)
        font.setWeight(QFont.Weight.Bold)
        # 创建表单布局（大众点评）
        dzdp_form_layout = QFormLayout()
        dzdp_label = QLabel("大众点评账号配置")
        dzdp_label.setFont(font)

        # 从QSettings中加载设置或使用默认值
        self.dzdp_username = QLineEdit(self.settings.value(
            "dzdp_username", ""))
        self.dzdp_password = QLineEdit(
            self.encryption.get_encrypted("dzdp_password", ""))
        self.dzdp_password.setEchoMode(QLineEdit.EchoMode.Password)

        # 添加表单项
        dzdp_form_layout.addRow("用户名:", self.dzdp_username)
        dzdp_form_layout.addRow("密码:", self.dzdp_password)
        dzdp_form_layout.setContentsMargins(0, 0, 0, 10)

        # 创建表单布局（携程）
        xiecheng_form_layout = QFormLayout()
        xiecheng_label = QLabel("携程账号配置")
        xiecheng_label.setFont(font)

        # 从QSettings中加载设置或使用默认值
        self.xiecheng_username = QLineEdit(
            self.settings.value("xiecheng_username", ""))
        self.xiecheng_password = QLineEdit(
            self.encryption.get_encrypted("xiecheng_password", ""))
        self.xiecheng_password.setEchoMode(QLineEdit.EchoMode.Password)

        # 添加表单项
        xiecheng_form_layout.addRow("用户名:", self.xiecheng_username)
        xiecheng_form_layout.addRow("密码:", self.xiecheng_password)
        xiecheng_form_layout.setContentsMargins(0, 0, 0, 10)

        # 创建表单布局（小红书）
        red_form_layout = QFormLayout()
        red_label = QLabel("小红书账号配置")
        red_label.setFont(font)

        # 从QSettings中加载设置或使用默认值
        self.red_username = QLineEdit(self.settings.value("red_username", ""))
        self.red_password = QLineEdit(
            self.encryption.get_encrypted("red_password", ""))
        self.red_password.setEchoMode(QLineEdit.EchoMode.Password)

        # 添加表单项
        red_form_layout.addRow("用户名:", self.red_username)
        red_form_layout.addRow("密码:", self.red_password)

        # 大众点评
        layout.addWidget(dzdp_label)
        layout.addSpacing(5)
        layout.addLayout(dzdp_form_layout)
        layout.addWidget(self.divider())

        # 携程
        layout.addWidget(xiecheng_label)
        layout.addSpacing(5)
        layout.addLayout(xiecheng_form_layout)
        layout.addWidget(self.divider())

        # 小红书
        layout.addWidget(red_label)
        layout.addSpacing(5)
        layout.addLayout(red_form_layout)

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

    def divider(a) -> QFrame:
        # 分割线
        line = QFrame()
        line.setStyleSheet("""
            QFrame {
                background-color: #fafafa;
            }
                           """)
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setContentsMargins(5, 20, 5, 20)
        return line

    def save_settings(self):
        # 保存设置到QSettings
        # 大众点评
        self.settings.setValue("dzdp_username", self.dzdp_username.text())
        self.encryption.set_encrypted("dzdp_password",
                                      self.dzdp_password.text())

        # 携程
        self.settings.setValue("xiecheng_username",
                               self.xiecheng_username.text())
        self.encryption.set_encrypted("xiecheng_password",
                                      self.xiecheng_password.text())

        # 小红书
        self.settings.setValue("red_username", self.red_username.text())
        self.encryption.set_encrypted("red_password", self.red_password.text())

        # print('所有Key: %s' % self.settings.allKeys())
        # print('大众点评用户名: %s' % self.settings.value('dzdp_username'))
        # print('大众点评密码（加密）: %s' % self.settings.value('dzdp_password'))
        # print('携程密码 (加密): %s' % self.settings.value('xiecheng_password'))
        # print('小红书密码 (加密): %s' % self.settings.value('red_password'))
        # print('大众点评密码（解密）: %s' % self.encryption.get_encrypted('dzdp_password'))
        # print('小红书密码 (解密): %s ' % self.encryption.get_encrypted('red_password'))
        # 关闭事件
        self.accept()
