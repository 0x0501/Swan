class StyleSheetManager():

    def __init__(self) -> None:
        pass

    @staticmethod
    def fluent_like_style():
        return """
        /* 全局样式 */
        * {
            font-family: "Segoe UI", "Microsoft YaHei";
            color: #2b2b2b;
        }

        /* 窗口标题栏 */
        QMainWindow::title {
            background-color: #ffffff;
            color: #2b2b2b;
            padding: 5px;
        }

        /* 按钮样式 */
        QPushButton {
            background-color: #1677ff;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 0px 20px;
            font-size: 14px;
            min-height: 32px;
        }

        QPushButton:hover {
            background-color: #106ebe;
        }

        QPushButton:pressed {
            background-color: #005a9e;
        }

        QPushButton:disabled {
            background-color: #f0f0f0;
            border: 1px solid #d9d9d9;
            color: #a0a0a0;
        }

        /* 文本输入框 */
        QLineEdit {
            background-color: #ffffff;
            border: 1px solid #d1d1d1;
            border-radius: 4px;
            padding: 0px 8px;
            min-height: 28px;
        }

        QLineEdit:hover {
            border: 1px solid #989898;
        }

        /* 下拉框 */
        QComboBox {
            background-color: #ffffff;
            border: 1px solid #d1d1d1;
            border-radius: 4px;
            padding: 0px 8px;
            min-height: 28px;
        }

        QComboBox::drop-down {
            border: none;
            width: 20px;
        }

        QComboBox::down-arrow {
            image: url(:/icons/chevron-down.svg);  /* 需要自行提供下拉箭头图标 */
            margin-right: 10px;
            width: 12px;
            height: 12px;
        }

        QComboBox:hover {
            border: 1px solid #989898;
        }

        /* 复选框 */
        QCheckBox {
            spacing: 8px;
        }

        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 1px solid #d1d1d1;
            border-radius: 3px;
        }

        QCheckBox::indicator:checked {
            background-color: #0078d4;
            border: none;
        }

        QCheckBox::indicator:hover {
            border: 1px solid #989898;
        }

        /* 单选框 */
        QRadioButton {
            spacing: 8px;
        }

        QRadioButton::indicator {
            width: 18px;
            height: 18px;
            border: 1px solid #d1d1d1;
            border-radius: 9px;
        }

        QRadioButton::indicator:checked {
            background-color: #0078d4;
            border: 4px solid #ffffff;
        }

        QRadioButton::indicator:hover {
            border: 1px solid #989898;
        }

        /* 滚动条 */
        QScrollBar:vertical {
            border: none;
            background-color: #f5f5f5;
            width: 8px;
            margin: 0px;
        }

        QScrollBar::handle:vertical {
            background-color: #c1c1c1;
            border-radius: 4px;
            min-height: 30px;
        }

        QScrollBar::handle:vertical:hover {
            background-color: #a8a8a8;
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }

        QScrollBar:horizontal {
            border: none;
            background-color: #f5f5f5;
            height: 8px;
            margin: 0px;
        }

        QScrollBar::handle:horizontal {
            background-color: #c1c1c1;
            border-radius: 4px;
            min-width: 30px;
        }

        QScrollBar::handle:horizontal:hover {
            background-color: #a8a8a8;
        }

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }

        /* 分组框 */
        QGroupBox {
            border: 1px solid #d1d1d1;
            border-radius: 4px;
            margin-top: 12px;
            padding-top: 12px;
        }

        QGroupBox::title {
            color: #2b2b2b;
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 8px;
            padding: 0 3px;
        }

        /* 菜单栏 */
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
            padding: 5px 20px;
        }
        QMenu::item::text {
            margin: 2px;
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

        /* 工具栏 */
        QToolBar {
            background-color: #ffffff;
            border-bottom: 1px solid #e1e1e1;
            spacing: 6px;
            padding: 3px;
        }

        QToolButton {
            background-color: transparent;
            border: none;
            border-radius: 4px;
            padding: 4px;
        }

        QToolButton:hover {
            background-color: #e5f3ff;
        }

        QToolButton:pressed {
            background-color: #cce4f7;
        }

        /* 状态栏 */
        QStatusBar {
            background-color: #ffffff;
            border-top: 1px solid #e1e1e1;
        }

        /* 进度条 */
        QProgressBar {
            border: none;
            background-color: #f0f0f0;
            border-radius: 2px;
            text-align: center;
        }

        QProgressBar::chunk {
            background-color: #0078d4;
            border-radius: 2px;
        }

        /* 选项卡 */
        QTabWidget::pane {
            border: 1px solid #d1d1d1;
            border-radius: 4px;
            background-color: #ffffff;
        }

        QTabBar::tab {
            background-color: #f5f5f5;
            border: 1px solid #d1d1d1;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 6px 16px;
            margin-right: 2px;
        }

        QTabBar::tab:selected {
            background-color: #ffffff;
            border-bottom: 2px solid #0078d4;
        }

        QTabBar::tab:hover:!selected {
            background-color: #e5f3ff;
        }

        /* 表格 */
        QTableView {
            background-color: #ffffff;
            border: 1px solid #d1d1d1;
            border-radius: 4px;
            gridline-color: #e1e1e1;
        }

        QTableView::item {
            padding: 6px;
        }

        QTableView::item:selected {
            background-color: #e5f3ff;
            color: #2b2b2b;
        }

        QHeaderView::section {
            background-color: #f5f5f5;
            border: none;
            border-right: 1px solid #d1d1d1;
            border-bottom: 1px solid #d1d1d1;
            padding: 6px;
        }

        /* 列表视图 */
        QListView {
            background-color: #ffffff;
            border: 1px solid #d1d1d1;
            border-radius: 4px;
        }

        QListView::item {
            padding: 6px;
        }

        QListView::item:selected {
            background-color: #e5f3ff;
            color: #2b2b2b;
        }

        /* 树形视图 */
        QTreeView {
            background-color: #ffffff;
            border: 1px solid #d1d1d1;
            border-radius: 4px;
        }

        QTreeView::item {
            padding: 6px;
        }

        QTreeView::item:selected {
            background-color: #e5f3ff;
            color: #2b2b2b;
        }

        QTreeView::branch {
            background-color: #ffffff;
        }

        QTreeView::branch:has-siblings:!adjoins-item {
            border-image: url(vline.png) 0;  /* 需要自行提供树枝线图标 */
        }

        QTreeView::branch:has-siblings:adjoins-item {
            border-image: url(branch-more.png) 0;  /* 需要自行提供树枝线图标 */
        }

        QTreeView::branch:!has-children:!has-siblings:adjoins-item {
            border-image: url(branch-end.png) 0;  /* 需要自行提供树枝线图标 */
        }

        /* 文本编辑框 */
        QTextEdit, QPlainTextEdit {
            background-color: #ffffff;
            border: 1px solid #d1d1d1;
            border-radius: 4px;
            padding: 6px;
        }

        /* 滑块 */
        QSlider::groove:horizontal {
            border: none;
            height: 4px;
            background-color: #f0f0f0;
            border-radius: 2px;
        }

        QSlider::handle:horizontal {
            background-color: #0078d4;
            border: none;
            width: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }

        QSlider::handle:horizontal:hover {
            background-color: #106ebe;
        }

        QSlider::add-page:horizontal {
            background-color: #f0f0f0;
        }

        QSlider::sub-page:horizontal {
            background-color: #0078d4;
        }
    """
