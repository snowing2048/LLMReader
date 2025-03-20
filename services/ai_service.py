# services/ai_service.py
import requests
import json
from typing import Dict, Any, List, Optional
from core.logger import logger
from services.config_service import ConfigService
from core.event_bus import EventBus

class AIService:
    def __init__(self, config_service=None):
        self.config_service = config_service or ConfigService()
        self.event_bus = EventBus()
        self.api_key = self.config_service.api_key
        self.api_url = self.config_service.api_url
        logger.info("AI服务初始化完成")
        
        # 订阅API密钥变更事件
        self.event_bus.subscribe('api_key_changed', self._on_api_key_changed)
    
    def _on_api_key_changed(self, data: Dict[str, Any]) -> None:
        """处理API密钥变更事件
        
        Args:
            data: 事件数据
        """
        self.api_key = data.get('api_key', '')
        self.api_url = data.get('api_url', '')
    
    def send_message(self, messages: List[Dict[str, str]], context: str = "") -> Optional[str]:
        """发送消息到AI API
        
        Args:
            messages: 消息列表，每个消息包含role和content
            context: 上下文内容
            
        Returns:
            str: AI的回复，如果请求失败则返回None
        """
        if not self.api_key:
            logger.error("API密钥未设置")
            self.event_bus.publish('ai_error', {'error': 'API密钥未设置'})
            return None
        
        try:
            # 构建请求数据
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": messages
            }
            
            # 如果有上下文，添加到系统消息中
            if context:
                system_message = {
                    "role": "system",
                    "content": f"以下是文档内容，请基于这些内容回答用户的问题：\n\n{context}"
                }
                payload["messages"].insert(0, system_message)
            
            # 发送请求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 使用配置的API URL或默认URL
            url = self.api_url or "https://api.openai.com/v1/chat/completions"
            
            logger.info(f"发送请求到AI API: {url}")
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                message = result['choices'][0]['message']
                content = message.get('content', '')
                
                # 发布AI回复事件
                self.event_bus.publish('ai_response', {'content': content})
                
                return content
            else:
                logger.error(f"AI API响应格式错误: {result}")
                self.event_bus.publish('ai_error', {'error': 'AI API响应格式错误'})
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"AI API请求异常: {str(e)}")
            self.event_bus.publish('ai_error', {'error': f'AI API请求异常: {str(e)}'})
            return None
        except Exception as e:
            logger.error(f"发送消息到AI API失败: {str(e)}")
            self.event_bus.publish('ai_error', {'error': f'发送消息到AI API失败: {str(e)}'})
            return None