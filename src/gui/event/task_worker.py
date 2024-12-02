from PySide6.QtCore import QThread, Signal
from loguru import logger
from src.core.swan import Swan
from src.core.location import Location
import traceback

class TaskWorker(QThread):
    finished = Signal(bool)
    error = Signal(str)
    
    def __init__(self, swan: Swan, location: Location):
        super().__init__()
        self.swan = swan
        # self.location = location
        self.swan.set_location(location)
        logger.debug('Current Location (in task_worker): %s' % self.swan.location)
        self._is_running = True
        self._is_finished = False
        self.finished.connect(lambda result: self._on_finished(result))
        
    def whether_finished(self):
        return self._is_finished
    
    def _on_finished(self, result):
        self._is_finished = result
        
    def set_location(self, location : Location):
        self.swan.set_location(location)
        
    def run(self):
        logger.debug('Swan Status (in task_worker): %s' % self.swan)
        logger.debug('Swan running state (in task_worker): %s' % self._is_running)
        try:
            if self.swan:
                recorder = self.swan.task_dzdp()
                # flush data into disk
                if recorder != None:
                    recorder.record()
                    logger.debug('Swan task has finished (task_worker).')
                else:
                    logger.error('Trying to flush data to file, but recorder is None.')
            self.finished.emit(True)
        except Exception as e:
            self.error.emit(str(e))
            # logger.error(e)
            traceback.print_exc(e)
        finally:
            self._is_running = False
            
    def stop(self):
        self._is_running = False
        if self.swan:
            # 在另一个线程中执行grace_shutdown
            self.swan._running = False  # 立即设置停止标志
            logger.warning('Send `stop` command to Swan (task_worker), signal connected: %s' % self._is_finished)
            # 不要在这里调用wait()，让线程自然结束
            # self.wait()  # 移除这行