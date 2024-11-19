from PyQt6.QtCore import QThread, pyqtSignal
from src.core.swan import Swan
from src.core.location import Location


class TaskWorker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, swan: Swan, location: Location):
        super().__init__()
        self.swan = swan
        self.location = location
        self._is_running = True
        
    def run(self):
        print('Swan Status: %s' % self.swan)
        print('Swan running state: %s' % self._is_running)
        try:
            if self.swan:
                self.swan.task_dzdp()
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self._is_running = False
            
    def stop(self):
        self._is_running = False
        if self.swan:
            # 在另一个线程中执行grace_shutdown
            self.swan._running = False  # 立即设置停止标志
            # 不要在这里调用wait()，让线程自然结束
            # self.wait()  # 移除这行