import sys
from PyQt6.QtWidgets import QApplication
from src.core.global_error_handler import GlobalErrorHandler
from src.gui.main_window import MainWindow


def exception_hook(exc_type, exc_value, exc_traceback):
    """Qt异常钩子"""
    # 不处理键盘中断异常
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    GlobalErrorHandler.handle_exception(exc_type, exc_value, exc_traceback)


def main():
    # 设置全局异常处理
    sys.excepthook = exception_hook

    app = QApplication(sys.argv)
    # 设置Qt的异常处理
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
