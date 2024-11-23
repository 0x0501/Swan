from PySide6.QtGui import QPixmap, QIcon

# 全局变量存储Swan图标
SWAN_ICON = None

class IconLoader():
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def load_icon():
        global SWAN_ICON
        if SWAN_ICON == None:
            pixmap = QPixmap(":/images/swan_icon.png")
            SWAN_ICON = QIcon(pixmap)
            
        return SWAN_ICON