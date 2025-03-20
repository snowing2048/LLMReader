# controllers/chat_controller.py
from typing import Dict, Any, List
from core.logger import logger
from core.event_bus import EventBus
from models.chat_model import ChatModel
from models.config_model import ConfigModel
from services.ai_service import AIService

class ChatController:
    def __init__(self, chat_model=None, config_model=None, ai_service=None):
        self.chat_model = chat_model or ChatModel()
        self.config_model = config_model or ConfigModel()
        self.ai_service = ai_service or AIService()
        self.event_bus = EventBus()
        self.current_context = ""
        logger.info("聊天控制器初始化完成")
        
        # 订阅事件
        self.event_bus.subscribe('file_opened', self._on_file_opened)
        self.event_bus.subscribe('page_changed', self._on_page_changed)
    
    def _on_file_opened(self, data: Dict[str, Any]) -> None:
        """处理文件打开事件
        
        Args:
            data: 事件数据
        """
        # 清空当前上下文
        self.current_context = ""
    
    def _on_page_changed(self, data: Dict[str, Any]) -> None:
        """处理页面变化事件
        
        Args:
            data: 事件数据
        """
        # 更新当前上下文
        page_num = data.get('page_num', 0)
        # 这里可以从PDF模型获取当前页面的文本内容作为上下文
        # 暂时留空，等待实现
    
    def send_message(self, text: str) -> None:
        """发送用户消息
        
        Args:
            text: 用户消息文本
        """
        # 添加用户消息到聊天模型
        self.chat_model.add_message(text, True)
        
        # 构建消息列表
        messages = []
        for msg in self.chat_model.messages[-5:]:  # 只取最近的5条消息
            role = "user" if msg.is_user else "assistant"
            messages.append({"role": role, "content": msg.text})
        
        # 调用AI服务获取回复
        response = self.ai_service.send_message(messages, self.current_context)
        
        if response:
            # 添加AI回复到聊天模型
            self.chat_model.add_message(response, False)
        else:
            # 添加错误消息
            self.chat_model.add_message("抱歉，无法获取回复。请检查API设置或网络连接。", False)
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """获取所有消息
        
        Returns:
            List[Dict[str, Any]]: 消息列表
        """
        return [{
            "text": msg.text,
            "is_user": msg.is_user
        } for msg in self.chat_model.messages]
    
    def clear_messages(self) -> None:
        """清空所有消息"""
        self.chat_model.messages = []
        # 发布消息清空事件
        self.event_bus.publish('messages_cleared', {})
    
    def set_api_key(self, api_key: str) -> None:
        """设置API密钥
        
        Args:
            api_key: API密钥
        """
        self.config_model.api_key = api_key
        # 发布API密钥变更事件
        self.event_bus.publish('api_key_changed', {
            'api_key': api_key,
            'api_url': self.config_model.api_url
        })
    
    def set_api_url(self, api_url: str) -> None:
        """设置API URL
        
        Args:
            api_url: API URL
        """
        self.config_model.api_url = api_url
        # 发布API密钥变更事件
        self.event_bus.publish('api_key_changed', {
            'api_key': self.config_model.api_key,
            'api_url': api_url
        })