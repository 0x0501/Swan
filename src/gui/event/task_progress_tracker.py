# 任务进度追踪器
from src.gui.event.event_emitter import EventEmitter


class TaskProgressTracker:
    def __init__(self, emitter: EventEmitter):
        self.emitter = emitter
        self._current_page = 0
        self._total_pages = 0

    @property
    def current_page(self) -> int:
        return self._current_page

    @current_page.setter
    def current_page(self, value: int):
        self._current_page = value
        self.emitter.emit_progress(self._current_page, self._total_pages)

    @property
    def total_pages(self) -> int:
        return self._total_pages

    @total_pages.setter
    def total_pages(self, value: int):
        self._total_pages = value
        self.emitter.emit_progress(self._current_page, self._total_pages)