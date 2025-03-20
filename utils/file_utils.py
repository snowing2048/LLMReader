import os
import shutil
import hashlib
from typing import Optional
from core.logger import logger

class FileUtils:
    """文件工具类，提供文件操作相关的工具方法"""
    
    @staticmethod
    def ensure_dir_exists(directory: str) -> None:
        """确保目录存在，如果不存在则创建
        
        Args:
            directory: 目录路径
        """
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.debug(f"创建目录: {directory}")
    
    @staticmethod
    def get_file_md5(file_path: str) -> Optional[str]:
        """计算文件的MD5值
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 文件的MD5值，如果计算失败则返回None
        """
        try:
            with open(file_path, 'rb') as f:
                md5 = hashlib.md5()
                # 分块读取文件以处理大文件
                for chunk in iter(lambda: f.read(4096), b""):
                    md5.update(chunk)
                return md5.hexdigest()
        except Exception as e:
            logger.error(f"计算文件MD5值失败: {str(e)}")
            return None
    
    @staticmethod
    def copy_file(src: str, dst: str) -> bool:
        """复制文件
        
        Args:
            src: 源文件路径
            dst: 目标文件路径
            
        Returns:
            bool: 是否复制成功
        """
        try:
            # 确保目标目录存在
            dst_dir = os.path.dirname(dst)
            FileUtils.ensure_dir_exists(dst_dir)
            
            # 复制文件
            shutil.copy2(src, dst)
            logger.debug(f"复制文件: {src} -> {dst}")
            return True
        except Exception as e:
            logger.error(f"复制文件失败: {src} -> {dst}, 错误: {str(e)}")
            return False