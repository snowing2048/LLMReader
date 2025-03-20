# services/cache_service.py
import os
import hashlib
import shutil
import io
from typing import Dict, Any, Optional, List
from core.logger import logger

class CacheService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        # 避免重复初始化
        if getattr(self, '_initialized', False):
            return
            
        # 缓存根目录
        self.cache_root = os.path.join(os.getcwd(), 'data', 'storage')
        # 确保缓存根目录存在
        os.makedirs(self.cache_root, exist_ok=True)
        self._initialized = True
        logger.info(f"缓存服务初始化完成，缓存根目录: {self.cache_root}")
    
    def get_pdf_md5(self, file_path: str) -> Optional[str]:
        """计算PDF文件的MD5值
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            str: PDF文件的MD5值，如果计算失败则返回None
        """
        try:
            with open(file_path, 'rb') as f:
                md5 = hashlib.md5()
                # 分块读取文件以处理大文件
                for chunk in iter(lambda: f.read(4096), b""):
                    md5.update(chunk)
                return md5.hexdigest()
        except Exception as e:
            logger.error(f"计算PDF文件MD5值失败: {str(e)}")
            return None
    
    def get_cache_dir(self, pdf_md5: str) -> str:
        """获取PDF文件的缓存目录
        
        Args:
            pdf_md5: PDF文件的MD5值
            
        Returns:
            str: 缓存目录路径
        """
        return os.path.join(self.cache_root, pdf_md5)
    
    def check_cache_exists(self, pdf_md5: str) -> bool:
        """检查PDF文件的缓存是否存在
        
        Args:
            pdf_md5: PDF文件的MD5值
            
        Returns:
            bool: 缓存是否存在
        """
        cache_dir = self.get_cache_dir(pdf_md5)
        content_file = os.path.join(cache_dir, 'content.txt')
        return os.path.exists(cache_dir) and os.path.exists(content_file)
    
    def create_cache(self, pdf_md5: str, content: str, images: List[Any] = None) -> bool:
        """创建PDF文件的缓存
        
        Args:
            pdf_md5: PDF文件的MD5值
            content: PDF文件的文本内容
            images: PDF文件中的图片列表
            
        Returns:
            bool: 是否成功创建缓存
        """
        try:
            cache_dir = self.get_cache_dir(pdf_md5)
            # 确保缓存目录存在
            os.makedirs(cache_dir, exist_ok=True)
            
            # 保存文本内容
            content_file = os.path.join(cache_dir, 'content.txt')
            with open(content_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 保存图片（如果有）
            if images:
                images_dir = os.path.join(cache_dir, 'images')
                os.makedirs(images_dir, exist_ok=True)
                for i, image in enumerate(images):
                    image_path = os.path.join(images_dir, f'image_{i}.png')
                    image.save(image_path)
            
            logger.info(f"成功创建缓存: {pdf_md5}")
            return True
            
        except Exception as e:
            logger.error(f"创建缓存失败: {str(e)}")
            return False