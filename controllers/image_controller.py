# controllers/image_controller.py
from typing import Dict, Any, List
from core.logger import logger
from core.event_bus import EventBus
from models.pdf_model import PDFModel
from models.config_model import ConfigModel

class ImageController:
    def __init__(self, pdf_model=None, config_model=None):
        self.pdf_model = pdf_model or PDFModel()
        self.config_model = config_model or ConfigModel()
        self.event_bus = EventBus()
        self.current_images = []
        self.current_image_index = 0
        logger.info("图片控制器初始化完成")
        
        # 订阅事件
        self.event_bus.subscribe('pdf_model_updated', self._on_pdf_model_updated)
        self.event_bus.subscribe('page_changed', self._on_page_changed)
    
    def _on_pdf_model_updated(self, data: Dict[str, Any]) -> None:
        """处理PDF模型更新事件
        
        Args:
            data: 事件数据
        """
        # 清空当前图片列表
        self.current_images = []
        self.current_image_index = 0
        
        # 发布图片列表更新事件
        self.event_bus.publish('image_list_updated', {
            'images': self.current_images,
            'current_index': self.current_image_index
        })
    
    def _on_page_changed(self, data: Dict[str, Any]) -> None:
        """处理页面变化事件
        
        Args:
            data: 事件数据
        """
        page_num = data.get('page_num', 0)
        # 获取当前页面的图片
        page_data = self.pdf_model.get_page(page_num)
        if page_data and 'images' in page_data:
            self.current_images = page_data['images']
            self.current_image_index = 0
            
            # 发布图片列表更新事件
            self.event_bus.publish('image_list_updated', {
                'images': self.current_images,
                'current_index': self.current_image_index
            })
    
    def get_current_image(self) -> Dict[str, Any]:
        """获取当前图片
        
        Returns:
            Dict[str, Any]: 当前图片信息
        """
        if self.current_images and 0 <= self.current_image_index < len(self.current_images):
            return self.current_images[self.current_image_index]
        return {}
    
    def next_image(self) -> Dict[str, Any]:
        """获取下一张图片
        
        Returns:
            Dict[str, Any]: 图片信息
        """
        if self.current_images and self.current_image_index < len(self.current_images) - 1:
            self.current_image_index += 1
            # 发布当前图片变化事件
            self.event_bus.publish('current_image_changed', {
                'image': self.current_images[self.current_image_index],
                'index': self.current_image_index
            })
            return self.current_images[self.current_image_index]
        return {}
    
    def prev_image(self) -> Dict[str, Any]:
        """获取上一张图片
        
        Returns:
            Dict[str, Any]: 图片信息
        """
        if self.current_images and self.current_image_index > 0:
            self.current_image_index -= 1
            # 发布当前图片变化事件
            self.event_bus.publish('current_image_changed', {
                'image': self.current_images[self.current_image_index],
                'index': self.current_image_index
            })
            return self.current_images[self.current_image_index]
        return {}
    
    def get_image_count(self) -> int:
        """获取图片数量
        
        Returns:
            int: 图片数量
        """
        return len(self.current_images)
    
    def get_current_image_index(self) -> int:
        """获取当前图片索引
        
        Returns:
            int: 当前图片索引
        """
        return self.current_image_index
    
    def set_current_image_index(self, index: int) -> Dict[str, Any]:
        """设置当前图片索引
        
        Args:
            index: 图片索引
            
        Returns:
            Dict[str, Any]: 图片信息
        """
        if self.current_images and 0 <= index < len(self.current_images):
            self.current_image_index = index
            # 发布当前图片变化事件
            self.event_bus.publish('current_image_changed', {
                'image': self.current_images[self.current_image_index],
                'index': self.current_image_index
            })
            return self.current_images[self.current_image_index]
        return {}