# controllers/reader_controller.py
from typing import Dict, Any
from core.logger import logger
from core.event_bus import EventBus
from models.pdf_model import PDFModel
from models.config_model import ConfigModel

class ReaderController:
    def __init__(self, pdf_model=None, config_model=None):
        self.pdf_model = pdf_model or PDFModel()
        self.config_model = config_model or ConfigModel()
        self.event_bus = EventBus()
        self.current_page = 0
        logger.info("阅读器控制器初始化完成")
        
        # 订阅事件
        self.event_bus.subscribe('pdf_model_updated', self._on_pdf_model_updated)
    
    def _on_pdf_model_updated(self, data: Dict[str, Any]) -> None:
        """处理PDF模型更新事件
        
        Args:
            data: 事件数据
        """
        self.current_page = data.get('current_page', 0)
    
    def get_page(self, page_num: int = None) -> Dict[str, Any]:
        """获取指定页面的内容
        
        Args:
            page_num: 页码，从0开始，如果为None则获取当前页面
            
        Returns:
            Dict[str, Any]: 页面内容，包括文本和图片
        """
        return self.pdf_model.get_page(page_num)
    
    def next_page(self) -> Dict[str, Any]:
        """获取下一页内容
        
        Returns:
            Dict[str, Any]: 页面内容，包括文本和图片
        """
        return self.pdf_model.next_page()
    
    def prev_page(self) -> Dict[str, Any]:
        """获取上一页内容
        
        Returns:
            Dict[str, Any]: 页面内容，包括文本和图片
        """
        return self.pdf_model.prev_page()
    
    def set_zoom_level(self, zoom_level: float) -> None:
        """设置缩放级别
        
        Args:
            zoom_level: 缩放级别，1.0表示100%
        """
        self.pdf_model.set_zoom_level(zoom_level)
        self.config_model.zoom_level = zoom_level
    
    def get_zoom_level(self) -> float:
        """获取缩放级别
        
        Returns:
            float: 缩放级别
        """
        return self.pdf_model.zoom_level
    
    def get_current_page(self) -> int:
        """获取当前页码
        
        Returns:
            int: 当前页码
        """
        return self.current_page
    
    def get_total_pages(self) -> int:
        """获取总页数
        
        Returns:
            int: 总页数
        """
        return self.pdf_model.get_total_pages()
    
    def get_metadata(self) -> Dict[str, Any]:
        """获取PDF文件的元数据
        
        Returns:
            Dict[str, Any]: 元数据
        """
        return self.pdf_model.get_metadata()