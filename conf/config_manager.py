import json
from pathlib import Path
from typing import Dict, Any
from core.logger import logger

class ConfigManager:
    _instance = None
    _config_file = Path('config')
    _default_config = {
        'api_key': '',
        'api_url': '',  # 添加API URL配置项
        'last_library_path': '',
        'last_folder_path': '',  # 上次打开的文件夹路径
        'window': {
            'width': 1200,
            'height': 800,
            'x': 100,
            'y': 100
        },
        'splitter_sizes': [200, 400, 400, 200],  # 左侧文件树、文本阅读区、图片查看区、右侧聊天区的宽度比例
        'image_viewer_splitter_sizes': [700, 300],  # 图片查看器中上部图片区域和下部缩略图区域的高度比例
        'zoom_level': 1.0,  # PDF查看器的缩放级别
        'categories': {},  # 文献分类数据
        'llm_configs': {  # LLM配置，包含三套配置
            'format': {  # 文本整理配置
                'api_key': '',
                'api_url': ''
            },
            'translate': {  # 翻译配置
                'api_key': '',
                'api_url': ''
            },
            'chat': {  # AI对话配置
                'api_key': '',
                'api_url': ''
            }
        },
        'theme': {
            'mode': 'auto',  # 'auto', 'light', 'dark'
            'last_auto_mode': 'light',  # 记录自动模式下最后的主题状态
            'font_family': 'Microsoft YaHei',  # 字体系列
            'font_weight': 'normal',  # 字重：normal, bold
            'letter_spacing': 'normal'  # 字间距：normal, wide, narrow
        }
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """从配置文件加载配置，如果文件不存在则创建默认配置"""
        try:
            if self._config_file.exists():
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.info("成功加载配置文件")
                    return config
            logger.info("配置文件不存在，使用默认配置")
            return self._default_config.copy()
        except Exception as e:
            logger.error(f'加载配置文件失败: {e}')
            return self._default_config.copy()
    
    def save_config(self) -> None:
        """保存配置到文件"""
        try:
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
            logger.info("成功保存配置文件")
        except Exception as e:
            logger.error(f'保存配置文件失败: {e}')
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项的值"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置配置项的值并保存"""
        self._config[key] = value
        self.save_config()
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """批量更新配置项"""
        self._config.update(config_dict)
        self.save_config()
    
    @property
    def api_key(self) -> str:
        return self.get('api_key', '')
    
    @api_key.setter
    def api_key(self, value: str) -> None:
        self.set('api_key', value)
    
    @property
    def api_url(self) -> str:
        return self.get('api_url', '')
    
    @api_url.setter
    def api_url(self, value: str) -> None:
        self.set('api_url', value)
    
    @property
    def last_library_path(self) -> str:
        return self.get('last_library_path', '')
    
    @last_library_path.setter
    def last_library_path(self, value: str) -> None:
        self.set('last_library_path', value)
    
    @property
    def last_folder_path(self) -> str:
        return self.get('last_folder_path', '')
    
    @last_folder_path.setter
    def last_folder_path(self, value: str) -> None:
        self.set('last_folder_path', value)
    
    @property
    def theme_mode(self) -> str:
        return self.get('theme', {}).get('mode', 'auto')
    
    @theme_mode.setter
    def theme_mode(self, value: str) -> None:
        if value not in ['auto', 'light', 'dark']:
            raise ValueError('Invalid theme mode')
        theme = self.get('theme', {})
        theme['mode'] = value
        self.set('theme', theme)
    
    @property
    def last_auto_theme(self) -> str:
        return self.get('theme', {}).get('last_auto_mode', 'light')
    
    @last_auto_theme.setter
    def last_auto_theme(self, value: str) -> None:
        if value not in ['light', 'dark']:
            raise ValueError('Invalid theme mode')
        theme = self.get('theme', {})
        theme['last_auto_mode'] = value
        self.set('theme', theme)
    
    @property
    def font_family(self) -> str:
        return self.get('theme', {}).get('font_family', 'Microsoft YaHei')
    
    @font_family.setter
    def font_family(self, value: str) -> None:
        theme = self.get('theme', {})
        theme['font_family'] = value
        self.set('theme', theme)
    
    @property
    def font_weight(self) -> str:
        return self.get('theme', {}).get('font_weight', 'normal')
    
    @font_weight.setter
    def font_weight(self, value: str) -> None:
        if value not in ['normal', 'bold']:
            raise ValueError('Invalid font weight')
        theme = self.get('theme', {})
        theme['font_weight'] = value
        self.set('theme', theme)
    
    @property
    def letter_spacing(self) -> str:
        return self.get('theme', {}).get('letter_spacing', 'normal')
    
    @letter_spacing.setter
    def letter_spacing(self, value: str) -> None:
        if value not in ['normal', 'wide', 'narrow']:
            raise ValueError('Invalid letter spacing')
        theme = self.get('theme', {})
        theme['letter_spacing'] = value
        self.set('theme', theme)
    
    @property
    def window_geometry(self) -> Dict[str, int]:
        return self.get('window', self._default_config['window'])
    
    @window_geometry.setter
    def window_geometry(self, value: Dict[str, int]) -> None:
        self.set('window', value)
    
    @property
    def splitter_sizes(self) -> list:
        return self.get('splitter_sizes', self._default_config['splitter_sizes'])
    
    @splitter_sizes.setter
    def splitter_sizes(self, value: list) -> None:
        self.set('splitter_sizes', value)
    
    @property
    def zoom_level(self) -> float:
        return self.get('zoom_level', self._default_config['zoom_level'])
    
    @zoom_level.setter
    def zoom_level(self, value: float) -> None:
        self.set('zoom_level', value)
    
    @property
    def image_viewer_splitter_sizes(self) -> list:
        return self.get('image_viewer_splitter_sizes', self._default_config['image_viewer_splitter_sizes'])
    
    @image_viewer_splitter_sizes.setter
    def image_viewer_splitter_sizes(self, value: list) -> None:
        self.set('image_viewer_splitter_sizes', value)
        
    # LLM配置相关属性
    @property
    def llm_configs(self) -> Dict[str, Dict[str, str]]:
        """获取所有LLM配置"""
        return self.get('llm_configs', self._default_config['llm_configs'])
    
    @llm_configs.setter
    def llm_configs(self, value: Dict[str, Dict[str, str]]) -> None:
        """设置所有LLM配置"""
        self.set('llm_configs', value)
    
    # 文本整理LLM配置
    @property
    def format_llm_config(self) -> Dict[str, str]:
        """获取文本整理LLM配置"""
        return self.get('llm_configs', {}).get('format', self._default_config['llm_configs']['format'])
    
    @format_llm_config.setter
    def format_llm_config(self, value: Dict[str, str]) -> None:
        """设置文本整理LLM配置"""
        llm_configs = self.llm_configs
        llm_configs['format'] = value
        self.llm_configs = llm_configs
    
    # 翻译LLM配置
    @property
    def translate_llm_config(self) -> Dict[str, str]:
        """获取翻译LLM配置"""
        return self.get('llm_configs', {}).get('translate', self._default_config['llm_configs']['translate'])
    
    @translate_llm_config.setter
    def translate_llm_config(self, value: Dict[str, str]) -> None:
        """设置翻译LLM配置"""
        llm_configs = self.llm_configs
        llm_configs['translate'] = value
        self.llm_configs = llm_configs
    
    # AI对话LLM配置
    @property
    def chat_llm_config(self) -> Dict[str, str]:
        """获取AI对话LLM配置"""
        return self.get('llm_configs', {}).get('chat', self._default_config['llm_configs']['chat'])
    
    @chat_llm_config.setter
    def chat_llm_config(self, value: Dict[str, str]) -> None:
        """设置AI对话LLM配置"""
        llm_configs = self.llm_configs
        llm_configs['chat'] = value
        self.llm_configs = llm_configs