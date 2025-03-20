from core.pdf_reader import PDFReader
from typing import List, Dict, Any, Callable, Optional
from core.logger import logger
from core.cache_manager import CacheManager
import os

class PDFManager:
    """PDF管理器类，负责管理PDF文件的加载、页面导航和缩放等操作
    使用观察者模式通知GUI组件PDF状态的变化
    """
    
    def __init__(self):
        self.pdf_reader = PDFReader()
        self.observers = []  # 观察者列表
        self.zoom_level = 1.0  # 缩放级别，1.0表示100%
        self.cache_manager = CacheManager()  # 缓存管理器
        self.current_pdf_path = None  # 当前打开的PDF文件路径
        self.current_pdf_md5 = None  # 当前打开的PDF文件的MD5值
        self.is_cached = False  # 当前PDF是否使用了缓存
        logger.info("PDF管理器初始化完成")
    
    def add_observer(self, observer):
        """添加观察者
        
        Args:
            observer: 实现了update方法的观察者对象
        """
        if observer not in self.observers:
            self.observers.append(observer)
            logger.debug(f"添加观察者: {observer.__class__.__name__}")
    
    def remove_observer(self, observer):
        """移除观察者
        
        Args:
            observer: 要移除的观察者对象
        """
        if observer in self.observers:
            self.observers.remove(observer)
            logger.debug(f"移除观察者: {observer.__class__.__name__}")
    
    def notify_observers(self, event_type, data=None):
        """通知所有观察者
        
        Args:
            event_type: 事件类型
            data: 事件数据
        """
        logger.debug(f"通知观察者事件: {event_type}, 数据: {data}")
        for observer in self.observers:
            observer.update(event_type, data)
    
    def load_pdf(self, file_path):
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
        self.current_pdf_md5 = self.cache_manager.get_pdf_md5(file_path)
        if not self.current_pdf_md5:
            logger.error(f"计算PDF文件MD5值失败: {file_path}")
            return False
        
        # 检查是否存在缓存
        self.is_cached = self.cache_manager.check_cache_exists(self.current_pdf_md5)
        
        if self.is_cached:
            logger.info(f"使用缓存加载PDF文件: {file_path}")
            # 从缓存中获取内容
            cache_content = self.cache_manager.get_cache_content(self.current_pdf_md5)
            
            # 仍然需要打开PDF文件以获取元数据和总页数
            if not self.pdf_reader.open(file_path):
                logger.error(f"打开PDF文件失败: {file_path}")
                return False
            
            metadata = self.pdf_reader.get_metadata()
            total_pages = self.pdf_reader.get_total_pages()
            
            # 通知观察者PDF已加载，并且是从缓存加载的
            self.notify_observers('pdf_loaded', {
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
            self.cache_manager.create_cache(self.current_pdf_md5, all_text, all_images)
            
            # 通知观察者PDF已加载
            self.notify_observers('pdf_loaded', {
                'total_pages': total_pages,
                'metadata': metadata,
                'cached': False,
                'cache_content': {'raw_content': all_text}
            })
            
            logger.info(f"PDF文件加载成功: {file_path}, 总页数: {total_pages}")
            return True
    
    def close_pdf(self):
        """关闭PDF文件"""
        logger.info("关闭PDF文件")
        self.pdf_reader.close()
        # 重置缓存状态
        self.current_pdf_path = None
        self.current_pdf_md5 = None
        self.is_cached = False
        # 通知观察者PDF已关闭
        self.notify_observers('pdf_closed')
        
    def rebuild_cache(self) -> bool:
        """重建当前PDF文件的缓存
        
        Returns:
            bool: 是否成功重建缓存
        """
        if not self.current_pdf_path or not self.current_pdf_md5:
            logger.warning("重建缓存失败: 没有打开的PDF文件")
            return False
        
        logger.info(f"开始重建PDF文件缓存: {self.current_pdf_path}")
        
        # 提取所有页面的文本内容
        total_pages = self.pdf_reader.get_total_pages()
        all_text = ""
        all_images = []
        
        for page_num in range(total_pages):
            page = self.pdf_reader.get_page(page_num)
            if page:
                all_text += f"\n--- 第 {page_num + 1} 页 ---\n\n"
                all_text += page.get_text()
                all_images.extend(page.images)
        
        # 重建缓存
        result = self.cache_manager.rebuild_cache(self.current_pdf_md5, all_text, all_images)
        
        if result:
            logger.info(f"PDF文件缓存重建成功: {self.current_pdf_path}")
            # 重新加载PDF文件以使用新缓存
            return self.load_pdf(self.current_pdf_path)
        else:
            logger.error(f"PDF文件缓存重建失败: {self.current_pdf_path}")
            return False
    
    def get_current_page(self):
        """获取当前页面
        
        Returns:
            PDFPage: 当前页面对象
        """
        return self.pdf_reader.get_page(self.pdf_reader.current_page)
    
    def go_to_page(self, page_num):
        """跳转到指定页面
        
        Args:
            page_num: 页码（从0开始）
            
        Returns:
            bool: 是否成功跳转
        """
        if not self.pdf_reader.doc or page_num < 0 or page_num >= self.pdf_reader.total_pages:
            logger.warning(f"页面跳转失败: 无效的页码 {page_num+1}")
            return False
        
        self.pdf_reader.current_page = page_num
        logger.debug(f"跳转到页面: {page_num+1}")
        # 通知观察者页面已改变
        self.notify_observers('page_changed', {
            'page_num': page_num + 1  # 转换为从1开始的页码
        })
        return True
    
    def next_page(self):
        """下一页
        
        Returns:
            bool: 是否成功跳转
        """
        if not self.pdf_reader.doc or self.pdf_reader.current_page >= self.pdf_reader.total_pages - 1:
            logger.debug("下一页失败: 已经是最后一页")
            return False
        
        self.pdf_reader.current_page += 1
        logger.debug(f"下一页: 当前页码 {self.pdf_reader.current_page+1}")
        # 通知观察者页面已改变
        self.notify_observers('page_changed', {
            'page_num': self.pdf_reader.current_page + 1  # 转换为从1开始的页码
        })
        return True
    
    def prev_page(self):
        """上一页
        
        Returns:
            bool: 是否成功跳转
        """
        if not self.pdf_reader.doc or self.pdf_reader.current_page <= 0:
            logger.debug("上一页失败: 已经是第一页")
            return False
        
        self.pdf_reader.current_page -= 1
        logger.debug(f"上一页: 当前页码 {self.pdf_reader.current_page+1}")
        # 通知观察者页面已改变
        self.notify_observers('page_changed', {
            'page_num': self.pdf_reader.current_page + 1  # 转换为从1开始的页码
        })
        return True
    
    def first_page(self):
        """首页
        
        Returns:
            bool: 是否成功跳转
        """
        if not self.pdf_reader.doc or self.pdf_reader.current_page == 0:
            logger.debug("首页跳转失败: 已经在第一页")
            return False
        
        self.pdf_reader.current_page = 0
        logger.debug("跳转到首页")
        # 通知观察者页面已改变
        self.notify_observers('page_changed', {
            'page_num': 1  # 转换为从1开始的页码
        })
        return True
    
    def last_page(self):
        """末页
        
        Returns:
            bool: 是否成功跳转
        """
        if not self.pdf_reader.doc or self.pdf_reader.current_page == self.pdf_reader.total_pages - 1:
            logger.debug("末页跳转失败: 已经在最后一页")
            return False
        
        self.pdf_reader.current_page = self.pdf_reader.total_pages - 1
        logger.debug("跳转到末页")
        # 通知观察者页面已改变
        self.notify_observers('page_changed', {
            'page_num': self.pdf_reader.total_pages  # 转换为从1开始的页码
        })
        return True
    
    def set_zoom_level(self, zoom_level):
        """设置缩放级别
        
        Args:
            zoom_level: 缩放级别（1.0表示100%）
            
        Returns:
            bool: 是否成功设置缩放级别
        """
        if zoom_level < 0.5 or zoom_level > 2.0:
            logger.warning(f"设置缩放级别失败: 无效的缩放级别 {zoom_level}")
            return False
        
        self.zoom_level = zoom_level
        logger.debug(f"设置缩放级别: {zoom_level*100}%")
        # 通知观察者缩放级别已改变
        self.notify_observers('zoom_changed', {
            'zoom_level': zoom_level
        })
        return True
    
    def search_text(self, query):
        """搜索文本
        
        Args:
            query: 搜索关键词
            
        Returns:
            List[Dict]: 搜索结果列表
        """
        if not self.pdf_reader.doc:
            logger.warning("搜索文本失败: 没有打开的PDF文档")
            return []
        
        logger.info(f"搜索文本: {query}")
        results = self.pdf_reader.search_text(query)
        logger.info(f"搜索结果数量: {len(results)}")
        return results