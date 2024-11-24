import sys, os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTableView,
                             QFileDialog, QStatusBar, QApplication, QHeaderView)
from PySide6.QtCore import Qt, QFileSystemWatcher, QTimer, QAbstractTableModel
from PySide6.QtGui import QAction, QKeySequence
import pandas as pd
import subprocess
from loguru import logger
from pyqttoast import Toast, ToastPreset
from src.utils.icon_loader import IconLoader
from src.utils.stylesheet_manager import StyleSheetManager


class CSVTableModel(QAbstractTableModel):

    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data.columns)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])
            if orientation == Qt.Orientation.Vertical:
                return str(section + 1)


class CSVViewer(QMainWindow):

    def __init__(self, default_dir=None):
        super().__init__()
        self.setWindowIcon(IconLoader.load_icon())
        self.default_dir = default_dir or os.path.expanduser("~")
        self.current_file = None
        self.watcher = QFileSystemWatcher()
        self.watcher.fileChanged.connect(self.handle_file_changed)
        self.scroll_positions = {'vertical': 0, 'horizontal': 0}

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Swan - CSV 阅读器")
        self.setGeometry(100, 100, 800, 600)

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Menu bar
        menubar = self.menuBar()
        self.setStyleSheet(StyleSheetManager.fluent_like_style())
        # self.setStyleSheet("""
        #     QMenuBar {
        #         border-bottom:1px solid #d9d9d9;
        #         font-size: 10pt;
        #         padding: 0;
        #         margin: 0;
        #     }
        #     QMenuBar::item {
        #         padding-top: 5px;
        #         padding-left: 15px;
        #         padding-right: 15px;
        #         padding-bottom: 5px;
        #         font-size: 10pt;
        #         background: transparent;  /* 确保背景透明 */
        #     }
        #     QMenuBar::item::selected, QMenuBar::item::hover  {
        #         color: black;
        #         background-color: #f0f0f0;
        #         font-size: 10pt;
        #         padding: 5px 15px;  /* 确保悬停时padding不变 */
        #     }
        #     QMenu {
        #         color:black;
        #         background-color:white; 
        #         border-radius:0;
        #         font-size: 10pt;
        #         border:1px solid #bbbbbb;
        #     }
        #     QMenu::item {
        #         padding: 4px 20px;
        #     }
        #     QMenu::item::text {
        #         margin: 5px 2px;
        #     }

        #     QMenu::item:selected { 
        #         color:#1aa3ff;
        #         background-color: #e5f5ff;
        #     }
        #     QMenu::separator{
        #         height:10px;
        #         background:#bbbbbb;
        #         margin:5px;
        #         margin-left:10px;
        #         margin-right:10px;
        #     }
        # """)
        file_menu = menubar.addMenu('File')

        open_action = QAction('打开CSV文件', self)
        open_action.setShortcut(QKeySequence('Ctrl+O'))
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)

        locate_action = QAction('定位当前文件', self)
        locate_action.setShortcut(QKeySequence('Ctrl+L'))
        locate_action.triggered.connect(self.locate_current_file)
        file_menu.addAction(locate_action)

        # Table view
        self.table_view = QTableView()
        self.table_view.setHorizontalScrollMode(
            QTableView.ScrollMode.ScrollPerPixel)
        self.table_view.setVerticalScrollMode(
            QTableView.ScrollMode.ScrollPerPixel)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.horizontalHeader().setSectionsMovable(True)
        self.table_view.verticalHeader().setSectionsMovable(True)

        # Enable resizing
        self.table_view.horizontalHeader().setSectionsClickable(True)
        self.table_view.horizontalHeader().setSectionsMovable(True)
        self.table_view.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Interactive)
        self.table_view.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Interactive)

        # Enable selection and copying
        self.table_view.setSelectionMode(
            QTableView.SelectionMode.ContiguousSelection)
        self.table_view.setContextMenuPolicy(
            Qt.ContextMenuPolicy.ActionsContextMenu)

        copy_action = QAction("Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy_selection)
        self.table_view.addAction(copy_action)

        layout.addWidget(self.table_view)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Store scroll position before update
        self.table_view.verticalScrollBar().valueChanged.connect(
            self.store_vertical_scroll)
        self.table_view.horizontalScrollBar().valueChanged.connect(
            self.store_horizontal_scroll)

    def store_vertical_scroll(self, value):
        self.scroll_positions['vertical'] = value

    def store_horizontal_scroll(self, value):
        self.scroll_positions['horizontal'] = value

    def restore_scroll_positions(self):
        self.table_view.verticalScrollBar().setValue(
            self.scroll_positions['vertical'])
        self.table_view.horizontalScrollBar().setValue(
            self.scroll_positions['horizontal'])

    def load_csv(self, file_path=None):
        """Load CSV file and display it in the viewer"""
        if file_path is None:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open CSV File", self.default_dir,
                "CSV Files (*.csv);;All Files (*.*)")

        if file_path:
            try:
                # Remove old file from watcher if exists
                if self.current_file:
                    self.watcher.removePath(self.current_file)
                # Read CSV file, set separator
                df = pd.read_csv(file_path, sep='|')
                model = CSVTableModel(df)
                self.table_view.setModel(model)

                # Update status bar
                self.status_bar.showMessage(
                    f"Rows: {df.shape[0]}, Columns: {df.shape[1]}", 0)

                # Add new file to watcher
                self.current_file = file_path
                self.watcher.addPath(file_path)

                # Update window title
                self.setWindowTitle(
                    f"CSV Viewer - {os.path.basename(file_path)}")

                return True
            except Exception as e:
                self.status_bar.showMessage(f"Error loading file: {str(e)}")
                logger.error(f"Error loading file: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
        return False

    def handle_file_changed(self):
        """Handle file changes and reload data while maintaining scroll position"""
        QTimer.singleShot(100, self.reload_current_file)

    def reload_current_file(self):
        """Reload the current file while maintaining scroll position"""
        if self.current_file and os.path.exists(self.current_file):
            self.load_csv(self.current_file)
            self.restore_scroll_positions()

    def copy_selection(self):
        """Copy selected cells to clipboard"""
        selection = self.table_view.selectedIndexes()
        if not selection:
            return

        # Get the bounds of the selection
        rows = sorted(index.row() for index in selection)
        columns = sorted(index.column() for index in selection)
        rowcount = rows[-1] - rows[0] + 1
        colcount = columns[-1] - columns[0] + 1

        # Create table of text
        table = []
        for r in range(rowcount):
            row = []
            for c in range(colcount):
                index = self.table_view.model().index(rows[0] + r,
                                                      columns[0] + c)
                if index in selection:
                    row.append(str(index.data() or ''))
                else:
                    row.append('')
            table.append('\t'.join(row))
        text = '\n'.join(table)

        # Copy to clipboard
        QApplication.clipboard().setText(text)

    def open_file_dialog(self):
        """Open file dialog to select and load CSV file"""
        self.load_csv()

    def locate_current_file(self):
        """Open system file explorer and select current file"""
        if self.current_file:
            normalized_path = os.path.normpath(self.current_file)
            logger.debug(f"Normalized path: {normalized_path}")
            if sys.platform == 'win32':
                subprocess.Popen(f'explorer /select,"{normalized_path}"')
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', '-R', normalized_path])
            else:
                # Linux systems
                os.system(f'xdg-open "{os.path.dirname(self.current_file)}"')
        else:
            """NO file was opened"""
            toast = Toast()
            toast.setDuration(3000)
            toast.setPositionRelativeToWidget(self)
            toast.setTitle('出错啦出错啦')
            toast.setText('当前没有打开任何文件哦(⊙o⊙)')
            toast.applyPreset(ToastPreset.INFORMATION)
            toast.show()

    def closeEvent(self, event):
        """Override closeEvent to ensure CSVViewer is closed when the main window is closed"""
        if hasattr(self, 'csv_viewer') and self.csv_viewer:
            self.csv_viewer.close()
        super().closeEvent(event)
