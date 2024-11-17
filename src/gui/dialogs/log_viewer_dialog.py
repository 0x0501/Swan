import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
                            QPushButton, QLabel, QMessageBox, QSpacerItem, 
                            QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, QSettings
from PyQt6.QtGui import QClipboard, QTextCursor
from PyQt6.QtWidgets import QApplication

class LogViewerDialog(QDialog):
    def __init__(self, settings: QSettings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("日志查看器")
        self.resize(800, 600)
        self.settings = settings
        
        # 创建主布局
        layout = QVBoxLayout()
        
        # 创建工具栏布局
        toolbar_layout = QHBoxLayout()
        
        # 创建复制按钮
        copy_button = QPushButton("一键复制", self)
        copy_button.clicked.connect(self._copy_log_content)
        toolbar_layout.addWidget(copy_button)
        
        # 创建刷新按钮
        refresh_button = QPushButton("刷新", self)
        refresh_button.clicked.connect(self._load_log_content)
        toolbar_layout.addWidget(refresh_button)
        
        # 清除日志按钮
        clear_button = QPushButton("清除",self)
        clear_button.clicked.connect(self._clear_log_content)
        toolbar_layout.addWidget(clear_button)
        
        # 添加弹性空间
        toolbar_layout.addSpacerItem(
            QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )
        
        # 添加自动刷新选项
        self.auto_refresh = False
        self.auto_refresh_button = QPushButton("启用自动刷新 (5s)", self)
        self.auto_refresh_button.setCheckable(True)
        self.auto_refresh_button.clicked.connect(self._toggle_auto_refresh)
        toolbar_layout.addWidget(self.auto_refresh_button)
        
        # 添加工具栏到主布局
        layout.addLayout(toolbar_layout)
        
        # 创建日志文本框
        self.log_text = QTextEdit(self)
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        font = self.log_text.font()
        font.setFamily("Courier New")  # 使用等宽字体
        self.log_text.setFont(font)
        layout.addWidget(self.log_text)
        
        # 创建底部状态布局
        status_layout = QHBoxLayout()
        self.status_label = QLabel("", self)
        status_layout.addWidget(self.status_label)
        layout.addLayout(status_layout)
        
        self.setLayout(layout)
        
        # 设置定时器用于自动刷新
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self._load_log_content)
        
        # 加载初始日志内容
        self._load_log_content()
        
    def _clear_log_content(self):
        log_path = self.settings.value("log_path", "./logs/swan.log")
        try:
            # 清空日志
            with open(log_path, 'w', encoding='utf-8') as file:
                file.close()
                self.log_text.setText("")
        except Exception as e:
            self.log_text.setPlainText("清理文件失败， 原因: %s" % e)
            self.status_label.setText("错误：无法清理日志文件")
                
        
    def _load_log_content(self):
        # 加载日志路径
        log_path = self.settings.value("log_path", "./logs/swan.log")
        
        try:
            if not os.path.exists(log_path):
                self.log_text.setPlainText("日志文件不存在：" + log_path)
                self.status_label.setText("错误：找不到日志文件")
                return
                
            with open(log_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.log_text.setPlainText(content)
                
                # 滚动到底部
                cursor = self.log_text.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.log_text.setTextCursor(cursor)
                
                # 更新状态
                size = os.path.getsize(log_path)
                self.status_label.setText(
                    f"日志文件大小: {self._format_size(size)} | 上次更新时间: "
                    f"{self._format_time(os.path.getmtime(log_path))}"
                )
                
        except Exception as e:
            self.log_text.setPlainText(f"读取日志文件时发生错误：{str(e)}")
            self.status_label.setText("错误：无法读取日志文件")
            
    def _copy_log_content(self):
        content = self.log_text.toPlainText()
        
        # 不能直接实例化
        clipboard = QApplication.clipboard()
        clipboard.setText(content)
        
        # 显示提示消息
        QMessageBox.information(
            self,
            "复制成功",
            "日志内容已复制到剪贴板",
            QMessageBox.StandardButton.Ok
        )
        
    def _toggle_auto_refresh(self, checked):
        if checked:
            self.auto_refresh_button.setText("禁用自动刷新")
            self.refresh_timer.start(5000)  # 每5秒刷新一次
        else:
            self.auto_refresh_button.setText("启用自动刷新 (5s)")
            self.refresh_timer.stop()
            
    def _format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"
        
    def _format_time(self, timestamp):
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
    def closeEvent(self, event):
        # 停止自动刷新定时器
        self.refresh_timer.stop()
        event.accept()
        
    def showEvent(self, event):
        # 当对话框显示时重新加载日志
        self._load_log_content()
        event.accept()