from PyQt6.QtCore import QThread, pyqtSignal
from loguru import logger
from src.core.swan import Swan
from src.core.location import Location


class TaskWorker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, swan: Swan, location: Location):
        super().__init__()
        self.swan = swan
        # self.location = location
        self.swan.set_location(location)
        logger.debug('Current Location (in task_worker): %s' % self.swan.location)
        self._is_running = True
        
    def set_location(self, location : Location):
        self.swan.set_location(location)
        
    def run(self):
        logger.debug('Swan Status (in task_worker): %s' % self.swan)
        logger.debug('Swan running state (in task_worker): %s' % self._is_running)
        try:
            if self.swan:
                recorder = self.swan.task_dzdp()
                # flush data into disk
                recorder.record()
                logger.debug('Swan task has finished (task_worker).')
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
            logger.warning('Send `stop` command to Swan (task_worker), current finished flag: %s' % self.finished.signal)
            # 不要在这里调用wait()，让线程自然结束
            # self.wait()  # 移除这行