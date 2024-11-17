from PyQt6.QtWidgets import (QMainWindow, QMenuBar, QMenu, QSystemTrayIcon,
                             QStyle, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QAction, QKeySequence, QIcon, QColor
from src.gui.dialogs.about_dialog import AboutDialog
from src.gui.dialogs.program_settings_dialog import ProgramSettingsDialog
from src.gui.dialogs.account_settings_dialog import AccountSettingsDialog
from src.gui.dialogs.log_viewer_dialog import LogViewerDialog
from src.core.swan import Swan
from PyQt6.QtWidgets import QApplication
import os


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Swan GUI")
        self.resize(800, 600)

        # 设置菜单栏样式
        # self.setStyleSheet("""
        #      QMenuBar {
        #         border-bottom: 1px solid #f0f0f0;
        #     }
        #     QMenuBar::item {
        #         background-color: transparent;
        #     }
        #     QMenu {
        #         background-color: white;
        #         border-radius: 5px;
        #         border: 1px solid #cccccc;  /* 可选：添加边框替代阴影 */
        #     }
        #     QMenu::item {
        #         background-color: transparent;
        #     }
        # """)
        # 判断是最小化还是退出
        self.force_quit = False
        self.settings = QSettings('swan_gui', 'settings')
        self.is_first_time_hide_tray = False
        # 初始化Swan实例
        self.swan = Swan('./swan.config.toml')

        self._create_menu_bar()
        self._create_status_bar()
        self._setup_tray_icon()

    def _create_menu_bar(self):
        menubar = self.menuBar()

        settings_menu = menubar.addMenu('设置')

        # 程序设置动作
        program_settings_action = QAction('程序设置', self)
        program_settings_action.setShortcut(QKeySequence("Ctrl+E"))
        program_settings_action.triggered.connect(self._show_program_settings)
        settings_menu.addAction(program_settings_action)

        # 账号设置动作
        account_settings_action = QAction('账号设置', self)
        account_settings_action.setShortcut(QKeySequence("Ctrl+R"))
        account_settings_action.triggered.connect(self._show_account_settings)
        settings_menu.addAction(account_settings_action)

        # 日志菜单
        log_menu = menubar.addMenu('日志')
        view_log_action = QAction('查看日志', self)
        view_log_action.setShortcut(QKeySequence("Ctrl+L"))
        view_log_action.triggered.connect(self._show_log_viewer)
        log_menu.addAction(view_log_action)

        # 关于菜单
        about_menu = menubar.addMenu('关于')
        about_action = QAction('关于 Swan', self)
        about_action.triggered.connect(self._show_about_dialog)
        about_menu.addAction(about_action)

    def _create_status_bar(self):
        self.statusBar().showMessage('就绪 - 晚风')

    def _setup_tray_icon(self):
        # 获取系统主题的应用程序图标
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)

        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon(icon, self)
        self.tray_icon.setToolTip('Swan GUI')

        # 创建托盘菜单
        tray_menu = QMenu()

        # 添加显示/隐藏窗口的动作
        show_action = QAction('显示主窗口', self)  # 更清晰的描述
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)

        # 添加分隔符
        tray_menu.addSeparator()

        # 添加查看日志的动作
        view_log_action = QAction('查看日志', self)
        view_log_action.triggered.connect(self._show_log_viewer)
        tray_menu.addAction(view_log_action)

        # 添加分隔符
        tray_menu.addSeparator()

        # 添加退出动作
        quit_action = QAction('彻底退出程序', self)  # 更明确的描述
        quit_action.triggered.connect(self._handle_quit)
        tray_menu.addAction(quit_action)

        # 设置托盘图标的菜单
        self.tray_icon.setContextMenu(tray_menu)

        # 显示托盘图标
        self.tray_icon.show()

        # 连接托盘图标的双击事件
        self.tray_icon.activated.connect(self._handle_tray_activation)

    def _handle_tray_activation(self, reason):
        # 使用整数值进行比较
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()

    def _show_program_settings(self):
        dialog = ProgramSettingsDialog(self.settings, self)
        dialog.exec()

    def _show_account_settings(self):
        dialog = AccountSettingsDialog(self.settings, self)
        dialog.exec()

    def _show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec()

    def _show_log_viewer(self):
        dialog = LogViewerDialog(self.settings, self)
        dialog.exec()

    def _handle_quit(self):
        self.force_quit = True
        self.swan.grace_shutdown()
        self.close()  # 调用继承的方法 `closeEvent`, 但不会彻底关闭
        QApplication.instance().quit()  # 彻底关闭

    def closeEvent(self, event):
        if self.force_quit:  # 如果是强制退出
            event.accept()
        else:  # 如果是普通关闭，最小化到托盘
            if self.tray_icon.isVisible():
                self.hide()
                if self.is_first_time_hide_tray == False:
                    self.tray_icon.showMessage(
                        'Swan GUI', '应用程序已最小化到系统托盘，双击图标可以重新打开窗口。',
                        QSystemTrayIcon.MessageIcon.Information, 2000)
                    self.is_first_time_hide_tray = True
                event.ignore()
            else:
                event.accept()
