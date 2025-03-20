# models/chat_model.py
from typing import Dict, Any, List, Optional
from core.event_bus import EventBus
from services.config_service import ConfigService

class ChatModel:
    def __init__(self, config_service=None):
        self.config_service = config_service or ConfigService()
        self.event_bus = EventBus()
        self.chat_history = []
        self.current_context = ""
        self.api_key = self.config_service.api_key
        self.api_url = self.config_service.api_url
        
        # 订阅事件
        self.event_bus.subscribe('pdf_loaded', self._on_pdf_loaded)
        self.event_bus.subscribe('api_key_changed', self._on_api_key_changed)
    
    def _on_pdf_loaded(self, data: Dict[str, Any]) -> None:
        """处理PDF加载事件，更新当前上下文
        
        Args:
            data: 事件数据
        """
        if data.get('cached', False) and 'cache_content' in data:
            # 从缓存中获取内容作为上下文
            self.current_context = data['cache_content'].get('raw_content', '')
        else:
            # 使用PDF的元数据作为上下文
            metadata = data.get('metadata', {})
            self.current_context = f"标题: {metadata.get('title', '未知')}\n作者: {metadata.get('author', '未知')}\n"
        
        # 发布上下文更新事件
        self.event_bus.publish('context_updated', {
            'context': self.current_context
        })
    
    def _on_api_key_changed(self, data: Dict[str, Any]) -> None:
        """处理API密钥变更事件
        
        Args:
            data: 事件数据
        """
        self.api_key = data.get('api_key', '')
        self.api_url = data.get('api_url', '')
    
    def add_message(self, role: str, content: str) -> None:
        """添加消息到聊天历史
        
        Args:
            role: 消息角色，'user'或'assistant'
            content: 消息内容
        """
        message = {
            'role': role,
            'content': content,
            'timestamp': self._get_current_timestamp()
        }
        self.chat_history.append(message)
        
        # 发布消息添加事件
        self.event_bus.publish('message_added', message)
    
    def _get_current_timestamp(self) -> str:
        """获取当前时间戳
        
        Returns:
            str: 格式化的时间戳
        """
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def get_chat_history(self) -> List[Dict[str, Any]]:
        """获取聊天历史
        
        Returns:
            List[Dict[str, Any]]: 聊天历史列表
        """
        return self.chat_history
    
    def clear_chat_history(self) -> None:
        """清空聊天历史"""
        self.chat_history = []
        
        # 发布聊天历史清空事件
        self.event_bus.publish('chat_history_cleared', {})
    
    def set_context(self, context: str) -> None:
        """设置当前上下文
        
        Args:
            context: 上下文内容
        """
        self.current_context = context
        
        # 发布上下文更新事件
        self.event_bus.publish('context_updated', {
            'context': self.current_context
        })
    
    def get_context(self) -> str:
        """获取当前上下文
        
        Returns:
            str: 上下文内容
        """
        return self.current_context