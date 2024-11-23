from PySide6.QtWidgets import (QApplication, QPushButton, 
                            QDialog, QTextEdit, QVBoxLayout,
                            QHBoxLayout, QLabel)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

class ErrorDialog(QDialog):
    def __init__(self, error_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Oops, Swan崩溃了!")
        self.setMinimumWidth(600)
        self.setMinimumHeight(300)

        # 创建主布局
        main_layout = QVBoxLayout()

        # 创建水平布局来放置图片和文本
        content_layout = QHBoxLayout()

        # 创建图片标签
        image_label = QLabel()
        # 获取原始图片
        original_pixmap = QPixmap(":/images/error_image.png")
        
        # 计算合适的显示大小
        # 获取设备像素比
        device_pixel_ratio = self.devicePixelRatio()
        # 设置期望的显示大小（逻辑像素）
        desired_size = 128
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
        image_label.setContentsMargins(10, 10, 10, 10)
        
        # 创建右侧的垂直布局（用于文本框和按钮）
        right_layout = QVBoxLayout()

        # 创建文本编辑框，用于显示错误信息
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText(error_info)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 创建复制按钮
        copy_button = QPushButton("复制错误信息")
        copy_button.clicked.connect(self.copy_error_info)
        copy_button.setMinimumHeight(30)
        
        # 创建关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        close_button.setMinimumHeight(30)
        
        # 添加按钮到按钮布局
        button_layout.addWidget(copy_button)
        button_layout.addWidget(close_button)
        
        # 将组件添加到右侧布局
        right_layout.addWidget(self.text_edit)
        # right_layout.addLayout(button_layout)
        
        # 将图片和右侧布局添加到水平布局
        content_layout.addWidget(image_label)
        content_layout.addLayout(right_layout)
        
        # 设置图片和文本的比例
        content_layout.setStretchFactor(image_label, 1)
        content_layout.setStretchFactor(right_layout, 4)
        
        # 将水平布局添加到主布局
        main_layout.addLayout(content_layout)
        main_layout.addLayout(button_layout)
        
        # 设置主布局
        self.setLayout(main_layout)

    def copy_error_info(self):
        QApplication.clipboard().setText(self.text_edit.toPlainText())
        self.accept()