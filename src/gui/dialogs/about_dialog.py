import platform
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from src.core.swan import Swan

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于")
        self.setFixedWidth(450)
        layout = QVBoxLayout()
        content_layout = QHBoxLayout()
        
        v_layout = QVBoxLayout()
        
        button_layout = QHBoxLayout()
        
        image_layout = QVBoxLayout()
        
        # 创建图片标签
        image_label = QLabel()
        # 获取原始图片
        original_pixmap = QPixmap(":/images/swan_icon.png")
        
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
        
        image_layout.addWidget(image_label)
        # 添加一些边距，使布局更加美观
        # image_label.setContentsMargins(10, 10, 10, 10)
        
        # 添加软件信息
        title_label = QLabel("Swan")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        version_label = QLabel(f"版本: {Swan.swan_version()}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        description_label = QLabel("Swan 是为了完成这该死的论文开发的程序，能够方便的爬取网络文本。")
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        author_label = QLabel("作者: Elias")
        author_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # 获取操作系统信息
        os_info = f"操作系统: {platform.system()} {platform.version()}"
        os_label = QLabel(os_info)
        os_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        python_info = f"Python版本: {platform.python_version()} ({platform.python_compiler()})"
        python_label = QLabel(python_info)
        python_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        build_date = f"编译日期: 2024.11.16"
        build_date_label = QLabel(build_date)
        build_date_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # 添加确定按钮
        ok_button = QPushButton("确定")
        ok_button.setMinimumHeight(30)
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        # 将所有控件添加到布局中
        # v_layout.addWidget(title_label)
        v_layout.addWidget(description_label)
        v_layout.addSpacing(2)
        v_layout.addWidget(version_label)
        v_layout.addSpacing(2)
        v_layout.addWidget(author_label)
        v_layout.addSpacing(2)
        v_layout.addWidget(os_label)
        v_layout.addSpacing(2)
        v_layout.addWidget(build_date_label)
        v_layout.addSpacing(2)
        v_layout.addWidget(python_label)
        v_layout.addStretch()

        image_layout.addStretch()
        image_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addLayout(image_layout)
        content_layout.addLayout(v_layout)
  
        layout.addWidget(title_label)
        layout.addLayout(content_layout)
        layout.addSpacing(20)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)