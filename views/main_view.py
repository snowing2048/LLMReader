# views/main_view.py
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter
from PyQt5.QtCore import Qt
from core.logger import logger

class MainView(QMainWindow):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.file_view = None
        self.reader_view = None
        self.image_view = None
        self.chat_view = None
        self.menu_view = None
        self.splitter = None
        logger.info("初始化主窗口视图")
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('文献阅读器')
        
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
        
        layout.addWidget(self.splitter)
    
    def set_views(self, file_view, reader_view, image_view, chat_view):
        """设置各个视图组件
        
        Args:
            file_view: 文件视图
            reader_view: 阅读器视图
            image_view: 图片查看器视图
            chat_view: 聊天视图
        """
        self.file_view = file_view
        self.reader_view = reader_view
        self.image_view = image_view
        self.chat_view = chat_view
        
        # 添加四个面板到主分割器
        self.splitter.addWidget(self.file_view)
        self.splitter.addWidget(self.reader_view)
        self.splitter.addWidget(self.image_view)
        self.splitter.addWidget(self.chat_view)
    
    def set_controllers(self, controllers):
        """设置控制器引用
        
        Args:
            controllers: 控制器字典
        """
        self.controller = controllers.get('app')
        
        # 将控制器引用传递给各个视图
        if self.file_view:
            self.file_view.set_controller(controllers.get('file'))
        if self.reader_view:
            self.reader_view.set_controller(controllers.get('reader'))
        if self.image_view:
            self.image_view.set_controller(controllers.get('image'))
        if self.chat_view:
            self.chat_view.set_controller(controllers.get('chat'))
    
    def set_geometry(self, x, y, width, height):
        """设置窗口几何信息
        
        Args:
            x: 窗口x坐标
            y: 窗口y坐标
            width: 窗口宽度
            height: 窗口高度
        """
        self.setGeometry(x, y, width, height)
    
    def set_splitter_sizes(self, sizes):
        """设置分割器比例
        
        Args:
            sizes: 分割器比例列表
        """
        if self.splitter and len(sizes) >= 4:
            self.splitter.setSizes(sizes)
    
    def set_image_viewer_splitter_sizes(self, sizes):
        """设置图片查看器分割器比例
        
        Args:
            sizes: 分割器比例列表
        """
        if self.image_view and hasattr(self.image_view, 'set_splitter_sizes'):
            self.image_view.set_splitter_sizes(sizes)
    
    def save_geometry(self):
        """保存窗口几何信息"""
        if self.controller:
            geometry = self.geometry()
            self.controller.save_window_geometry({
                'x': geometry.x(),
                'y': geometry.y(),
                'width': geometry.width(),
                'height': geometry.height()
            })
    
    def save_splitter_sizes(self):
        """保存分割器比例"""
        if self.controller and self.splitter:
            sizes = self.splitter.sizes()
            self.controller.save_splitter_sizes(sizes)
    
    def save_image_viewer_splitter_sizes(self):
        """保存图片查看器分割器比例"""
        if self.controller and self.image_view and hasattr(self.image_view, 'get_splitter_sizes'):
            sizes = self.image_view.get_splitter_sizes()
            self.controller.save_image_viewer_splitter_sizes(sizes)
    
    def closeEvent(self, event):
        """窗口关闭事件处理
        
        Args:
            event: 关闭事件
        """
        # 保存窗口几何信息和分割器比例
        self.save_geometry()
        self.save_splitter_sizes()
        self.save_image_viewer_splitter_sizes()
        
        # 调用父类方法
        super().closeEvent(event)