from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QProgressBar, QVBoxLayout, QLabel
from PySide6.QtCore import QTimer, Signal, QThread
import sys
from src.gui.event.task_worker import TaskWorker
from src.utils.icon_loader import IconLoader

class StatusChecker(QThread):
    status_changed = Signal(bool)
    
    def __init__(self, task_worker : TaskWorker = None):
        super().__init__()
        # 这里可以添加需要检查的状态变量
        self.is_running = True
        self.task_worker = task_worker
        
    def check_status(self) -> bool:
        # 在这里实现您的状态检测逻辑
        # 返回True表示任务完成，返回False表示任务未完成
        # 这里仅作示例，您需要替换为实际的检测逻辑
        if self.task_worker == None: # 测试使用
            return False
        return self.task_worker.whether_finished()
        
class ExitDialog(QDialog):
    def __init__(self, task_worker : TaskWorker = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Swan")
        self.setWindowIcon(IconLoader.load_icon())
        self.setFixedSize(300, 100)
        self.setStyleSheet("""
            QProgressBar {
                border: 1px solid grey;
                border-radius: 5px;
                text-align: right;
            }
            QProgressBar::chunk {
                background-color: #85a5ff;
                border-top-left-radius: 3px;
                border-bottom-left-radius: 3px;
            }
        """)
        layout = QVBoxLayout()
        
        self.label = QLabel("Swan正在保存数据中,请勿关闭弹窗...(●'◡'●)")
        layout.addWidget(self.label)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # 设置为循环进度条
        layout.addWidget(self.progress)
        
        self.setLayout(layout)
        
        # 创建状态检测器
        self.checker = StatusChecker(task_worker)
        
        # 创建定时器，每500ms检测一次
        self.timer = QTimer(self)
        self.timer.setInterval(500)  # 设置间隔为500毫秒
        self.timer.timeout.connect(self.check_status)
        self.timer.start()
        
    def closeEvent(self, event):
        # 重写关闭事件，使得点击关闭按钮时不会退出应用
        event.ignore()
        self.timer.stop()
        self.hide()
        
    def check_status(self):
        if self.checker.check_status():
            self.timer.stop()
            self.accept()