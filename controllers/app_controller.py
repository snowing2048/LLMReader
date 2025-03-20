# controllers/app_controller.py
from typing import Dict, Any
from core.logger import logger
from core.service_locator import ServiceLocator
from core.event_bus import EventBus
from models.config_model import ConfigModel
from controllers.file_controller import FileController
from controllers.reader_controller import ReaderController
from controllers.image_controller import ImageController
from controllers.chat_controller import ChatController
from views.main_view import MainView

class AppController:
    def __init__(self):
        # 初始化事件总线
        self.event_bus = EventBus()
        
        # 初始化配置模型
        self.config_model = ConfigModel()
        
        # 注册服务
        ServiceLocator.register('config_model', self.config_model)
        
        # 初始化主视图
        self.main_view = MainView()
        
        # 初始化子控制器
        self.file_controller = FileController()
        self.reader_controller = ReaderController()
        self.image_controller = ImageController()
        self.chat_controller = ChatController()
        
        # 设置主视图的控制器引用
        self.main_view.set_controllers({
            'app': self,
            'file': self.file_controller,
            'reader': self.reader_controller,
            'image': self.image_controller,
            'chat': self.chat_controller
        })
        
        # 从配置中加载窗口几何信息
        self._load_window_geometry()
        
        logger.info("应用程序控制器初始化完成")
    
    def _load_window_geometry(self) -> None:
        """从配置中加载窗口几何信息"""
        window_geometry = self.config_model.window_geometry
        self.main_view.set_geometry(
            window_geometry.get('x', 100),
            window_geometry.get('y', 100),
            window_geometry.get('width', 1200),
            window_geometry.get('height', 800)
        )
        
        # 加载分割器比例
        splitter_sizes = self.config_model.splitter_sizes
        self.main_view.set_splitter_sizes(splitter_sizes)
        
        # 加载图片查看器分割器比例
        image_viewer_splitter_sizes = self.config_model.image_viewer_splitter_sizes
        self.main_view.set_image_viewer_splitter_sizes(image_viewer_splitter_sizes)
    
    def save_window_geometry(self, geometry: Dict[str, int]) -> None:
        """保存窗口几何信息到配置
        
        Args:
            geometry: 窗口几何信息，包含x、y、width、height
        """
        self.config_model.window_geometry = geometry
    
    def save_splitter_sizes(self, sizes: list) -> None:
        """保存分割器比例到配置
        
        Args:
            sizes: 分割器比例列表
        """
        self.config_model.splitter_sizes = sizes
    
    def save_image_viewer_splitter_sizes(self, sizes: list) -> None:
        """保存图片查看器分割器比例到配置
        
        Args:
            sizes: 分割器比例列表
        """
        self.config_model.image_viewer_splitter_sizes = sizes
    
    def show(self) -> None:
        """显示主窗口"""
        self.main_view.show()
    
    def exit(self) -> None:
        """退出应用程序"""
        # 保存配置
        self.main_view.save_geometry()
        self.main_view.save_splitter_sizes()
        
        # 清理资源
        ServiceLocator.clear()
        logger.info("应用程序退出")