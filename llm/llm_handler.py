from openai import OpenAI
import json
from typing import List, Dict, Any, Optional, Union
from core.logger import logger

class LLMClient:
    """LLM客户端，用于标准化与LLM模型的交互"""
    
    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None, client_type: str = 'general'):
        """初始化LLM客户端
        
        Args:
            api_url: API的完整URL，如果为None则使用OpenAI默认URL
            api_key: API密钥，如果为None则使用环境变量中的密钥
            client_type: 客户端类型，可选值为'general'、'format'、'translate'、'chat'
        """
        self.api_url = api_url
        self.api_key = api_key
        self.client_type = client_type
        
        # 初始化OpenAI客户端
        self.client = OpenAI(
            api_key=api_key,
            base_url=api_url
        ) if api_key or api_url else OpenAI()
    
    def set_api_url(self, api_url: str) -> None:
        """设置API URL
        
        Args:
            api_url: API的完整URL
        """
        self.api_url = api_url
        self.client = OpenAI(api_key=self.api_key, base_url=api_url)
        logger.info(f"已设置API URL: {api_url}")
    
    def set_api_key(self, api_key: str) -> None:
        """设置API密钥
        
        Args:
            api_key: API密钥
        """
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key, base_url=self.api_url)
        logger.info("已设置API密钥")
    
    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "gpt-3.5-turbo", 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """发送聊天请求到LLM模型
        
        Args:
            messages: 消息列表，每个消息是一个字典，包含role和content字段
            model: 模型名称
            temperature: 温度参数，控制输出的随机性
            max_tokens: 最大生成的token数量
            system_prompt: 系统提示，如果提供，将添加到消息列表的开头
            
        Returns:
            LLM模型的响应
            
        Raises:
            Exception: 当API调用失败时抛出异常
        """
        try:
            # 如果提供了系统提示，则添加到消息列表的开头
            if system_prompt:
                messages.insert(0, {"role": "system", "content": system_prompt})
            
            # 构建请求参数
            params = {
                "model": model,
                "messages": messages,
                "temperature": temperature
            }
            
            # 如果提供了最大token数量，则添加到请求参数中
            if max_tokens is not None:
                params["max_tokens"] = max_tokens
            
            # 发送请求
            logger.info(f"发送请求到LLM模型: {model}")
            response = self.client.chat.completions.create(**params)
            
            # 将响应对象转换为字典
            response_dict = {
                'choices': [
                    {
                        'message': {
                            'content': response.choices[0].message.content,
                            'role': response.choices[0].message.role
                        },
                        'index': response.choices[0].index,
                        'finish_reason': response.choices[0].finish_reason
                    }
                ],
                'created': response.created,
                'model': response.model,
                'id': response.id
            }
            
            logger.info("成功接收到LLM模型响应")
            return response_dict
        
        except Exception as e:
            logger.error(f"OpenAI API错误: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"调用LLM模型时发生未知错误: {str(e)}")
            raise
    
    def get_completion_text(self, response: Dict[str, Any]) -> str:
        """从LLM模型响应中提取文本
        
        Args:
            response: LLM模型的响应
            
        Returns:
            提取的文本
        """
        try:
            return response.choices[0].message['content']
        except (KeyError, IndexError, AttributeError) as e:
            logger.error(f"从LLM响应中提取文本时发生错误: {str(e)}")
            return ""