from loguru import logger
import traceback
import sys
import traceback
from PyQt6.QtWidgets import QApplication
from src.gui.dialogs.error_dialog import ErrorDialog


class GlobalErrorHandler:

    @staticmethod
    def handle_exception(exc_type, exc_value, exc_traceback):
        """处理未捕获的异常"""
        # 获取错误信息
        error_info = ''.join(
            traceback.format_exception(exc_type, exc_value, exc_traceback))

        # 如果是在Qt应用程序中
        app = QApplication.instance()
        if app is not None:
            # 显示错误对话框, 并且输出到控制台
            logger.error(f'\n {error_info}')
            dialog = ErrorDialog(error_info)
            dialog.exec()
        else:
            # 如果不在Qt应用程序中，使用标准错误输出
            print(error_info, file=sys.stderr)
            logger.error(f'\n {error_info}')
