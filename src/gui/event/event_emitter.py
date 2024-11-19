from PyQt6.QtCore import Qt, QSettings, QObject, QEvent, pyqtSignal

class EventEmitter(QObject):
    progress_updated = pyqtSignal(int, int)  # current_page, total_pages

    def emit_progress(self, current: int, total: int):
        self.progress_updated.emit(current, total)