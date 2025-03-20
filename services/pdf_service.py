# services/pdf_service.py
from core.pdf_reader import PDFReader
from typing import List, Dict, Any, Optional
from core.logger import logger
from services.cache_service import CacheService
from core.event_bus import EventBus

class PDFService:
    def __init__(self, cache_service=None):
        self.pdf_reader = PDFReader()
        self.cache_service = cache_service or CacheService()
        self.event_bus = EventBus()
        self.current_pdf_path = None
        self.current_pdf_md5 = None
        self.zoom_level = 1.0
        logger.info("PDF服务初始化完成")
    
    def load_pdf(self, file_path: str) -> bool:
        """加载PDF文件
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            bool: 是否成功加载PDF文件
        """
        logger.info(f"尝试加载PDF文件: {file_path}")
        
        # 保存当前PDF文件路径
        self.current_pdf_path = file_path
        
        # 计算PDF文件的MD5值
        self.current_pdf_md5 = self.cache_service.get_pdf_md5(file_path)
        if not self.current_pdf_md5:
            logger.error(f"计算PDF文件MD5值失败: {file_path}")
            return False
        
        # 检查是否存在缓存
        is_cached = self.cache_service.check_cache_exists(self.current_pdf_md5)
        
        if is_cached:
            logger.info(f"使用缓存加载PDF文件: {file_path}")
            # 从缓存中获取内容
            cache_content = self.cache_service.get_cache_content(self.current_pdf_md5)
            
            # 仍然需要打开PDF文件以获取元数据和总页数
            if not self.pdf_reader.open(file_path):
                logger.error(f"打开PDF文件失败: {file_path}")
                return False
            
            metadata = self.pdf_reader.get_metadata()
            total_pages = self.pdf_reader.get_total_pages()
            
            # 发布PDF已加载事件
            self.event_bus.publish('pdf_loaded', {
                'total_pages': total_pages,
                'metadata': metadata,
                'cached': True,
                'cache_content': cache_content
            })
            
            logger.info(f"从缓存加载PDF文件成功: {file_path}, 总页数: {total_pages}")
            return True
        else:
            # 没有缓存，正常加载PDF文件
            logger.info(f"正常加载PDF文件: {file_path}")
            if not self.pdf_reader.open(file_path):
                logger.error(f"打开PDF文件失败: {file_path}")
                return False
            
            # 获取PDF内容并创建缓存
            metadata = self.pdf_reader.get_metadata()
            total_pages = self.pdf_reader.get_total_pages()
            
            # 提取所有页面的文本内容
            all_text = ""
            all_images = []
            for page_num in range(total_pages):
                page = self.pdf_reader.get_page(page_num)
                if page:
                    all_text += f"\n--- 第 {page_num + 1} 页 ---\n\n"
                    all_text += page.get_text()
                    all_images.extend(page.images)
            
            # 创建缓存
            self.cache_service.create_cache(self.current_pdf_md5, all_text, all_images)
            
            # 发布PDF已加载事件
            self.event_bus.publish('pdf_loaded', {
                'total_pages': total_pages,
                'metadata': metadata,
                'cached': False,
                'cache_content': {'raw_content': all_text}
            })
            
            logger.info(f"PDF文件加载成功: {file_path}, 总页数: {total_pages}")
            return True
    
    def get_page(self, page_num: int) -> Dict[str, Any]:
        """获取指定页面的内容
        
        Args:
            page_num: 页码，从0开始
            
        Returns:
            Dict[str, Any]: 页面内容，包括文本和图片
        """
        if not self.pdf_reader.is_open():
            logger.error("PDF文件未打开")
            return {}
        
        page = self.pdf_reader.get_page(page_num)
        if not page:
            logger.error(f"获取页面失败: {page_num}")
            return {}
        
        return {
            'text': page.get_text(),
            'images': page.images
        }
    
    def get_total_pages(self) -> int:
        """获取PDF文件的总页数
        
        Returns:
            int: 总页数
        """
        if not self.pdf_reader.is_open():
            logger.error("PDF文件未打开")
            return 0
        
        return self.pdf_reader.get_total_pages()
    
    def get_metadata(self) -> Dict[str, Any]:
        """获取PDF文件的元数据
        
        Returns:
            Dict[str, Any]: 元数据
        """
        if not self.pdf_reader.is_open():
            logger.error("PDF文件未打开")
            return {}
        
        return self.pdf_reader.get_metadata()
    
    def set_zoom_level(self, zoom_level: float) -> None:
        """设置缩放级别
        
        Args:
            zoom_level: 缩放级别，1.0表示100%
        """
        self.zoom_level = zoom_level
        # 发布缩放级别变化事件
        self.event_bus.publish('zoom_changed', {'zoom_level': zoom_level})
    
    def close(self) -> None:
        """关闭PDF文件"""
        if self.pdf_reader.is_open():
            self.pdf_reader.close()
            self.current_pdf_path = None
            self.current_pdf_md5 = None
            logger.info("关闭PDF文件")
            # 发布PDF已关闭事件
            self.event_bus.publish('pdf_closed', {})