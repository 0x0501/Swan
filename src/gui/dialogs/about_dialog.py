import os
import platform
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于")
        self.setFixedSize(400, 270)
        
        layout = QVBoxLayout()
        
        # 添加软件信息
        title_label = QLabel("Swan (天鹅)")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        version_label = QLabel("版本: 1.0.0")
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
        
        # 将所有控件添加到布局中
        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addSpacing(2)
        layout.addWidget(version_label)
        layout.addSpacing(2)
        layout.addWidget(author_label)
        layout.addSpacing(2)
        layout.addWidget(os_label)
        layout.addSpacing(2)
        layout.addWidget(build_date_label)
        layout.addSpacing(2)
        layout.addWidget(python_label)
        layout.addStretch()
        layout.addWidget(ok_button)
  
        
        self.setLayout(layout)