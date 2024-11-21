from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtGui import QPixmap, QIcon, QCursor
from PyQt6.QtCore import Qt

class StarterButton(QPushButton):
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        
        # 使用 QPixmap 加载图片
        self.pixmap = pixmap
        
        # 将 QPixmap 转换为 QIcon
        icon = QIcon(pixmap)
        
        # 设置按钮的图标
        self.setIcon(icon)
        
        # 设置图标大小
        self.setIconSize(pixmap.size())
        
        # 去除按钮的默认样式
        self.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                border: none;
                background-color: transparent;
            }
        """)

    def enterEvent(self, event):
        # 当鼠标进入按钮区域时，改变鼠标指针形状
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

    def leaveEvent(self, event):
        # 当鼠标离开按钮区域时，恢复默认鼠标指针形状
        self.unsetCursor()