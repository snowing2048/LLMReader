# controllers/file_controller.py
from typing import Dict, Any, List
from core.logger import logger
from core.event_bus import EventBus
from models.pdf_model import PDFModel
from models.config_model import ConfigModel

class FileController:
    def __init__(self, pdf_model=None, config_model=None):
        self.pdf_model = pdf_model or PDFModel()
        self.config_model = config_model or ConfigModel()
        self.event_bus = EventBus()
        self.current_library_path = self.config_model.last_library_path
        logger.info("文件控制器初始化完成")
    
    def open_pdf(self, file_path: str) -> bool:
        """打开PDF文件
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            bool: 是否成功打开PDF文件
        """
        logger.info(f"尝试打开PDF文件: {file_path}")
        result = self.pdf_model.load_pdf(file_path)
        if result:
            # 发布文件打开事件
            self.event_bus.publish('file_opened', {
                'file_path': file_path,
                'file_type': 'pdf'
            })
        return result
    
    def close_pdf(self) -> None:
        """关闭PDF文件"""
        self.pdf_model.close_pdf()
        # 发布文件关闭事件
        self.event_bus.publish('file_closed', {})
    
    def set_library_path(self, path: str) -> None:
        """设置文献库路径
        
        Args:
            path: 文献库路径
        """
        self.current_library_path = path
        self.config_model.last_library_path = path
        # 发布文献库路径变更事件
        self.event_bus.publish('library_path_changed', {
            'path': path
        })
    
    def get_library_path(self) -> str:
        """获取文献库路径
        
        Returns:
            str: 文献库路径
        """
        return self.current_library_path
    
    def get_file_categories(self) -> Dict[str, Any]:
        """获取文件分类信息
        
        Returns:
            Dict[str, Any]: 文件分类信息
        """
        return self.config_model.categories
    
    def update_file_category(self, file_path: str, category: str) -> None:
        """更新文件分类
        
        Args:
            file_path: 文件路径
            category: 分类名称
        """
        categories = self.config_model.categories
        if category not in categories:
            categories[category] = []
        
        # 确保文件路径不重复添加到同一分类
        if file_path not in categories[category]:
            categories[category].append(file_path)
        
        self.config_model.categories = categories
        
        # 发布文件分类更新事件
        self.event_bus.publish('file_category_updated', {
            'file_path': file_path,
            'category': category
        })