from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFormLayout, QFrame, QWidget)
from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QFont, QPixmap

class AccountCheckDialog(QDialog):
    def __init__(self, parent: QWidget, message = str) -> None:
        super().__init__(parent)
        
        self.setWindowTitle('账号配置出错啦')
        self.setFixedWidth(400)
        self.assent_button = QPushButton('明白了')
        self.assent_button.setFixedWidth(100)
        self.assent_button.clicked.connect(self._on_assent_button_click)
        layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        h_layout = QHBoxLayout()
        v_layout = QVBoxLayout()
        # 创建图片标签
        image_label = QLabel()
        # 获取原始图片
        original_pixmap = QPixmap(":/images/error_image.png")
        
        # 计算合适的显示大小
        # 获取设备像素比
        device_pixel_ratio = self.devicePixelRatio()
        # 设置期望的显示大小（逻辑像素）
        desired_size = 110
        # 计算实际需要的像素大小
        actual_size = int(desired_size * device_pixel_ratio)
        
        # 使用高质量的缩放方法
        scaled_pixmap = original_pixmap.scaled(
            actual_size, 
            actual_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        # 设置设备像素比，确保在高DPI显示器上清晰显示
        scaled_pixmap.setDevicePixelRatio(device_pixel_ratio)
        
        image_label.setPixmap(scaled_pixmap)
        # 设置固定大小，避免布局拉伸导致的模糊
        # image_label.setFixedSize(desired_size, desired_size)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 添加一些边距，使布局更加美观
        # image_label.setContentsMargins(10, 10, 10, 10)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.assent_button)
        message = QLabel(f'{message}，前往：设置 - 账号设置（Ctrl +R）进行账号配置。')
        message.setWordWrap(True)
        v_layout.addWidget(message)
        v_layout.addStretch()
        h_layout.addWidget(image_label)
        # h_layout.addWidget(message)
        h_layout.addLayout(v_layout)
        layout.addSpacing(20)
        layout.addLayout(h_layout)
        layout.addSpacing(20)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
    def _on_assent_button_click(self):
        self.accept()