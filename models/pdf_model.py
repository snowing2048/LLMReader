# models/pdf_model.py
from typing import Dict, Any, List, Optional
from services.pdf_service import PDFService
from core.event_bus import EventBus

class PDFModel:
    def __init__(self, pdf_service=None):
        self.pdf_service = pdf_service or PDFService()
        self.event_bus = EventBus()
        self.current_page = 0
        self.total_pages = 0
        self.metadata = {}
        self.is_loaded = False
        self.file_path = None
        self.zoom_level = 1.0
        
        # 订阅PDF服务的事件
        self.event_bus.subscribe('pdf_loaded', self._on_pdf_loaded)
        self.event_bus.subscribe('pdf_closed', self._on_pdf_closed)
        self.event_bus.subscribe('zoom_changed', self._on_zoom_changed)
    
    def _on_pdf_loaded(self, data: Dict[str, Any]) -> None:
        """处理PDF加载事件
        
        Args:
            data: 事件数据
        """
        self.total_pages = data.get('total_pages', 0)
        self.metadata = data.get('metadata', {})
        self.is_loaded = True
        self.current_page = 0
        
        # 发布模型更新事件
        self.event_bus.publish('pdf_model_updated', {
            'current_page': self.current_page,
            'total_pages': self.total_pages,
            'metadata': self.metadata,
            'is_loaded': self.is_loaded,
            'file_path': self.file_path,
            'zoom_level': self.zoom_level
        })
    
    def _on_pdf_closed(self, data: Dict[str, Any]) -> None:
        """处理PDF关闭事件
        
        Args:
            data: 事件数据
        """
        self.current_page = 0
        self.total_pages = 0
        self.metadata = {}
        self.is_loaded = False
        self.file_path = None
        
        # 发布模型更新事件
        self.event_bus.publish('pdf_model_updated', {
            'current_page': self.current_page,
            'total_pages': self.total_pages,
            'metadata': self.metadata,
            'is_loaded': self.is_loaded,
            'file_path': self.file_path,
            'zoom_level': self.zoom_level
        })
    
    def _on_zoom_changed(self, data: Dict[str, Any]) -> None:
        """处理缩放级别变化事件
        
        Args:
            data: 事件数据
        """
        self.zoom_level = data.get('zoom_level', 1.0)
        
        # 发布模型更新事件
        self.event_bus.publish('pdf_model_updated', {
            'current_page': self.current_page,
            'total_pages': self.total_pages,
            'metadata': self.metadata,
            'is_loaded': self.is_loaded,
            'file_path': self.file_path,
            'zoom_level': self.zoom_level
        })
    
    def load_pdf(self, file_path: str) -> bool:
        """加载PDF文件
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            bool: 是否成功加载PDF文件
        """
        self.file_path = file_path
        return self.pdf_service.load_pdf(file_path)
    
    def close_pdf(self) -> None:
        """关闭PDF文件"""
        self.pdf_service.close()
    
    def get_page(self, page_num: Optional[int] = None) -> Dict[str, Any]:
        """获取指定页面的内容
        
        Args:
            page_num: 页码，从0开始，如果为None则获取当前页面
            
        Returns:
            Dict[str, Any]: 页面内容，包括文本和图片
        """
        if page_num is None:
            page_num = self.current_page
        
        # 更新当前页码
        if page_num != self.current_page:
            self.current_page = page_num
            # 发布页面变化事件
            self.event_bus.publish('page_changed', {'page_num': page_num})
        
        return self.pdf_service.get_page(page_num)
    
    def next_page(self) -> Dict[str, Any]:
        """获取下一页内容
        
        Returns:
            Dict[str, Any]: 页面内容，包括文本和图片
        """
        if self.current_page < self.total_pages - 1:
            return self.get_page(self.current_page + 1)
        return {}
    
    def prev_page(self) -> Dict[str, Any]:
        """获取上一页内容
        
        Returns:
            Dict[str, Any]: 页面内容，包括文本和图片
        """
        if self.current_page > 0:
            return self.get_page(self.current_page - 1)
        return {}
    
    def set_zoom_level(self, zoom_level: float) -> None:
        """设置缩放级别
        
        Args:
            zoom_level: 缩放级别，1.0表示100%
        """
        self.pdf_service.set_zoom_level(zoom_level)
    
    def get_metadata(self) -> Dict[str, Any]:
        """获取PDF文件的元数据
        
        Returns:
            Dict[str, Any]: 元数据
        """
        return self.metadata
    
    def get_total_pages(self) -> int:
        """获取PDF文件的总页数
        
        Returns:
            int: 总页数
        """
        return self.total_pages