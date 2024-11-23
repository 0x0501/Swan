from PySide6.QtCore import QObject, Signal

class EventEmitter(QObject):
    progress_updated = Signal(int, int)  # current_page, total_pages

    def emit_progress(self, current: int, total: int):
        self.progress_updated.emit(current, total)