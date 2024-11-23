from PySide6.QtWidgets import (QMainWindow, QMenu, QSystemTrayIcon,
                             QStyle, QStatusBar,
                             QListView)
from PySide6.QtCore import Qt, QSettings, QTimer, QSize, QFile
from PySide6.QtGui import QAction, QKeySequence, QIcon, QPixmap
from loguru import logger
from pathlib import Path
from src.core.encryption import Encryption
from src.core.location import Location
from src.gui.dialogs.about_dialog import AboutDialog
from src.gui.dialogs.csv_table_viewer import CSVViewer
from src.gui.dialogs.program_settings_dialog import ProgramSettingsDialog
from src.gui.dialogs.account_settings_dialog import AccountSettingsDialog
from src.gui.dialogs.log_viewer_dialog import LogViewerDialog
from src.core.swan import Swan
from PySide6.QtWidgets import QApplication, QVBoxLayout, QLabel, QPushButton, QProgressBar, QWidget, QHBoxLayout, QComboBox
from src.gui.event.task_progress_tracker import TaskProgressTracker
from src.gui.event.event_emitter import EventEmitter
from src.gui.event.task_worker import TaskWorker
from pyqttoast import Toast, ToastPreset, ToastPosition
from src.utils.text import load_json
from src.utils.random_selector import RandomUniqueSelector
from src.gui.widgets.starter_button import StarterButton
from src.core.platform import Platform
from src.gui.dialogs.account_check_dialog import AccountCheckDialog
from src.gui.resources import resources
from os import getenv

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        
        profile = "Ming" if getenv("APP_PROFILE") == "ming" else ""
        if profile != '':
            self.setWindowTitle(f"Swan - {profile}")
        else:
            self.setWindowTitle('Swan')
        
        self.resize(800, 600)
        self.next_saying = ''
        # 设置状态栏
        self.statusBar: QStatusBar = QStatusBar()

        # 新增分别的状态栏，一个用于显示状态，一个用于通知
        self.statusBar_info = QLabel()
        self.statusBar_info.setStyleSheet("""
            QLabel {
                font-size: 10pt;
                margin-top: 0px;
                padding-left: 5px;
                padding-right: 5px;
            }
        """)
        self.statusBar_info.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.statusBar_extra = QLabel()
        self.statusBar_extra.setStyleSheet("""
            QLabel {
                font-size: 10pt;
                margin-top: 0px;
                padding-left: 5px;
                padding-right: 5px;
            }
        """)
        self.statusBar_extra.setVisible(False)
        self.statusBar.addWidget(self.statusBar_info)
        self.statusBar.addWidget(self.statusBar_extra)

        self.setStatusBar(self.statusBar)
        # 设置菜单栏样式
        self.setStyleSheet("""
            QMenuBar {
                border-bottom:1px solid #d9d9d9;
                font-size: 10pt;
                padding: 0;
                margin: 0;
            }
            QMenuBar::item {
                padding-top: 5px;
                padding-left: 15px;
                padding-right: 15px;
                padding-bottom: 5px;
                font-size: 10pt;
                background: transparent;  /* 确保背景透明 */
            }
            QMenuBar::item::selected, QMenuBar::item::hover  {
                color: black;
                background-color: #f0f0f0;
                font-size: 10pt;
                padding: 5px 15px;  /* 确保悬停时padding不变 */
            }
            QMenu {
                color:black;
                background-color:white; 
                border-radius:0;
                font-size: 10pt;
                border:1px solid #bbbbbb;
            }
            QMenu::item {
                padding: 4px 20px;
            }
            QMenu::item::text {
                margin: 5px 2px;
            }

            QMenu::item:selected { 
                color:#1aa3ff;
                background-color: #e5f5ff;
            }
            QMenu::separator{
                height:10px;
                background:#bbbbbb;
                margin:5px;
                margin-left:10px;
                margin-right:10px;
            }
        """)
        # 判断是最小化还是退出
        self.settings = QSettings('swan_gui', 'settings')
        self.encryption = Encryption(self.settings.value('encryption_dir_path', './bin'), self.settings, None)
        self.force_quit = not self.settings.value('is_system_tray', type=bool)
        self.is_first_time_hide_tray = False
        # 初始化Swan实例, 在Launch中再赋值
        self.swan = None
        self.task_worker = None

        self._create_menu_bar()
        self._create_status_bar()
        self._setup_tray_icon()
        self._update_status_bar_extra()
        # setting up progress tracker
        self.emitter = EventEmitter()
        self.progress_tracker = TaskProgressTracker(self.emitter)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Top row with comboboxes
        top_row = QHBoxLayout()

        # Left combobox (Locations)
        self.location_combo = QComboBox()
        self.location_combo.addItems(['束河古镇', '白沙古镇'])
        self.location_combo.setStyleSheet("""
            QComboBox {
                min-height: 30px;
                padding-left: 10px;
                padding-right: 10px;
            }
            QComboBox QAbstractItemView::item {
                min-height: 30px;
                min-width: 60px;
            }
            """)
        self.location_combo.setView(QListView())
        self.location_combo.setMinimumWidth(200)  # 设置最小宽度
        top_row.addWidget(self.location_combo)

        # Add spacing between comboboxes
        top_row.addStretch()

        # Right combobox (可以根据需要添加其他选项)
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(['大众点评（美团）'])
        self.platform_combo.setStyleSheet("""
            QComboBox {
                min-height: 30px;
            }
            QComboBox QAbstractItemView::item {
                min-height: 30px;
                min-width: 60px;
            }
            """)
        self.platform_combo.setMinimumWidth(200)  # 设置最小宽度
        top_row.addWidget(self.platform_combo)

        main_layout.addLayout(top_row)

        # Middle row with image and button
        middle_row = QHBoxLayout()

        # Image container
        image_container = QWidget()
        image_layout = QVBoxLayout(image_container)

        # Image
        original_pixmap = QPixmap(":/images/starter_image.png")

        # 计算合适的显示大小
        # 获取设备像素比
        device_pixel_ratio = self.devicePixelRatio()
        # 设置期望的显示大小（逻辑像素）
        desired_size = 256
        # 计算实际需要的像素大小
        actual_size = int(desired_size * device_pixel_ratio)

        # 使用高质量的缩放方法
        scaled_pixmap = original_pixmap.scaled(
            actual_size, actual_size, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        # 设置设备像素比，确保在高DPI显示器上清晰显示
        scaled_pixmap.setDevicePixelRatio(device_pixel_ratio)
        csv_shortcut_icon = QIcon(scaled_pixmap)

        # 创建开始按钮
        starter_button = StarterButton(scaled_pixmap)
        starter_button.setIcon(csv_shortcut_icon)
        # image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        starter_button.setIconSize(QSize(256, 256))
        starter_button.clicked.connect(self._csv_shortcut)
        # image_label.setFixedHeight(desired_size)
        image_layout.addWidget(starter_button)
        middle_row.addWidget(image_container)

        # Button container
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)

        # Start button
        self.start_button = QPushButton('启动')
        self.start_button.setMinimumHeight(50)  # 设置按钮高度
        self.start_button.setMinimumWidth(150)
        self.start_button.clicked.connect(self._start_swan)
        # self.start_button.clicked.connect(self._test_update_progress)
        button_layout.addWidget(self.start_button)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Cancel button
        self.cancel_button = QPushButton('取消')
        self.cancel_button.setMinimumHeight(50)
        self.start_button.setMinimumWidth(150)
        self.cancel_button.clicked.connect(self._cancel_swan)
        self.cancel_button.setEnabled(False)  # Initially disabled

        button_layout.addWidget(self.cancel_button)

        middle_row.addWidget(button_container)
        main_layout.addLayout(middle_row)

        # Add spacing before progress bar
        main_layout.addSpacing(20)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setOrientation(Qt.Orientation.Horizontal)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setFixedHeight(20)  # 设置进度条高度
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid grey;
                border-radius: 5px;
                text-align: right;
            }
            QProgressBar::chunk {
                background-color: #4096ff;
                border-top-left-radius: 3px;
                border-bottom-left-radius: 3px;
            }
        """)
        # Hide progress bar
        self.progress_bar.setVisible(False)
        ########### insert layout ###########
        main_layout.addWidget(self.progress_bar)
        self.emitter.progress_updated.connect(self._update_progress)
        # Add bottom spacing
        main_layout.addSpacing(20)
        
        # check whether sayings file exist
        logger.debug("Resource file exists:", QFile(':/strings/sayings.json').exists())

    def _create_menu_bar(self):
        menubar = self.menuBar()
        # menubar.setWindowFlags(Qt.WindowType.NoDropShadowWindowHint
        #                        | Qt.WindowType.FramelessWindowHint)
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

        # 查看菜单
        view_menu = menubar.addMenu('查看')
        view_log_action = QAction('查看日志', self)
        view_log_action.setShortcut(QKeySequence("Ctrl+L"))
        view_log_action.triggered.connect(self._show_log_viewer)
        view_menu.addAction(view_log_action)
        # view_menu.enterEvent = lambda e : self._create_status_bar

        # CSV阅读器
        csv_viewer_action = QAction('CSV阅读器', self)
        csv_viewer_action.setShortcut(QKeySequence("Ctrl+P"))
        csv_viewer_action.triggered.connect(
            lambda: self._show_csv_viewer_dialog())
        view_menu.addAction(csv_viewer_action)

        # 关于菜单
        about_menu = menubar.addMenu('关于')
        about_action = QAction('关于 Swan', self)
        about_action.triggered.connect(self._show_about_dialog)
        about_menu.addAction(about_action)

    def _csv_shortcut(self):
        # Swan正在运行
        if self.swan != None and self.swan.is_running():
            data_file = Path(self.settings.value(
                'data_directory', './data')).joinpath('dazhongdianping.csv')
            print(data_file)
            self._show_csv_viewer_dialog(data_file)
        else:
            # Swan没有运行
            self._show_csv_viewer_dialog()

    def _create_status_bar(self):
        self._update_status_bar_info('Swan已就绪 - 晚风吹起你鬓间的白发，抚平回忆留下的疤~',
                                     stick_to=False)

    def _update_status_bar_info(self,
                                text: str,
                                million_sec: int = 5000,
                                stick_to: bool = False):
        self.statusBar_info.setText(text)
        self.statusBar_info.setVisible(True)

        def clear_content(status_bar_label: QLabel):
            status_bar_label.setText('')
            status_bar_label.setVisible(False)

        if stick_to == False:
            # 单次触发
            self.status_bar_info_timer = QTimer(self)
            self.status_bar_info_timer.setSingleShot(True)
            self.status_bar_info_timer.timeout.connect(
                lambda: clear_content(self.statusBar_info))
            # 默认三秒消失
            self.status_bar_info_timer.start(million_sec)

    # 自更新status bar
    def _update_status_bar_extra(self, million_sec: int = 5000):

        if hasattr(self, 'saying') == False and hasattr(
                self, 'random_saying') == False:
            saying = load_json(':/strings/sayings.json')['sayings']
            self.random_saying = RandomUniqueSelector(saying)

        def change_saying(status_bar_label: QLabel):
            self.next_saying = self.random_saying.get_next()
            status_bar_label.setText(self.next_saying)
            self.statusBar_extra.setVisible(True)
            # 根据字符长度决定显示时间
            # 3个字符看1秒
            display_time = round((len(self.next_saying) / 3) * 1000)
            self.status_bar_extra_timer.setInterval(display_time)

        # if the first time, delay 5sec to display
        if hasattr(self, 'status_bar_extra_timer') == False:
            first_timer = QTimer()
            first_timer.setSingleShot(True)
            first_timer.timeout.connect(
                lambda: change_saying(self.statusBar_extra))
            first_timer.start(5000)

        self.status_bar_extra_timer = QTimer(self)
        self.status_bar_extra_timer.timeout.connect(
            lambda: change_saying(self.statusBar_extra))

        self.status_bar_extra_timer.start(million_sec)

    def _account_check(self, platform: int | Platform) -> bool:
        match platform:
            case Platform.DAZHONGDIANPING.value:
                username = self.settings.value('dzdp_username', '')
                password = self.encryption.get_encrypted('dzdp_password')
                
                if username == '' or password == '':
                    logger.warning('Username or password don\'t configure properly.')
                    return False
                logger.debug('Current select platform: %s' % '大众点评')
            case Platform.XIECHENG.value:
                logger.debug('Current select platform: %s' % '携程')
            case Platform.RED.value:
                logger.debug('Current select platform: %s' % '小红书')
        pass

    def _start_swan(self):
        if not self.swan:
            self.swan = Swan(self.settings, self.progress_tracker).launch()
        # Get selected location
        location = Location.SHUHE_TOWN if self.location_combo.currentText(
        ) == '束河古镇' else Location.BAISHA_TOWN
        logger.info('Current chosen location: %s' % location)

        # index from 0
        platform = self.platform_combo.currentIndex()
        if self._account_check(platform) == False:
            self._show_account_check_dialog('大众点评账号未配置')
            return

        # Create and start the worker thread
        if self.task_worker == None:
            self.task_worker = TaskWorker(self.swan, location)  # TODO: bug fix
            self.task_worker.finished.connect(self._on_task_finished)
            self.task_worker.error.connect(self._on_task_error)
        self.task_worker.set_location(location)
        self.task_worker.start()

        # Update UI
        self.progress_bar.setVisible(True)
        self.start_button.setEnabled(False)
        self.cancel_button.setEnabled(True)

        toast = Toast()
        toast.setDuration(3000)
        toast.setPositionRelativeToWidget(self)
        toast.setPosition(ToastPosition.TOP_RIGHT)
        toast.setOffset(10, 35)
        toast.setTitle('Swan通知')
        toast.setText('Swan已开始搜集数据...耐心等待喵(●\'◡\'●)')
        toast.applyPreset(ToastPreset.INFORMATION)
        toast.show()
        # reset progress bar
        self.progress_bar.setValue(0)
        self._update_status_bar_info('正在运行任务...', stick_to=True)

    def _cancel_swan(self):
        if self.task_worker and self.task_worker.isRunning():
            self._update_status_bar_info('正在停止任务...')
            toast = Toast()
            toast.setDuration(3000)
            toast.setPositionRelativeToWidget(self)
            toast.setPosition(ToastPosition.TOP_RIGHT)
            toast.setOffset(10, 35)
            toast.setTitle('Swan通知')
            toast.setText('Swan准备上岸啦~ 正在保存数据中...')
            toast.applyPreset(ToastPreset.INFORMATION)
            toast.show()
            self.cancel_button.setEnabled(False)
            self.task_worker.stop()

    def _on_task_finished(self):
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self._update_status_bar_info('任务已完成')
        self.progress_bar.setValue(0)

        toast = Toast()
        toast.setDuration(3500)
        toast.setPositionRelativeToWidget(self)
        toast.setPosition(ToastPosition.TOP_RIGHT)
        toast.setOffset(10, 35)
        toast.setTitle('Swan通知')
        toast.setText('Swan已游上岸边, 数据已保存~')
        toast.applyPreset(ToastPreset.WARNING)
        toast.show()

    def _on_task_error(self, error_message):
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self._update_status_bar_info(f'任务出错: {error_message}')
        self.progress_bar.setValue(0)
        toast = Toast()
        toast.setDuration(3000)
        toast.setPositionRelativeToWidget(self)
        toast.setPosition(ToastPosition.TOP_RIGHT)
        toast.setOffset(10, 35)
        toast.setTitle('Swan通知')
        toast.setText('Swan运行出错: %s' % error_message)
        toast.applyPreset(ToastPreset.ERROR)
        toast.show()
        # throw an error for global error handler
        # raise Exception(error_message)

    def _test_update_progress(self):
        # 模拟进度更新
        self.progress_bar.setVisible(True)
        current_value = self.progress_bar.value()
        max_value = self.progress_bar.maximum()
        new_value = min(current_value + 10, max_value)
        self.progress_bar.setValue(new_value)
        self._update_progress(new_value, max_value)

        toast = Toast()
        toast.setDuration(3000)
        toast.setPositionRelativeToWidget(self)
        toast.setPosition(ToastPosition.TOP_RIGHT)
        toast.setOffset(10, 35)
        toast.setTitle('Swan通知')
        toast.setText('Swan已开始搜集数据...耐心等待喵(●\'◡\'●)')
        toast.applyPreset(ToastPreset.INFORMATION)
        toast.show()

    def _update_progress(self, current_page, max_page):
        progress = int((current_page / max_page) * 100)
        self.progress_bar.setValue(progress)

        # change the text
        self.progress_bar.setFormat(
            f'{round((current_page / max_page) * 100, 2)}% [{current_page}/{max_page}]'
        )
        logger.debug('Current progress: %s' % progress)
        logger.debug('Current page: %s' % current_page)
        logger.debug('Current maximum page: %s' % max_page)
        # Re-enable start button when complete
        if current_page >= max_page:
            self.start_button.setEnabled(True)

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

    def _show_account_check_dialog(self, message : str):
        dialog = AccountCheckDialog(self, message)
        dialog.exec()
        
    def _show_program_settings(self):
        dialog = ProgramSettingsDialog(self.settings, self)
        dialog.exec()

    def _show_account_settings(self):
        dialog = AccountSettingsDialog(self.settings, self)
        dialog.exec()

    def _show_csv_viewer_dialog(self, specific_file_path: str = ''):
        print(specific_file_path)
        try:
            logger.debug("Opening CSV viewer...")  # 调试信息
            self.csv_viewer = CSVViewer(self.settings.value('data_directory'))
            if specific_file_path != '':
                print(specific_file_path)
                if Path(specific_file_path).exists():
                    self.csv_viewer.load_csv(
                        Path(specific_file_path).as_posix())
                    logger.debug('Instant CSV file path: %s' %
                                 Path(specific_file_path).as_posix())
            logger.debug("CSV viewer instance created")  # 调试信息
            self.csv_viewer.setWindowModality(
                Qt.WindowModality.NonModal)  # 确保窗口非模态
            self.csv_viewer.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose,
                                         False)  # 防止关闭时被删除
            self.csv_viewer.show()
            logger.debug("CSV viewer shown")  # 调试信息
        except Exception as e:
            logger.error(f"Error showing CSV viewer: {str(e)}")  # 错误信息
            import traceback
            traceback.print_exc()  # 打印完整的错误堆栈

    def _show_about_dialog(self):
        # raise Exception('Test')
        dialog = AboutDialog(self)
        dialog.exec()

    def _show_log_viewer(self):
        dialog = LogViewerDialog(self.settings)
        dialog.exec()

    def _handle_quit(self):
        logger.debug(
            'Clean up Swan (_handle_quit), ready to dive off to water!')
        self.force_quit = True

        # 如果Swan正在运行，显示弹窗
        if self.task_worker and self.task_worker.isRunning():
            self.task_worker.stop()
            self.swan.grace_shutdown()

        self.close()  # 调用继承的方法 `closeEvent`, 但不会彻底关闭
        QApplication.instance().quit()  # 彻底关闭

    def closeEvent(self, event):
        # 如果Swan正在运行，先停止
        if self.task_worker and self.task_worker.isRunning():
            self.task_worker.stop()
            self.swan.grace_shutdown(
                after_grace_shut_down=lambda: logger.error('Closure'))

        if not self.settings.value('is_system_tray', type=bool):  # 如果是强制退出
            event.accept()
            if hasattr(self, 'csv_viewer'):
                self.csv_viewer.close()
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
