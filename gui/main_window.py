from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QSplitter, 
                             QPushButton, QAction, QMenuBar, QMenu, QFileDialog, QMessageBox)
from core.theme_manager import ThemeManager
from .file_panel import FilePanel
from .reader_panel import ReaderPanel
from .chat_list_panel import ChatListPanel
from .image_viewer_panel import ImageViewerPanel
from .menu_manager import MenuManager
from conf.config_manager import ConfigManager
from core import vars
from core.logger import logger

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.info("初始化主窗口")
        self.config_manager = ConfigManager()
        self.theme_manager = ThemeManager()
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        self.initUI()
        
        # 应用当前主题
        self.theme_manager.apply_theme(self.theme_manager.get_current_theme())

    def initUI(self):
        self.setWindowTitle('文献阅读器')
        
        # 设置窗口图标
        import os
        from PyQt5.QtGui import QIcon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "logo.svg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            logger.debug(f"设置窗口图标: {icon_path}")
        
        # 从配置中加载窗口几何信息
        window_geometry = self.config_manager.window_geometry
        self.setGeometry(
            window_geometry['x'],
            window_geometry['y'],
            window_geometry['width'],
            window_geometry['height']
        )
        logger.debug(f"设置窗口几何信息: {window_geometry}")

        # 主布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # 创建四栏布局
        self.splitter = QSplitter()
        
        # 设置分割器样式，添加分隔线
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #CCCCCC;
                border: 1px solid #999999;
                width: 2px;
                height: 2px;
                margin: 1px;
            }
            QSplitter::handle:horizontal {
                width: 4px;
            }
            QSplitter::handle:vertical {
                height: 4px;
            }
        """)
        
        # 左侧文件树
        self.file_panel = FilePanel()
        
        # 中间文本阅读区域
        self.reader_panel = ReaderPanel()
        
        # 图片查看区域
        self.image_viewer_panel = ImageViewerPanel()
        
        # 右侧聊天区域
        self.chat_panel = ChatListPanel()

        # 创建菜单管理器
        self.menu_manager = MenuManager(self)

        # 添加四个面板到主分割器
        self.splitter.addWidget(self.file_panel)
        self.splitter.addWidget(self.reader_panel)
        self.splitter.addWidget(self.image_viewer_panel)
        self.splitter.addWidget(self.chat_panel)
        
        # 从配置中加载分割器比例，如果配置中只有三个面板的比例，则设置默认比例
        splitter_sizes = self.config_manager.splitter_sizes
        if len(splitter_sizes) == 3:  # 旧配置只有三个面板
            # 计算新的分割器比例
            reader_size = splitter_sizes[1]
            # 将阅读区域的空间分配给文本阅读和图片查看
            splitter_sizes = [splitter_sizes[0], reader_size // 2, reader_size // 2, splitter_sizes[2]]
            logger.info("检测到旧的分割器配置，已自动调整为四栏布局")
        
        self.splitter.setSizes(splitter_sizes)
        self.splitter.setStretchFactor(0, 1)  # 文件树
        self.splitter.setStretchFactor(1, 2)  # 文本阅读区域
        self.splitter.setStretchFactor(2, 2)  # 图片查看区域
        self.splitter.setStretchFactor(3, 2)  # 聊天区域
        logger.debug(f"设置分割器比例: {splitter_sizes}")

        layout.addWidget(self.splitter)

        # 添加文件选择功能
        self.file_panel.file_selected.connect(self.on_file_selected)
        
        # 从配置中加载上次的文献库路径
        last_library = self.config_manager.last_library_path
        if last_library:
            logger.info(f"加载上次的文献库路径: {last_library}")
            self.file_panel.set_root_path(last_library)

        # 从配置中加载API密钥
        api_key = self.config_manager.api_key
        if api_key:
            logger.info("从配置中加载API密钥")
            self.chat_panel.set_api_key(api_key)

        # 从配置中加载缩放级别
        zoom_level = self.config_manager.zoom_level
        logger.debug(f"从配置中加载缩放级别: {zoom_level*100}%")
        self.reader_panel.set_zoom_level(zoom_level)
        
        logger.info("主窗口初始化完成")

    def on_file_selected(self, file_path):
        """处理文件选择事件
        
        Args:
            file_path: 选中的文件路径
        """
        logger.info(f"选择文件: {file_path}")
        # 加载PDF文件
        result = self.reader_panel.load_pdf(file_path)
        
        # 如果PDF加载成功，启用重建缓存菜单项
        if result:
            logger.debug("PDF加载成功，启用重建缓存菜单项")
            self.menu_manager.rebuild_cache_action.setEnabled(True)
        else:
            logger.warning(f"PDF加载失败: {file_path}")
    
    def on_theme_changed(self, theme: str):
        """处理主题变化
        
        Args:
            theme: 新的主题模式，'light' 或 'dark'
        """
        logger.debug(f"主题变化: {theme}")
    
    def closeEvent(self, event):
        logger.info("应用程序关闭，保存配置")
        # 保存窗口几何信息
        geometry = self.geometry()
        window_geometry = {
            'x': geometry.x(),
            'y': geometry.y(),
            'width': geometry.width(),
            'height': geometry.height()
        }
        self.config_manager.window_geometry = window_geometry
        logger.debug(f"保存窗口几何信息: {window_geometry}")
        
        # 保存分割器比例
        splitter_sizes = self.splitter.sizes()
        self.config_manager.splitter_sizes = splitter_sizes
        logger.debug(f"保存分割器比例: {splitter_sizes}")
        
        # 保存图片查看器分割器比例
        image_viewer_splitter_sizes = self.image_viewer_panel.splitter.sizes()
        self.config_manager.image_viewer_splitter_sizes = image_viewer_splitter_sizes
        logger.debug(f"保存图片查看器分割器比例: {image_viewer_splitter_sizes}")
        
        # 保存缩放级别
        zoom_level = self.reader_panel.zoom_level / 100.0
        self.config_manager.zoom_level = zoom_level
        logger.debug(f"保存缩放级别: {zoom_level*100}%")
        
        # 调用父类的closeEvent
        super().closeEvent(event)